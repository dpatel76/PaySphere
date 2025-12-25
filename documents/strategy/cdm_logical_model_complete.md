# PAYMENTS COMMON DOMAIN MODEL (CDM)
## COMPLETE LOGICAL DATA MODEL

**Document Version:** 1.0
**Date:** December 18, 2025
**Classification:** Technical Specification - Complete Model

---

## TABLE OF CONTENTS

1. [Entity Relationship Diagram](#entity-relationship-diagram)
2. [Core Domain Entities](#core-domain-entities)
3. [Supporting Domain Entities](#supporting-domain-entities)
4. [Reference Data Entities](#reference-data-entities)
5. [Compliance and Regulatory Entities](#compliance-and-regulatory-entities)
6. [Operational Entities](#operational-entities)
7. [Analytics Entities](#analytics-entities)
8. [Relationships and Cardinality](#relationships-and-cardinality)
9. [Entity Attribute Complete Specification](#entity-attribute-complete-specification)

---

## ENTITY RELATIONSHIP DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CORE DOMAIN ENTITIES                          │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │  PaymentInstruction  │◄──────┐
                    │  (Root Aggregate)    │       │
                    └──────────┬───────────┘       │
                               │                   │
                 ┌─────────────┼─────────────┐     │
                 │             │             │     │
         ┌───────▼──────┐ ┌───▼──────┐ ┌────▼─────▼──┐
         │    Party     │ │ Account  │ │   Status    │
         │  (Debtor/    │ │          │ │   Event     │
         │  Creditor)   │ │          │ │             │
         └──────┬───────┘ └────┬─────┘ └─────────────┘
                │              │
         ┌──────▼──────────────▼─────┐
         │  FinancialInstitution     │
         │  (Agent Banks)            │
         └───────────────────────────┘

                    ┌──────────────────────┐
                    │    Settlement        │
                    │                      │
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │    Charge            │
                    │                      │
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │  RegulatoryInfo      │
                    │                      │
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │  RemittanceInfo      │
                    │                      │
                    └──────────────────────┘

                    ┌──────────────────────┐
                    │  PaymentRelationship │
                    │  (Returns, Covers)   │
                    └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    REFERENCE DATA ENTITIES                           │
└─────────────────────────────────────────────────────────────────────┘

├── Currency
├── Country
├── ClearingSystem
├── PurposeCode
├── StatusReasonCode
├── ChargeType
├── SchemeCode
├── PaymentType
└── RegulatoryReportType

┌─────────────────────────────────────────────────────────────────────┐
│                 COMPLIANCE & REGULATORY ENTITIES                     │
└─────────────────────────────────────────────────────────────────────┘

├── ScreeningResult
├── ComplianceCase
├── RegulatoryReport
├── SanctionsList
└── AMLAlert

┌─────────────────────────────────────────────────────────────────────┐
│                      OPERATIONAL ENTITIES                            │
└─────────────────────────────────────────────────────────────────────┘

├── PaymentException
├── ManualIntervention
├── AuditTrail
├── DataQualityIssue
└── ReconciliationRecord

┌─────────────────────────────────────────────────────────────────────┐
│                       ANALYTICS ENTITIES                             │
└─────────────────────────────────────────────────────────────────────┘

├── PaymentMetrics (aggregations)
├── CustomerPaymentBehavior (features)
├── PaymentFlowAnalysis
└── FraudPattern
```

---

## CORE DOMAIN ENTITIES

### Entity 1: PaymentInstruction

**Purpose**: Root aggregate representing a complete payment instruction from initiation through settlement

**Attributes**: (All attributes with complete specification)

| Attribute Name | Data Type | Constraints | Description | Derived From | Mandatory | Default Value |
|----------------|-----------|-------------|-------------|--------------|-----------|---------------|
| paymentId | UUID | Primary Key, Unique, Not Null | Unique identifier for payment (generated) | System generated | Yes | UUID v4 |
| endToEndId | VARCHAR(35) | Unique per payment type + date | End-to-end identification per ISO 20022 | ISO 20022, MT :20:, NACHA Trace | No | NULL |
| uetr | UUID | Format: UUID, SWIFT gpi only | Unique End-to-end Transaction Reference (SWIFT gpi) | SWIFT MX, MT (if gpi) | No (Yes for SWIFT gpi) | NULL |
| instructionId | VARCHAR(35) | | Instruction identification | ISO 20022, MT :20:, Fedwire IMAD | No | NULL |
| transactionId | VARCHAR(35) | | Transaction identification | ISO 20022, source system | No | NULL |
| paymentType | ENUM | See PaymentType reference | Payment type classification | Derived from scheme and product | Yes | NULL |
| productCode | VARCHAR(50) | | BofA internal product code | CashPro product catalog | No | NULL |
| schemeCode | ENUM | See SchemeCode reference | Payment scheme identifier | Source system, message type | Yes | NULL |
| serviceLevel | VARCHAR(4) | ISO 20022 service level codes | Service level (URGP, SEPA, SDVA, etc.) | ISO 20022 SvcLvl | No | NULL |
| localInstrument | VARCHAR(35) | | Local instrument code | ISO 20022, scheme-specific | No | NULL |
| categoryPurpose | VARCHAR(4) | ISO 20022 category purpose | Category purpose code | ISO 20022 CtgyPurp | No | NULL |
| instructedAmount | STRUCT {amount: DECIMAL(18,2), currency: CHAR(3)} | amount > 0, currency ISO 4217 | Instructed amount and currency | All sources | Yes | NULL |
| interbankSettlementAmount | STRUCT {amount: DECIMAL(18,2), currency: CHAR(3)} | | Interbank settlement amount (if different) | ISO 20022, MT :32A: | No | Same as instructedAmount |
| equivalentAmount | STRUCT {amount: DECIMAL(18,2), currency: CHAR(3)} | | Equivalent amount in different currency | ISO 20022 | No | NULL |
| exchangeRate | DECIMAL(15,10) | > 0 | Exchange rate if currency conversion | ISO 20022, FX systems | No | NULL |
| chargeBearer | ENUM('DEBT','CRED','SHAR','SLEV') | ISO 20022 charge bearer | Who bears charges | ISO 20022, MT :71A: | No | 'SHAR' |
| creationDateTime | TIMESTAMP | Not Null | When payment instruction was created | System timestamp | Yes | CURRENT_TIMESTAMP |
| acceptanceDateTime | TIMESTAMP | | When payment was accepted by bank | Processing system | No | NULL |
| requestedExecutionDate | DATE | >= creation date | Requested execution date | Customer instruction | Yes | CURRENT_DATE |
| requestedExecutionTime | TIME | | Requested execution time (for time-critical payments) | Customer instruction | No | NULL |
| valueDate | DATE | | Value date for funds | ISO 20022, MT :32A: | No | NULL |
| settlementDate | DATE | | Actual settlement date | Settlement system | No | NULL |
| interbankSettlementDate | DATE | | Interbank settlement date | ISO 20022 | No | NULL |
| debtorId | UUID | Foreign Key to Party | Reference to debtor party entity | Derived | Yes | NULL |
| debtorAccountId | UUID | Foreign Key to Account | Reference to debtor account entity | Derived | No | NULL |
| debtorAgentId | UUID | Foreign Key to FinancialInstitution | Reference to debtor agent FI | Derived | No | NULL |
| creditorId | UUID | Foreign Key to Party | Reference to creditor party entity | Derived | Yes | NULL |
| creditorAccountId | UUID | Foreign Key to Account | Reference to creditor account entity | Derived | No | NULL |
| creditorAgentId | UUID | Foreign Key to FinancialInstitution | Reference to creditor agent FI | Derived | No | NULL |
| intermediaryAgent1Id | UUID | Foreign Key to FinancialInstitution | First intermediary agent | Derived | No | NULL |
| intermediaryAgent2Id | UUID | Foreign Key to FinancialInstitution | Second intermediary agent | Derived | No | NULL |
| intermediaryAgent3Id | UUID | Foreign Key to FinancialInstitution | Third intermediary agent | Derived | No | NULL |
| purpose | VARCHAR(4) | ISO 20022 external purpose code | Purpose code | ISO 20022 Purp/Cd | No | NULL |
| purposeDescription | VARCHAR(500) | | Purpose description (free text) | Customer provided | No | NULL |
| priority | ENUM('HIGH','NORM','URGP') | | Payment priority | ISO 20022, scheme rules | No | 'NORM' |
| instructionPriority | VARCHAR(4) | | Instruction priority code | ISO 20022 | No | NULL |
| currentStatus | ENUM | See PaymentStatus reference | Current payment status | Processing system | Yes | 'initiated' |
| statusReason | VARCHAR(4) | ISO 20022 status reason codes | Status reason code | ISO 20022, scheme | No | NULL |
| statusReasonDescription | VARCHAR(500) | | Status reason narrative | Processing system | No | NULL |
| statusTimestamp | TIMESTAMP | Not Null | Timestamp of last status change | System | Yes | CURRENT_TIMESTAMP |
| previousStatus | ENUM | See PaymentStatus reference | Previous status (for audit trail) | Derived from status history | No | NULL |
| numberOfStatusChanges | INTEGER | >= 0 | Count of status changes | Calculated | No | 0 |
| regulatoryReporting | ARRAY<STRUCT> | See RegulatoryReporting structure | Regulatory reporting codes and details | Various regulations | No | [] |
| crossBorderFlag | BOOLEAN | Not Null | Cross-border payment indicator | Calculated from debtor/creditor countries | Yes | FALSE |
| crossBorderType | ENUM('domestic','intra_eu','cross_border') | | Type of cross-border transaction | Calculated | No | NULL |
| sanctionsScreeningStatus | ENUM('not_screened','clear','hit','pending','false_positive','blocked') | | Sanctions screening status | Screening system | No | 'not_screened' |
| sanctionsScreeningTimestamp | TIMESTAMP | | When sanctions screening completed | Screening system | No | NULL |
| fraudScore | DECIMAL(5,2) | 0-100 | Fraud risk score | Fraud detection system | No | NULL |
| fraudScoreVersion | VARCHAR(20) | | Version of fraud scoring model | Fraud system | No | NULL |
| fraudFlags | ARRAY<VARCHAR> | | List of fraud flags/alerts | Fraud system | No | [] |
| amlRiskRating | ENUM('low','medium','high','very_high') | | AML risk rating | AML system | No | NULL |
| amlAlertId | UUID | Foreign Key to AMLAlert | Reference to AML alert if raised | AML system | No | NULL |
| peakyFlag | BOOLEAN | | Payment subject to enhanced due diligence | Compliance | No | FALSE |
| structuringIndicator | BOOLEAN | | Potential structuring to avoid reporting | AML system | No | FALSE |
| sourceSystem | VARCHAR(100) | Not Null | Source system identifier | System | Yes | NULL |
| sourceSystemRecordId | VARCHAR(100) | | Record ID in source system | Source system | No | NULL |
| sourceMessageType | VARCHAR(50) | | Source message type (MT103, pain.001, etc.) | Source | No | NULL |
| sourceMessageContent | TEXT | | Original source message (for audit) | Source | No | NULL |
| ingestionTimestamp | TIMESTAMP | Not Null | When record ingested into Bronze layer | ETL system | Yes | CURRENT_TIMESTAMP |
| bronzeToSilverTimestamp | TIMESTAMP | | When transformed from Bronze to Silver | ETL system | No | NULL |
| dataQualityScore | DECIMAL(5,2) | 0-100 | Overall data quality score | DQ framework | No | NULL |
| dataQualityDimensions | STRUCT | Completeness, Validity, Consistency, Accuracy, Timeliness scores | Individual DQ dimension scores | DQ framework | No | NULL |
| dataQualityIssues | ARRAY<VARCHAR> | | List of data quality issues | DQ framework | No | [] |
| lineageSourceTable | VARCHAR(200) | | Source table name for lineage | Lineage tracking | No | NULL |
| lineageSourceColumns | ARRAY<VARCHAR> | | Source columns for lineage | Lineage tracking | No | [] |
| partitionYear | INTEGER | Not Null, Partition column | Year for partitioning | Derived from paymentDate | Yes | YEAR(requestedExecutionDate) |
| partitionMonth | INTEGER | Not Null, Partition column | Month for partitioning | Derived from paymentDate | Yes | MONTH(requestedExecutionDate) |
| region | VARCHAR(10) | Not Null, Partition column | Geographic region (US, EMEA, APAC) | Derived from debtor/creditor | Yes | NULL |
| productType | VARCHAR(50) | Not Null, Partition column | Product type for partitioning | Derived from paymentType | Yes | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp in Silver | System | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | System | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that last updated | System | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version for optimistic locking | System | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | System | No | FALSE |
| deletedTimestamp | TIMESTAMP | | When record was soft deleted | System | No | NULL |
| extensions | JSON | | Product-specific extension fields | Various | No | {} |

**Product-Specific Extension Fields** (stored in `extensions` JSON):

ACH Extensions:
- `achSECCode`: Standard Entry Class Code (PPD, CCD, WEB, etc.)
- `achCompanyName`: Company name (16 chars)
- `achCompanyID`: Company identification (10 chars)
- `achCompanyEntryDescription`: Entry description (10 chars)
- `achCompanyDiscretionaryData`: Discretionary data (20 chars)
- `achOriginatingDFI`: Originating DFI identification (8 digits)
- `achReceivingDFI`: Receiving DFI identification (8 digits)
- `achTraceNumber`: Trace number (15 digits)
- `achTransactionCode`: Transaction code (2 digits)
- `achAddendaRecordIndicator`: Addenda indicator (0 or 1)
- `achAddendaType`: Addenda type code (05, 02, etc.)
- `achEffectiveEntryDate`: Effective entry date (YYMMDD)
- `achBatchNumber`: Batch number
- `achReturnReasonCode`: Return reason code (if returned)
- `achNotificationOfChangeCode`: NOC code (if NOC)
- `achSameDayFlag`: Same-day ACH indicator

Wire Extensions:
- `fedwireMessageType`: Message type (1000, 1500, etc.)
- `fedwireIMAD`: Input Message Accountability Data
- `fedwireOMAD`: Output Message Accountability Data
- `fedwireBusinessFunctionCode`: Business function code
- `fedwireSenderReference`: Sender reference
- `fedwireReceiverMemo`: Receiver memo
- `fedwireBeneficiaryReference`: Beneficiary reference
- `fedwireOriginatorToBeneficiaryInfo`: Originator to beneficiary info (4x35 chars)
- `chipsUID`: CHIPS unique identifier
- `chipsSequenceNumber`: CHIPS sequence number

SWIFT Extensions:
- `swiftMessageType`: MT type (103, 202, etc.) or MX message
- `swiftSenderBIC`: Sender BIC
- `swiftReceiverBIC`: Receiver BIC
- `swiftTransactionReference`: :20: field
- `swiftRelatedReference`: :21: field
- `swiftBankOperationCode`: :23B: field
- `swiftInstructionCode`: :23E: field
- `swiftSenderToReceiverInfo`: :72: field
- `swiftRegulatoryReporting`: :77B: field
- `swiftEnvelopeContents`: :77T: field
- `swiftGPIFlag`: gpi service indicator
- `swiftGPIUETR`: UETR for gpi
- `swiftGPIServiceType`: gpi service type
- `swiftCOVFlag`: Cover payment indicator

SEPA Extensions:
- `sepaScheme`: SCT, SCT_INST, SDD_CORE, SDD_B2B
- `sepaCreditorIdentifier`: Creditor identifier (for SDD)
- `sepaMandateReference`: Mandate reference (for SDD)
- `sepaMandateSignatureDate`: Mandate signature date
- `sepaSequenceType`: FRST, RCUR, FNAL, OOFF (for SDD)
- `sepaAmendmentIndicator`: Amendment indicator
- `sepaOriginalMandateReference`: Original mandate ref (if amended)
- `sepaOriginalCreditorIdentifier`: Original creditor ID (if amended)
- `sepaDirectDebitTransactionId`: Transaction ID

BACS Extensions:
- `bacsUserNumber`: User number
- `bacsProcessingDay`: Processing day (day offset)
- `bacsTransactionCode`: Transaction code
- `bacsOriginatingSortCode`: Originating sort code
- `bacsDestinationSortCode`: Destination sort code
- `bacsReference`: Payment reference (18 chars)
- `bacsStandard`: Standard 18, AUDDIS, ADDACS

CashPro Extensions:
- `cashProWorkflowState`: Workflow state
- `cashProApprovalChain`: Approval chain
- `cashProTemplateID`: Template ID
- `cashProBatchID`: Batch ID
- `cashProUserID`: Initiating user ID

**Regulatory Reporting Extensions** (AUSTRAC/FinCEN/PSD2):

AUSTRAC IFTI Extensions:
- `directionIndicator`: 'S' (Sent) or 'R' (Received) - IFTI Field 6.1
- `transferType`: 'SWIFT', 'RTGS', 'ACH', 'OTHER' - IFTI Field 6.2
- `countryOfOrigin`: ISO 3166-1 alpha-2 country code - IFTI Field 6.3
- `countryOfDestination`: ISO 3166-1 alpha-2 country code - IFTI Field 6.4
- `suspiciousActivityIndicator`: Boolean - IFTI Field 6.5

FinCEN CTR Extensions:
- `cashInTotal`: Total cash received in transaction (DECIMAL)
- `cashOutTotal`: Total cash disbursed in transaction (DECIMAL)
- `cashInInstruments`: Array of {instrument: STRING, amount: DECIMAL} - CTR Items 24-30
- `cashOutInstruments`: Array of {instrument: STRING, amount: DECIMAL} - CTR Items 31-37
- `aggregationIndicator`: Boolean - part of aggregated reporting
- `aggregationPeriodStart`: DATE - start of aggregation period
- `aggregationPeriodEnd`: DATE - end of aggregation period
- `foreignCashInDetail`: Array of {country: CHAR(2), currency: CHAR(3), amount: DECIMAL} - CTR Items 62-66
- `foreignCashOutDetail`: Array of {country: CHAR(2), currency: CHAR(3), amount: DECIMAL} - CTR Items 68-72

FinCEN SAR Extensions:
- `suspiciousActivityStartDate`: DATE - SAR Item 47
- `suspiciousActivityEndDate`: DATE - SAR Item 48
- `suspiciousActivityAmount`: DECIMAL - SAR Item 49
- `suspiciousActivityTypes`: Array of activity type codes - SAR Items 52-68 (STRUCTURING, TERRORIST_FINANCING, FRAUD, IDENTITY_THEFT, CHECK_FRAUD, COUNTERFEIT_CHECK, WIRE_TRANSFER_FRAUD, ACH_FRAUD, CREDIT_CARD_FRAUD, MONEY_LAUNDERING, BRIBERY, EMBEZZLEMENT, MISUSE_OF_POSITION, CYBER_EVENT, UNAUTHORIZED_WIRE_TRANSFER, OTHER)
- `ipAddress`: STRING - SAR cyber event fields
- `urlDomain`: STRING - SAR cyber event fields
- `deviceIdentifier`: STRING - SAR cyber event fields
- `cyberEventIndicator`: Boolean - SAR cyber event flag

PSD2 Strong Customer Authentication (SCA) Extensions:
- `cardPresentIndicator`: Boolean - card-present transaction
- `cardholderPresentIndicator`: Boolean - cardholder present
- `scaMethod`: 'SMS_OTP', 'MOBILE_APP', 'HARDWARE_TOKEN', 'BIOMETRIC', 'KNOWLEDGE_BASED', 'NONE'
- `scaExemption`: 'LOW_VALUE', 'TRA', 'RECURRING', 'TRUSTED_BENEFICIARY', 'CORPORATE', 'MIT', NULL
- `scaStatus`: 'SUCCESSFUL', 'FAILED', 'EXEMPTED', 'NOT_REQUIRED'
- `threeDSecureVersion`: STRING - 3DS version (e.g., '2.2.0')
- `eciValue`: STRING - Electronic Commerce Indicator
- `cardScheme`: 'VISA', 'MASTERCARD', 'AMEX', 'DISCOVER', 'OTHER'

PSD2 Fraud Reporting Extensions:
- `fraudType`: 'LOST_STOLEN', 'COUNTERFEIT', 'CNP_FRAUD', 'ID_THEFT', 'APPLICATION_FRAUD', 'ACCOUNT_TAKEOVER', NULL
- `fraudDetectionDate`: DATE - when fraud was detected
- `fraudReportedDate`: DATE - when fraud was reported
- `fraudAmountRecovered`: DECIMAL - amount recovered from fraud
- `chargebackIndicator`: Boolean - chargeback filed
- `chargebackDate`: DATE - chargeback date
- `chargebackAmount`: DECIMAL - chargeback amount

Cross-Product Regulatory Extensions:
- `transactionLocationCountry`: CHAR(2) - ISO 3166-1 country code
- `transactionLocationCity`: VARCHAR(35) - city name
- `merchantCategoryCode`: VARCHAR(4) - MCC code (for card payments)
- `merchantName`: VARCHAR(140) - merchant name
- `terminalId`: VARCHAR(50) - terminal identifier (for card/ATM)
- `atmId`: VARCHAR(50) - ATM identifier
- `fundsAvailabilityDate`: DATE - when funds available to beneficiary
- `holdPlacedIndicator`: Boolean - hold placed on funds
- `holdReason`: VARCHAR(200) - reason for hold

**JSON Schema Validation**: All regulatory extensions follow JSON Schema Draft 2020-12 format with appropriate validation rules (enums, patterns, ranges, required fields). See `cdm_physical_model_complete.md` for complete schema specifications.

---

### Entity 2: Party

**Purpose**: Represents a party involved in a payment (debtor, creditor, or ultimate party)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| partyId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| partyType | ENUM('individual','organization','government','financial_institution') | Not Null | Party type classification | Yes | NULL |
| name | VARCHAR(140) | Not Null | Party name (standardized) | Yes | NULL |
| nameLine2 | VARCHAR(140) | | Additional name line | No | NULL |
| legalName | VARCHAR(140) | | Official legal name | No | NULL |
| shortName | VARCHAR(35) | | Short name (for space-constrained formats) | No | NULL |
| nameStandardizationScore | DECIMAL(5,2) | 0-100 | Name standardization confidence score | No | NULL |
| organizationType | ENUM('corporation','partnership','trust','sole_proprietorship','nonprofit','government_entity') | | Type of organization (if party is organization) | No | NULL |
| industryClassification | VARCHAR(10) | NAICS or SIC code | Industry classification code | No | NULL |
| dateOfBirth | DATE | | Date of birth (for individuals) | No | NULL |
| placeOfBirth | VARCHAR(100) | | Place of birth (for individuals) | No | NULL |
| countryOfBirth | CHAR(2) | ISO 3166-1 alpha-2 | Country of birth | No | NULL |
| nationality | CHAR(2) | ISO 3166-1 alpha-2 | Nationality (for individuals) | No | NULL |
| countryOfIncorporation | CHAR(2) | ISO 3166-1 alpha-2 | Country of incorporation (for organizations) | No | NULL |
| dateOfIncorporation | DATE | | Date of incorporation | No | NULL |
| registrationNumber | VARCHAR(50) | | Business registration number | No | NULL |
| identifications | ARRAY<STRUCT{scheme:VARCHAR, identification:VARCHAR, issuingCountry:CHAR(2), issuer:VARCHAR, validFrom:DATE, validTo:DATE}> | | Party identification schemes | No | [] |
| taxIdentificationNumber | VARCHAR(50) | | Primary tax ID (SSN, EIN, VAT, etc.) | No | NULL |
| taxResidenceCountry | CHAR(2) | ISO 3166-1 alpha-2 | Tax residence country | No | NULL |
| postalAddress | STRUCT | See Address structure below | Primary postal address | No | NULL |
| residentialAddress | STRUCT | | Residential address (if different from postal) | No | NULL |
| registeredAddress | STRUCT | | Registered address (for organizations) | No | NULL |
| addressStandardizationScore | DECIMAL(5,2) | 0-100 | Address standardization confidence | No | NULL |
| phoneNumber | VARCHAR(25) | E.164 format preferred | Primary phone number | No | NULL |
| mobileNumber | VARCHAR(25) | | Mobile phone number | No | NULL |
| faxNumber | VARCHAR(25) | | Fax number | No | NULL |
| emailAddress | VARCHAR(255) | Email format | Primary email address | No | NULL |
| websiteURL | VARCHAR(255) | URL format | Website | No | NULL |
| isPEP | BOOLEAN | Not Null | Politically Exposed Person flag | No | FALSE |
| pepType | ENUM('domestic_pep','foreign_pep','international_organization','rca') | | PEP type (if isPEP=true) | No | NULL |
| pepSince | DATE | | Date identified as PEP | No | NULL |
| pepPosition | VARCHAR(200) | | PEP position/role | No | NULL |
| isSanctioned | BOOLEAN | Not Null | Sanctioned party flag | No | FALSE |
| sanctionedBy | ARRAY<VARCHAR> | | Sanctioning authorities (OFAC, EU, UN, etc.) | No | [] |
| sanctionListNames | ARRAY<VARCHAR> | | Specific sanction list names | No | [] |
| sanctionedSince | DATE | | Date added to sanctions list | No | NULL |
| highRiskJurisdiction | BOOLEAN | Not Null | Party from high-risk jurisdiction | No | FALSE |
| highRiskJurisdictionList | ARRAY<CHAR(2)> | | List of high-risk countries associated | No | [] |
| adverseMediaFlag | BOOLEAN | Not Null | Adverse media flag | No | FALSE |
| adverseMediaSummary | TEXT | | Summary of adverse media findings | No | NULL |
| adverseMediaLastChecked | DATE | | Last adverse media check date | No | NULL |
| customerSince | DATE | | Customer relationship start date (if BofA customer) | No | NULL |
| customerSegment | ENUM('retail','commercial','corporate','institutional','government') | | Customer segment classification | No | NULL |
| relationshipManager | VARCHAR(100) | | Assigned relationship manager | No | NULL |
| riskRating | ENUM('low','medium','high','very_high') | | Overall risk rating | No | NULL |
| riskRatingDate | DATE | | Date of risk rating assignment | No | NULL |
| riskRatingRationale | TEXT | | Rationale for risk rating | No | NULL |
| kycStatus | ENUM('pending','in_progress','approved','expired','rejected') | | KYC status | No | NULL |
| kycCompletionDate | DATE | | Date KYC completed | No | NULL |
| kycExpiryDate | DATE | | KYC expiry date | No | NULL |
| kycNextReviewDate | DATE | | Next scheduled KYC review | No | NULL |
| kycDocuments | ARRAY<STRUCT{documentType:VARCHAR, documentID:VARCHAR, issueDate:DATE, expiryDate:DATE}> | | KYC documents collected | No | [] |
| eddRequired | BOOLEAN | Not Null | Enhanced Due Diligence required flag | No | FALSE |
| eddCompletedDate | DATE | | EDD completion date | No | NULL |
| beneficialOwners | ARRAY<STRUCT{name:VARCHAR, ownership:DECIMAL, isPEP:BOOLEAN, isController:BOOLEAN}> | | Beneficial owners (for organizations) | No | [] |
| controllingPersons | ARRAY<STRUCT{name:VARCHAR, role:VARCHAR, isPEP:BOOLEAN}> | | Controlling persons | No | [] |
| relatedParties | ARRAY<UUID> | Foreign keys to other Party records | Related parties (family, business affiliations) | No | [] |
| dataSource | VARCHAR(100) | | Primary data source | No | NULL |
| dataQualityScore | DECIMAL(5,2) | 0-100 | Party data quality score | No | NULL |
| standardizationStatus | ENUM('raw','standardized','verified','certified') | | Data standardization status | No | 'raw' |
| lastVerificationDate | DATE | | Last verification date | No | NULL |
| nextVerificationDate | DATE | | Next scheduled verification | No | NULL |
| effectiveFrom | TIMESTAMP | Not Null | Effective start date (SCD Type 2) | Yes | CURRENT_TIMESTAMP |
| effectiveTo | TIMESTAMP | | Effective end date (NULL = current) | No | NULL |
| isCurrent | BOOLEAN | Not Null | Current version flag | Yes | TRUE |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |
| givenName | VARCHAR(35) | | First/given name(s) for individuals | No | NULL |
| familyName | VARCHAR(35) | | Family/last name for individuals | No | NULL |
| suffix | VARCHAR(10) | | Name suffix (Jr., Sr., III, etc.) | No | NULL |
| dbaName | VARCHAR(140) | | Doing Business As / Trade Name | No | NULL |
| occupation | VARCHAR(100) | | Occupation or type of business | No | NULL |
| naicsCode | VARCHAR(6) | | NAICS industry classification code | No | NULL |
| formOfIdentification | VARCHAR(100) | | Type of ID document (passport, DL, etc.) | No | NULL |
| identificationNumber | VARCHAR(50) | | ID document number | No | NULL |
| identificationIssuingCountry | CHAR(2) | ISO 3166-1 | ID issuing country | No | NULL |
| identificationIssuingState | VARCHAR(3) | | ID issuing state/province | No | NULL |
| alternateNames | ARRAY<VARCHAR(140)> | | Known aliases or alternate names | No | [] |
| entityFormation | VARCHAR(50) | | Type of entity formation | No | NULL |
| numberOfEmployees | INTEGER | >= 0 | Number of employees (for businesses) | No | NULL |
| usTaxStatus | ENUM | See tax codes | US tax classification | No | NULL |
| fatcaClassification | ENUM | See FATCA codes | FATCA entity classification | No | NULL |
| crsReportable | BOOLEAN | | CRS reportable flag | No | FALSE |
| crsEntityType | ENUM | See CRS codes | CRS entity type classification | No | NULL |
| taxResidencies | ARRAY<STRUCT> | See tax residency structure | Array of tax residency countries | No | [] |
| w8benStatus | ENUM('Active','Expired','NotProvided') | | W-8BEN form status | No | NULL |
| w9Status | ENUM('Active','Expired','NotProvided') | | W-9 form status | No | NULL |
| tinIssuingCountry | CHAR(2) | ISO 3166-1 | TIN issuing country (beyond primary) | No | NULL |
| secondaryTINs | ARRAY<STRUCT> | country, tin, tinType | Secondary tax IDs for multiple jurisdictions | No | [] |
| substantialUSOwner | BOOLEAN | | Substantial US owner flag (FATCA) | No | FALSE |
| nationalIDType | VARCHAR(50) | | Country-specific national ID type | No | NULL |
| nationalIDNumber | VARCHAR(50) | | National ID number | No | NULL |
| chinaHukou | VARCHAR(100) | | Hukou (household registration) - China | No | NULL |
| indiaAadharNumber | VARCHAR(12) | 12 digits | Aadhaar UID - India | No | NULL |
| indiaCANNumber | VARCHAR(20) | | PAN alternate - India | No | NULL |
| koreaAlienRegistrationNumber | VARCHAR(13) | 13 digits | Alien registration - South Korea | No | NULL |
| japanMyNumber | VARCHAR(12) | 12 digits | My Number / Individual Number - Japan | No | NULL |
| singaporeNRIC_FIN | VARCHAR(9) | Sxxxxxxx format | NRIC (citizen) or FIN (foreigner) - Singapore | No | NULL |

**Tax Residency Structure:**
```json
{
  "country": "US",  // ISO 3166-1 alpha-2
  "tinType": "EIN",  // SSN, EIN, VAT, etc.
  "tin": "12-3456789",
  "taxResidencyBasis": "CITIZENSHIP",  // CITIZENSHIP, RESIDENCE, DOMICILE, INCORPORATION
  "effectiveFrom": "2020-01-01",
  "effectiveTo": null  // NULL = current
}
```

**US Tax Status Codes:** US_CITIZEN, US_RESIDENT_ALIEN, NON_RESIDENT_ALIEN, US_CORPORATION, US_PARTNERSHIP, US_TRUST, FOREIGN_ENTITY

**FATCA Classification Codes:** ACTIVE_NFFE, PASSIVE_NFFE, FFI, PARTICIPATING_FFI, REGISTERED_DEEMED_COMPLIANT_FFI, CERTIFIED_DEEMED_COMPLIANT_FFI, EXCEPTED_FFI, EXEMPT_BENEFICIAL_OWNER, DIRECT_REPORTING_NFFE, SPONSORED_DIRECT_REPORTING_NFFE

**CRS Entity Type Codes:** FINANCIAL_INSTITUTION, ACTIVE_NFE, PASSIVE_NFE, INVESTMENT_ENTITY, GOVERNMENT_ENTITY, INTERNATIONAL_ORGANISATION, CENTRAL_BANK

**Regulatory Reporting Notes (Regional):**
- `givenName` and `familyName`: Required for AUSTRAC IFTI-E Fields 2.2, 2.3
- `suffix`: Required for FinCEN CTR Item 9
- `dbaName`: Required for FinCEN CTR Item 11
- `occupation`: Required for FinCEN CTR Item 12, SAR Item 45
- `naicsCode`: Required for FinCEN CTR Item 13 (6-digit NAICS code)
- `formOfIdentification`, `identificationNumber`: Required for FinCEN CTR Items 15-16
- `identificationIssuingCountry`, `identificationIssuingState`: Required for FinCEN CTR Items 17-18
- `alternateNames`: Required for FinCEN SAR Item 39
- `entityFormation`: Required for FinCEN SAR Item 44
- `numberOfEmployees`: Required for FinCEN SAR Item 46

**Address Structure** (used in postalAddress, residentialAddress, registeredAddress):

```
Address {
  addressType: ENUM('postal','residential','registered','business','po_box')
  department: VARCHAR(70)
  subDepartment: VARCHAR(70)
  streetName: VARCHAR(70)
  buildingNumber: VARCHAR(16)
  buildingName: VARCHAR(35)
  floor: VARCHAR(70)
  postBox: VARCHAR(16)
  room: VARCHAR(70)
  postCode: VARCHAR(16)
  townName: VARCHAR(35)
  townLocationName: VARCHAR(35)
  districtName: VARCHAR(35)
  countrySubDivision: VARCHAR(35)  // State/Province
  country: CHAR(2)  // ISO 3166-1 alpha-2
  addressLine: ARRAY<VARCHAR(70)>  // For unstructured addresses (max 7 lines)
  geolocation: STRUCT{latitude:DECIMAL(10,8), longitude:DECIMAL(11,8)}
  validFrom: DATE
  validTo: DATE
}
```

---

### Entity 3: Account

**Purpose**: Represents a bank account (debtor account, creditor account, nostro, vostro)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| accountId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| iban | VARCHAR(34) | ISO 13616 format | IBAN (if applicable) | No | NULL |
| bban | VARCHAR(30) | | Basic Bank Account Number | No | NULL |
| accountNumber | VARCHAR(34) | Not Null | Account number (proprietary format) | Yes | NULL |
| checkDigit | CHAR(2) | | Check digit (separate from account number) | No | NULL |
| accountName | VARCHAR(140) | | Account name/title | No | NULL |
| accountType | ENUM('current','savings','nostro','vostro','virtual','loan','escrow','suspense','gl_account') | Not Null | Account type | Yes | NULL |
| accountSubType | VARCHAR(50) | | Account subtype (product-specific) | No | NULL |
| currency | CHAR(3) | ISO 4217 | Account currency | Yes | 'USD' |
| multiCurrencyFlag | BOOLEAN | | Indicates if account supports multiple currencies | No | FALSE |
| supportedCurrencies | ARRAY<CHAR(3)> | | List of supported currencies (if multi-currency) | No | [] |
| servicer | UUID | FK to FinancialInstitution | Financial institution servicing the account | No | NULL |
| branch | VARCHAR(100) | | Branch identifier | No | NULL |
| sortCode | VARCHAR(6) | UK format (XX-XX-XX) | UK sort code (if UK account) | No | NULL |
| routingNumber | VARCHAR(9) | US ABA format | US routing number (if US account) | No | NULL |
| swiftBIC | VARCHAR(11) | ISO 9362 | SWIFT BIC for account | No | NULL |
| accountOwner | UUID | FK to Party | Account owner party | No | NULL |
| accountRelationship | ENUM('customer_account','nostro','vostro','internal','third_party') | Not Null | Relationship type | Yes | NULL |
| beneficialOwners | ARRAY<UUID> | FK to Party | Beneficial owners (if different from legal owner) | No | [] |
| jointAccountHolders | ARRAY<UUID> | FK to Party | Joint account holders | No | [] |
| accountStatus | ENUM('active','dormant','closed','frozen','blocked','restricted') | Not Null | Account status | Yes | 'active' |
| statusReason | VARCHAR(200) | | Reason for status (if not active) | No | NULL |
| statusEffectiveDate | DATE | | Date status became effective | No | NULL |
| openedDate | DATE | | Account opening date | No | NULL |
| closedDate | DATE | | Account closure date (if closed) | No | NULL |
| lastActivityDate | DATE | | Date of last transaction | No | NULL |
| dormantSince | DATE | | Date account became dormant | No | NULL |
| availableBalance | DECIMAL(18,2) | | Available balance (optional, not always populated) | No | NULL |
| ledgerBalance | DECIMAL(18,2) | | Ledger balance | No | NULL |
| holdAmount | DECIMAL(18,2) | | Amount on hold | No | NULL |
| minimumBalance | DECIMAL(18,2) | | Minimum balance requirement | No | NULL |
| maximumBalance | DECIMAL(18,2) | | Maximum balance allowed | No | NULL |
| overdraftLimit | DECIMAL(18,2) | | Overdraft limit (if applicable) | No | NULL |
| balanceLastUpdated | TIMESTAMP | | Timestamp of last balance update | No | NULL |
| restrictions | ARRAY<VARCHAR> | | Account restrictions (e.g., debit_only, credit_only, no_withdrawals) | No | [] |
| dailyDebitLimit | DECIMAL(18,2) | | Daily debit transaction limit | No | NULL |
| dailyCreditLimit | DECIMAL(18,2) | | Daily credit transaction limit | No | NULL |
| singleTransactionLimit | DECIMAL(18,2) | | Single transaction limit | No | NULL |
| monthlyTransactionLimit | DECIMAL(18,2) | | Monthly transaction limit | No | NULL |
| accountPurpose | VARCHAR(200) | | Purpose of account | No | NULL |
| mandateRequired | BOOLEAN | | Indicates if mandate required for debits | No | FALSE |
| activeMandates | ARRAY<VARCHAR> | | Active mandate references | No | [] |
| interestRate | DECIMAL(6,4) | | Interest rate (if interest-bearing) | No | NULL |
| interestAccrualMethod | ENUM('daily','monthly','quarterly','annually') | | Interest accrual method | No | NULL |
| taxWithholdingRate | DECIMAL(5,2) | | Tax withholding rate | No | NULL |
| statementFrequency | ENUM('daily','weekly','monthly','quarterly','annually','on_demand') | | Statement frequency | No | NULL |
| lastStatementDate | DATE | | Date of last statement | No | NULL |
| correspondentBankAccount | VARCHAR(34) | | Correspondent bank account (for nostro/vostro) | No | NULL |
| correspondentBankBIC | VARCHAR(11) | | Correspondent bank BIC | No | NULL |
| correspondentRelationshipType | ENUM('nostro','vostro','loro') | | Type of correspondent relationship | No | NULL |
| regulatoryClassification | VARCHAR(50) | | Regulatory account classification | No | NULL |
| accountingGLCode | VARCHAR(50) | | General ledger code | No | NULL |
| profitCenter | VARCHAR(50) | | Profit center allocation | No | NULL |
| costCenter | VARCHAR(50) | | Cost center allocation | No | NULL |
| riskRating | ENUM('low','medium','high') | | Account risk rating | No | NULL |
| sanctionsScreeningStatus | ENUM('clear','hit','pending') | | Sanctions screening status | No | NULL |
| amlRiskRating | ENUM('low','medium','high','very_high') | | AML risk rating | No | NULL |
| dataSource | VARCHAR(100) | | Data source system | No | NULL |
| dataQualityScore | DECIMAL(5,2) | 0-100 | Account data quality score | No | NULL |
| effectiveFrom | TIMESTAMP | Not Null | Effective start (SCD Type 2) | Yes | CURRENT_TIMESTAMP |
| effectiveTo | TIMESTAMP | | Effective end (NULL = current) | No | NULL |
| isCurrent | BOOLEAN | Not Null | Current version flag | Yes | TRUE |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |
| loanAmount | DECIMAL(18,2) | | Loan amount (if loan account) | No | NULL |
| loanOrigination | DATE | | Loan origination date | No | NULL |

**Regulatory Reporting Notes:**
- `openedDate`: Maps to FinCEN CTR Item 89 (Account opening date)
- `closedDate`: Maps to FinCEN SAR Item 90 (Account closing date)
- `accountStatus`: Maps to FinCEN SAR Item 89 (Account status code)
- `accountSubType`: Maps to FinCEN SAR Item 88 (Detailed product type)
- `loanAmount`: Required for FinCEN SAR Item 59 (Loan amount if applicable)
- `loanOrigination`: Required for FinCEN SAR Item 60 (Loan origination date)

---

### Entity 4: FinancialInstitution

**Purpose**: Represents a financial institution (agent banks, intermediaries, correspondents)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| financialInstitutionId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| bic | VARCHAR(11) | ISO 9362 (8 or 11 chars) | SWIFT BIC | No | NULL |
| lei | VARCHAR(20) | ISO 17442 | Legal Entity Identifier | No | NULL |
| name | VARCHAR(140) | Not Null | Financial institution name | Yes | NULL |
| legalName | VARCHAR(140) | | Official legal name | No | NULL |
| shortName | VARCHAR(35) | | Short name | No | NULL |
| financialInstitutionType | ENUM('commercial_bank','investment_bank','central_bank','credit_union','savings_and_loan','broker_dealer','payment_service_provider','clearing_house','other') | | Type of FI | No | NULL |
| regulatoryCategory | ENUM('bank','nbfi','psp','other') | | Regulatory category | No | NULL |
| branchIdentification | VARCHAR(50) | | Branch identifier | No | NULL |
| branchName | VARCHAR(140) | | Branch name | No | NULL |
| branchType | ENUM('head_office','branch','representative_office','subsidiary') | | Branch type | No | NULL |
| postalAddress | STRUCT | See Address structure | Primary postal address | No | NULL |
| registeredAddress | STRUCT | | Registered office address | No | NULL |
| phoneNumber | VARCHAR(25) | | Primary phone number | No | NULL |
| emailAddress | VARCHAR(255) | | Primary email address | No | NULL |
| websiteURL | VARCHAR(255) | | Website URL | No | NULL |
| clearingSystemMemberships | ARRAY<STRUCT> | See ClearingSystemMembership structure | Clearing system participations | No | [] |
| fedwireMemberId | VARCHAR(9) | | Fedwire ABA routing number | No | NULL |
| chipsMemberId | VARCHAR(4) | | CHIPS UID | No | NULL |
| targetMemberId | VARCHAR(11) | | TARGET2 BIC | No | NULL |
| chapsMemberId | VARCHAR(6) | | CHAPS sort code | No | NULL |
| rtpMemberId | VARCHAR(9) | | RTP routing number | No | NULL |
| corr espondentRelationships | ARRAY<STRUCT> | See CorrespondentRelationship structure | Correspondent banking relationships | No | [] |
| nostroAccounts | ARRAY<STRUCT{currency:CHAR(3), accountNumber:VARCHAR, counterpartyFI:UUID}> | | Nostro accounts held | No | [] |
| vostroAccounts | ARRAY<STRUCT{currency:CHAR(3), accountNumber:VARCHAR, counterpartyFI:UUID}> | | Vostro accounts maintained | No | [] |
| swiftMembershipStatus | ENUM('member','non_member','suspended','terminated') | | SWIFT membership status | No | NULL |
| swiftMemberSince | DATE | | Date joined SWIFT | No | NULL |
| primaryRegulator | VARCHAR(100) | | Primary regulatory authority | No | NULL |
| additionalRegulators | ARRAY<VARCHAR> | | Additional regulators | No | [] |
| jurisdiction | CHAR(2) | ISO 3166-1 alpha-2 | Primary jurisdiction | No | NULL |
| operatingJurisdictions | ARRAY<CHAR(2)> | | All operating jurisdictions | No | [] |
| regulatoryLicenses | ARRAY<STRUCT{licenseType:VARCHAR, licenseNumber:VARCHAR, issuingAuthority:VARCHAR, issueDate:DATE, expiryDate:DATE}> | | Regulatory licenses held | No | [] |
| bankingLicense | BOOLEAN | | Has banking license | No | FALSE |
| paymentServicesLicense | BOOLEAN | | Has payment services license | No | FALSE |
| stockExchangeListing | ARRAY<VARCHAR> | | Stock exchanges where listed | No | [] |
| publiclyTraded | BOOLEAN | | Publicly traded flag | No | FALSE |
| parentCompany | UUID | FK to FinancialInstitution | Ultimate parent company | No | NULL |
| subsidiaries | ARRAY<UUID> | FK to FinancialInstitution | Subsidiary institutions | No | [] |
| affiliates | ARRAY<UUID> | FK to FinancialInstitution | Affiliated institutions | No | [] |
| dueDiligenceStatus | ENUM('pending','in_progress','approved','rejected','expired') | | Due diligence status | No | NULL |
| dueDiligenceCompletedDate | DATE | | DD completion date | No | NULL |
| dueDiligenceExpiryDate | DATE | | DD expiry date | No | NULL |
| nextDueDiligenceReviewDate | DATE | | Next scheduled DD review | No | NULL |
| dueDiligenceDocuments | ARRAY<VARCHAR> | | DD documents collected | No | [] |
| riskRating | ENUM('low','medium','high') | | Correspondent risk rating | No | NULL |
| riskRatingDate | DATE | | Risk rating date | No | NULL |
| riskRatingRationale | TEXT | | Risk rating rationale | No | NULL |
| sanctionedFI | BOOLEAN | Not Null | Sanctioned institution flag | No | FALSE |
| sanctionedBy | ARRAY<VARCHAR> | | Sanctioning authorities | No | [] |
| highRiskJurisdiction | BOOLEAN | Not Null | Operates in high-risk jurisdiction | No | FALSE |
| adverseMediaFlag | BOOLEAN | Not Null | Adverse media flag | No | FALSE |
| restrictedFI | BOOLEAN | Not Null | Restricted institution flag | No | FALSE |
| restrictionReasons | ARRAY<VARCHAR> | | Reasons for restriction | No | [] |
| approvedForCorrespondentBanking | BOOLEAN | Not Null | Approved for correspondent relationships | No | FALSE |
| approvedProducts | ARRAY<VARCHAR> | | Approved products/services | No | [] |
| blockedProducts | ARRAY<VARCHAR> | | Blocked products/services | No | [] |
| transactionLimits | ARRAY<STRUCT{product:VARCHAR, limit:DECIMAL, currency:CHAR(3)}> | | Transaction limits per product | No | [] |
| creditRating | VARCHAR(10) | | Credit rating (e.g., Moody's, S&P) | No | NULL |
| creditRatingAgency | VARCHAR(50) | | Rating agency | No | NULL |
| creditRatingDate | DATE | | Rating date | No | NULL |
| financialStrength | ENUM('strong','adequate','weak','distressed') | | Financial strength assessment | No | NULL |
| capitalAdequacy Ratio | DECIMAL(5,2) | | Capital adequacy ratio | No | NULL |
| totalAssets | DECIMAL(18,2) | | Total assets (in millions, USD equivalent) | No | NULL |
| dataSource | VARCHAR(100) | | Data source | No | NULL |
| dataQualityScore | DECIMAL(5,2) | 0-100 | Data quality score | No | NULL |
| effectiveFrom | TIMESTAMP | Not Null | Effective start (SCD Type 2) | Yes | CURRENT_TIMESTAMP |
| effectiveTo | TIMESTAMP | | Effective end (NULL = current) | No | NULL |
| isCurrent | BOOLEAN | Not Null | Current version flag | Yes | TRUE |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |
| rssdNumber | VARCHAR(10) | | RSSD number (US Federal Reserve) | No | NULL |
| tinType | ENUM('EIN','SSN','ITIN','FOREIGN') | | Tax identification number type | No | NULL |
| tinValue | VARCHAR(20) | | Tax identification number value | No | NULL |
| fiType | ENUM('bank','credit_union','msb','broker_dealer','casino','other') | | Financial institution type | No | NULL |
| msbRegistrationNumber | VARCHAR(50) | | MSB registration number (if applicable) | No | NULL |
| branchCountry | CHAR(2) | ISO 3166-1 | Branch country | No | NULL |
| branchState | VARCHAR(3) | | Branch state/province | No | NULL |

**Regulatory Reporting Notes:**
- `rssdNumber`: Required for FinCEN CTR Item 74 (RSSD number for US banks)
- `tinType`, `tinValue`: Required for FinCEN CTR Items 79-80 (Tax ID type and value)
- `fiType`: Required for FinCEN CTR/SAR classification of financial institution type
- `msbRegistrationNumber`: Required for FinCEN SAR Item 95 (Money Services Business registration)
- `branchCountry`, `branchState`: Required for AUSTRAC IFTI Fields 4.4, 5.4 and FinCEN CTR Items 77, 86

**ClearingSystemMembership Structure**:
```
ClearingSystemMembership {
  clearingSystem: ENUM('FedACH','Fedwire','CHIPS','RTP','FedNow','TARGET2','CHAPS','BACS','FPS','SEPA','Euro1','STEP2','CIPS','PIX',...)
  memberId: VARCHAR(50)
  membershipType: ENUM('direct','indirect','indirect_remote')
  membershipStatus: ENUM('active','suspended','terminated')
  memberSince: DATE
  terminationDate: DATE
  role: ENUM('participant','settlement_bank','clearing_member')
}
```

**CorrespondentRelationship Structure**:
```
CorrespondentRelationship {
  counterpartyFI: UUID  // FK to FinancialInstitution
  relationshipType: ENUM('nostro','vostro','bilateral','clearing_agent')
  currency: CHAR(3)
  accountNumber: VARCHAR(34)
  status: ENUM('active','suspended','terminated')
  approvedDate: DATE
  effectiveDate: DATE
  expiryDate: DATE
  reviewDate: DATE
  transactionLimit: DECIMAL(18,2)
  outstandingLimit: DECIMAL(18,2)
  products: ARRAY<VARCHAR>
  purpose: VARCHAR(200)
}
```

### Entity 5: Settlement

**Purpose**: Represents settlement details for a payment (interbank settlement, cash settlement)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| settlementId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| settlementMethod | ENUM('INDA','INGA','COVE','CLRG') | ISO 20022 settlement codes | Settlement method (Interbank debit/credit, Cover, Clearing) | Yes | NULL |
| settlementAccount | UUID | FK to Account | Settlement account | No | NULL |
| settlementAmount | STRUCT{amount:DECIMAL(18,2), currency:CHAR(3)} | Not Null | Settlement amount | Yes | NULL |
| settlementDate | DATE | Not Null | Settlement date | Yes | NULL |
| settlementTime | TIME | | Settlement time (if known) | No | NULL |
| settlementPriority | ENUM('high','normal','low') | | Settlement priority | No | 'normal' |
| clearingChannel | ENUM('RTGS','DNS','mixed') | | Clearing channel type | No | NULL |
| clearingSystem | VARCHAR(50) | | Clearing system code | No | NULL |
| clearingSystemReference | VARCHAR(35) | | Clearing system reference number | No | NULL |
| clearingSystemProprietaryCode | VARCHAR(35) | | System proprietary code | No | NULL |
| interbankSettlementAmount | DECIMAL(18,2) | | Interbank settlement amount | No | NULL |
| instructedAmount | DECIMAL(18,2) | | Instructed amount (before charges) | No | NULL |
| counterValueAmount | STRUCT{amount:DECIMAL(18,2), currency:CHAR(3)} | | Counter value in different currency | No | NULL |
| exchangeRate | DECIMAL(15,10) | | Exchange rate for settlement | No | NULL |
| settlementStatus | ENUM('pending','processing','settled','failed','cancelled','suspended') | Not Null | Settlement status | Yes | 'pending' |
| settlementStatusTimestamp | TIMESTAMP | Not Null | Status timestamp | Yes | CURRENT_TIMESTAMP |
| failureReason | VARCHAR(4) | | Settlement failure reason code | No | NULL |
| failureDescription | TEXT | | Settlement failure description | No | NULL |
| nostroAccountDebit | UUID | FK to Account | Nostro account debited | No | NULL |
| nostroAccountCredit | UUID | FK to Account | Nostro account credited | No | NULL |
| settlingAgent | UUID | FK to FinancialInstitution | Settling financial institution | No | NULL |
| settlementInstructionId | VARCHAR(35) | | Settlement instruction ID | No | NULL |
| netSettlementAmount | DECIMAL(18,2) | | Net settlement (after netting) | No | NULL |
| grossSettlementAmount | DECIMAL(18,2) | | Gross settlement amount | No | NULL |
| settlementBatchId | VARCHAR(35) | | Batch ID for bulk settlements | No | NULL |
| settlementCycle | VARCHAR(10) | | Settlement cycle identifier | No | NULL |
| confirmationReceived | BOOLEAN | Not Null | Settlement confirmation received | No | FALSE |
| confirmationTimestamp | TIMESTAMP | | Confirmation receipt timestamp | No | NULL |
| confirmationReference | VARCHAR(35) | | Confirmation reference number | No | NULL |
| dataSource | VARCHAR(100) | | Source system for settlement data | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |

---

### Entity 6: Charge

**Purpose**: Represents charges/fees associated with a payment

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| chargeId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| chargeType | ENUM('CRED','DEBT','SHAR','INST','CORR','OTHR') | | Type of charge (creditor, debtor, shared, instructing, correspondent, other) | Yes | NULL |
| chargeCategory | ENUM('transaction_fee','fx_markup','correspondent_fee','regulatory_fee','service_charge','penalty','other') | | Charge category | No | NULL |
| chargeBearer | ENUM('DEBT','CRED','SHAR','SLEV') | | Who bears the charge | Yes | NULL |
| chargeAmount | STRUCT{amount:DECIMAL(18,2), currency:CHAR(3)} | amount >= 0 | Charge amount | Yes | NULL |
| equivalentAmount | STRUCT{amount:DECIMAL(18,2), currency:CHAR(3)} | | Equivalent amount in payment currency | No | NULL |
| taxAmount | DECIMAL(18,2) | >= 0 | Tax on charge | No | NULL |
| taxRate | DECIMAL(5,2) | 0-100 | Tax rate percentage | No | NULL |
| taxType | VARCHAR(50) | | Type of tax (VAT, GST, etc.) | No | NULL |
| baseAmount | DECIMAL(18,2) | | Base amount for percentage charges | No | NULL |
| chargeRate | DECIMAL(8,5) | | Charge rate (for percentage-based) | No | NULL |
| minimumCharge | DECIMAL(18,2) | | Minimum charge amount | No | NULL |
| maximumCharge | DECIMAL(18,2) | | Maximum charge amount | No | NULL |
| chargeAgentId | UUID | FK to FinancialInstitution | FI that levied the charge | No | NULL |
| chargeAccount | UUID | FK to Account | Account to which charge posted | No | NULL |
| chargeDescription | VARCHAR(500) | | Charge description | No | NULL |
| chargePurpose | VARCHAR(4) | | ISO 20022 charge purpose code | No | NULL |
| regulatoryCharge | BOOLEAN | Not Null | Indicates regulatory/compliance charge | No | FALSE |
| regulatoryAuthority | VARCHAR(100) | | Regulatory authority (if regulatory charge) | No | NULL |
| waivedFlag | BOOLEAN | Not Null | Charge waived indicator | No | FALSE |
| waivedReason | VARCHAR(200) | | Reason for waiver | No | NULL |
| waivedBy | VARCHAR(100) | | Who authorized waiver | No | NULL |
| waivedTimestamp | TIMESTAMP | | When charge was waived | No | NULL |
| chargeStatus | ENUM('calculated','pending','charged','waived','refunded') | Not Null | Charge status | Yes | 'calculated' |
| chargeTimestamp | TIMESTAMP | | When charge was applied | No | NULL |
| reversalFlag | BOOLEAN | Not Null | Charge was reversed | No | FALSE |
| reversalReason | VARCHAR(200) | | Reversal reason | No | NULL |
| reversalTimestamp | TIMESTAMP | | Reversal timestamp | No | NULL |
| chargeReference | VARCHAR(35) | | Charge reference number | No | NULL |
| glAccount | VARCHAR(50) | | General ledger account for charge | No | NULL |
| revenueRecognition | ENUM('immediate','deferred','amortized') | | Revenue recognition treatment | No | NULL |
| dataSource | VARCHAR(100) | | Source system | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |

---

### Entity 7: RegulatoryInfo

**Purpose**: Captures regulatory reporting information and compliance data elements

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| regulatoryInfoId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| regulationType | ENUM('bsa_aml','ofac','ctr','sar','fincen','fbar','kyc','psd2','gdpr','mifid','emir','crs','fatca','other') | | Type of regulatory requirement | Yes | NULL |
| jurisdiction | CHAR(2) | ISO 3166-1 alpha-2 | Regulatory jurisdiction | Yes | NULL |
| regulatoryAuthority | VARCHAR(100) | | Regulatory authority name | No | NULL |
| reportingRequirement | VARCHAR(100) | | Specific reporting requirement | No | NULL |
| reportingCode | VARCHAR(35) | | Regulatory reporting code | No | NULL |
| reportingDetails | TEXT | | Free-text regulatory details | No | NULL |
| structuredReportingData | JSON | | Structured regulatory data | No | {} |
| crossBorderFlag | BOOLEAN | Not Null | Cross-border transaction | Yes | FALSE |
| crossBorderCountries | ARRAY<CHAR(2)> | | Countries involved | No | [] |
| highValueTransaction | BOOLEAN | Not Null | High value transaction flag (>$10K USD equivalent) | No | FALSE |
| thresholdAmount | DECIMAL(18,2) | | Regulatory threshold amount | No | NULL |
| thresholdCurrency | CHAR(3) | | Threshold currency | No | NULL |
| ctrRequired | BOOLEAN | Not Null | Currency Transaction Report required | No | FALSE |
| ctrFilingDate | DATE | | CTR filing date | No | NULL |
| ctrReferenceNumber | VARCHAR(50) | | CTR reference number | No | NULL |
| sarRequired | BOOLEAN | Not Null | Suspicious Activity Report required | No | FALSE |
| sarFilingDate | DATE | | SAR filing date | No | NULL |
| sarReferenceNumber | VARCHAR(50) | | SAR reference number | No | NULL |
| ofacReportingRequired | BOOLEAN | Not Null | OFAC reporting required | No | FALSE |
| ofacBlockedTransaction | BOOLEAN | Not Null | OFAC blocked transaction | No | FALSE |
| ofacRejectedTransaction | BOOLEAN | Not Null | OFAC rejected transaction | No | FALSE |
| ofacFilingDate | DATE | | OFAC report filing date | No | NULL |
| fatcaApplicable | BOOLEAN | Not Null | FATCA applicable | No | FALSE |
| fatcaStatus | VARCHAR(50) | | FATCA status classification | No | NULL |
| crsApplicable | BOOLEAN | Not Null | Common Reporting Standard applicable | No | FALSE |
| crsReportingJurisdiction | CHAR(2) | | CRS reporting jurisdiction | No | NULL |
| psd2Applicable | BOOLEAN | Not Null | PSD2/PSD3 applicable (EU payments) | No | FALSE |
| psd2StrongAuthRequired | BOOLEAN | | SCA required | No | NULL |
| psd2ExemptionType | VARCHAR(50) | | SCA exemption type | No | NULL |
| gdprApplicable | BOOLEAN | Not Null | GDPR applicable | No | FALSE |
| gdprLegalBasis | ENUM('consent','contract','legal_obligation','vital_interests','public_task','legitimate_interests') | | GDPR legal basis for processing | No | NULL |
| gdprDataRetentionPeriod | INTEGER | In days | Data retention period (days) | No | NULL |
| doraApplicable | BOOLEAN | Not Null | DORA applicable (Digital Operational Resilience Act) | No | FALSE |
| sanctionsScreeningPerformed | BOOLEAN | Not Null | Sanctions screening performed | No | FALSE |
| sanctionsScreeningTimestamp | TIMESTAMP | | Screening timestamp | No | NULL |
| sanctionsHit | BOOLEAN | Not Null | Sanctions hit detected | No | FALSE |
| sanctionsListNames | ARRAY<VARCHAR> | | Sanction lists with hits | No | [] |
| sanctionsFalsePositive | BOOLEAN | | False positive indicator | No | NULL |
| sanctionsClearanceTimestamp | TIMESTAMP | | Clearance timestamp | No | NULL |
| sanctionsClearedBy | VARCHAR(100) | | Who cleared the hit | No | NULL |
| amlRiskScore | DECIMAL(5,2) | 0-100 | AML risk score | No | NULL |
| amlRiskFactors | ARRAY<VARCHAR> | | AML risk factors identified | No | [] |
| amlReviewRequired | BOOLEAN | Not Null | Manual AML review required | No | FALSE |
| amlReviewedBy | VARCHAR(100) | | AML reviewer | No | NULL |
| amlReviewTimestamp | TIMESTAMP | | AML review timestamp | No | NULL |
| amlReviewDecision | ENUM('approve','reject','escalate','hold') | | AML review decision | No | NULL |
| beneficialOwnershipDeclared | BOOLEAN | | Beneficial ownership declared | No | NULL |
| beneficialOwners | ARRAY<UUID> | FK to Party | Beneficial owners | No | [] |
| economicPurpose | TEXT | | Economic purpose of transaction | No | NULL |
| sourceOfFunds | VARCHAR(200) | | Source of funds | No | NULL |
| purposeOfPayment | VARCHAR(500) | | Purpose of payment (regulatory) | No | NULL |
| relationshipToCounterparty | VARCHAR(200) | | Relationship to counterparty | No | NULL |
| pepInvolved | BOOLEAN | Not Null | PEP involved in transaction | No | FALSE |
| pepDetails | TEXT | | PEP details | No | NULL |
| highRiskCountry | BOOLEAN | Not Null | High-risk country involved | No | FALSE |
| highRiskCountryCodes | ARRAY<CHAR(2)> | | High-risk country codes | No | [] |
| cashIntensiveBusiness | BOOLEAN | | Cash-intensive business indicator | No | NULL |
| structuringIndicator | BOOLEAN | Not Null | Structuring to avoid reporting | No | FALSE |
| rapidMovementOfFunds | BOOLEAN | | Rapid movement indicator | No | NULL |
| roundDollarAmount | BOOLEAN | | Round dollar amount (potential red flag) | No | NULL |
| unusualActivityFlag | BOOLEAN | Not Null | Unusual activity detected | No | FALSE |
| unusualActivityDescription | TEXT | | Description of unusual activity | No | NULL |
| regulatoryExemption | VARCHAR(100) | | Applicable exemption | No | NULL |
| exemptionReason | TEXT | | Reason for exemption | No | NULL |
| complianceApprovalRequired | BOOLEAN | Not Null | Compliance approval required | No | FALSE |
| complianceApprovedBy | VARCHAR(100) | | Compliance approver | No | NULL |
| complianceApprovalTimestamp | TIMESTAMP | | Approval timestamp | No | NULL |
| dataSource | VARCHAR(100) | | Source system | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |

---

### Entity 8: RemittanceInfo

**Purpose**: Captures remittance information and payment purpose details

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| remittanceInfoId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| remittanceInformationType | ENUM('structured','unstructured','both') | | Type of remittance information | Yes | NULL |
| unstructuredRemittanceInfo | ARRAY<VARCHAR(140)> | Max 140 chars per line | Unstructured remittance (free text) | No | [] |
| creditorReferenceType | VARCHAR(35) | | Creditor reference type code | No | NULL |
| creditorReference | VARCHAR(35) | | Creditor reference (invoice, account number) | No | NULL |
| invoiceNumber | VARCHAR(35) | | Invoice number | No | NULL |
| invoiceDate | DATE | | Invoice date | No | NULL |
| invoiceAmount | DECIMAL(18,2) | | Invoice amount | No | NULL |
| purchaseOrderNumber | VARCHAR(35) | | Purchase order number | No | NULL |
| contractNumber | VARCHAR(35) | | Contract number | No | NULL |
| billNumber | VARCHAR(35) | | Bill number | No | NULL |
| documentType | VARCHAR(35) | | Type of document referenced | No | NULL |
| documentNumber | VARCHAR(35) | | Document number | No | NULL |
| documentDate | DATE | | Document date | No | NULL |
| referredDocumentAmount | DECIMAL(18,2) | | Amount of referred document | No | NULL |
| lineItems | ARRAY<STRUCT> | See LineItem structure | Invoice/payment line items | No | [] |
| discountAmount | DECIMAL(18,2) | | Discount amount | No | NULL |
| discountRate | DECIMAL(5,2) | | Discount rate percentage | No | NULL |
| taxAmount | DECIMAL(18,2) | | Tax amount | No | NULL |
| taxRate | DECIMAL(5,2) | | Tax rate | No | NULL |
| taxType | VARCHAR(50) | | Tax type (VAT, GST, Sales Tax) | No | NULL |
| taxIdentificationNumber | VARCHAR(50) | | Tax ID related to payment | No | NULL |
| shippingCost | DECIMAL(18,2) | | Shipping cost | No | NULL |
| handlingFee | DECIMAL(18,2) | | Handling fee | No | NULL |
| adjustmentAmount | DECIMAL(18,2) | | Adjustment amount (can be negative) | No | NULL |
| adjustmentReason | VARCHAR(200) | | Reason for adjustment | No | NULL |
| additionalRemittanceInformation | TEXT | | Additional remittance details | No | NULL |
| paymentTerm | VARCHAR(50) | | Payment terms (Net 30, COD, etc.) | No | NULL |
| paymentDueDate | DATE | | Payment due date | No | NULL |
| earlyPaymentDiscount | BOOLEAN | | Early payment discount applied | No | NULL |
| latePaymentPenalty | DECIMAL(18,2) | | Late payment penalty | No | NULL |
| payeeNote | TEXT | | Note for payee | No | NULL |
| payerNote | TEXT | | Note from payer | No | NULL |
| categoryPurpose | VARCHAR(4) | ISO 20022 category purpose | Category purpose code | No | NULL |
| localInstrument | VARCHAR(35) | | Local instrument code | No | NULL |
| serviceLevel | VARCHAR(4) | | Service level code | No | NULL |
| dataSource | VARCHAR(100) | | Source system | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |

**LineItem Structure**:
```
LineItem {
  lineItemNumber: INTEGER
  description: VARCHAR(500)
  quantity: DECIMAL(10,2)
  unitPrice: DECIMAL(18,2)
  unitOfMeasure: VARCHAR(10)
  lineItemAmount: DECIMAL(18,2)
  taxAmount: DECIMAL(18,2)
  discountAmount: DECIMAL(18,2)
  productCode: VARCHAR(50)
  commodityCode: VARCHAR(35)
  hsCode: VARCHAR(10)  // Harmonized System code
}
```

---

### Entity 9: StatusEvent

**Purpose**: Complete audit trail of all status changes for a payment

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| statusEventId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| eventSequence | INTEGER | >= 1 | Sequence number of event | Yes | 1 |
| status | ENUM | See PaymentStatus enum | Payment status | Yes | NULL |
| previousStatus | ENUM | | Previous status | No | NULL |
| statusReason | VARCHAR(4) | ISO 20022 status reason | Status reason code | No | NULL |
| statusReasonText | TEXT | | Status reason description | No | NULL |
| statusCategory | ENUM('initiation','processing','settlement','exception','completion') | | Status category | No | NULL |
| eventTimestamp | TIMESTAMP | Not Null | When status change occurred | Yes | CURRENT_TIMESTAMP |
| eventSource | VARCHAR(100) | | System/component that generated event | No | NULL |
| eventType | ENUM('status_change','notification','alert','milestone','error','system_event') | | Type of event | Yes | NULL |
| isTerminalStatus | BOOLEAN | | Indicates terminal status (completed/failed/rejected) | No | FALSE |
| errorCode | VARCHAR(10) | | Error code (if error) | No | NULL |
| errorMessage | TEXT | | Error message | No | NULL |
| errorSeverity | ENUM('info','warning','error','critical') | | Error severity | No | NULL |
| processingStage | VARCHAR(100) | | Processing stage when event occurred | No | NULL |
| systemComponent | VARCHAR(100) | | System component | No | NULL |
| userId | VARCHAR(100) | | User who triggered event (if manual) | No | NULL |
| automatedFlag | BOOLEAN | Not Null | Automated vs manual event | Yes | TRUE |
| notificationSent | BOOLEAN | Not Null | Notification sent to customer | No | FALSE |
| notificationChannels | ARRAY<VARCHAR> | | Channels used (email, SMS, API callback) | No | [] |
| notificationTimestamp | TIMESTAMP | | When notification sent | No | NULL |
| retryAttempt | INTEGER | >= 0 | Retry attempt number (if retried) | No | NULL |
| maxRetries | INTEGER | | Maximum retries configured | No | NULL |
| retryTimestamp | TIMESTAMP | | Next retry scheduled time | No | NULL |
| slaBreachFlag | BOOLEAN | Not Null | SLA breach indicator | No | FALSE |
| slaDueTimestamp | TIMESTAMP | | SLA due timestamp | No | NULL |
| slaActualTimestamp | TIMESTAMP | | SLA actual completion timestamp | No | NULL |
| slaVariance | INTEGER | In seconds | SLA variance (negative = breach) | No | NULL |
| settlementTimestamp | TIMESTAMP | | Settlement timestamp (if settled) | No | NULL |
| confirmationReceived | BOOLEAN | | Confirmation received from counterparty | No | NULL |
| externalReference | VARCHAR(35) | | External system reference | No | NULL |
| additionalData | JSON | | Additional event-specific data | No | {} |
| dataSource | VARCHAR(100) | | Source system | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |

**PaymentStatus ENUM Values**:
```
- initiated
- received
- accepted
- validation_pending
- validated
- validation_failed
- fraud_screening
- fraud_clear
- fraud_hold
- fraud_reject
- sanctions_screening
- sanctions_clear
- sanctions_hit
- sanctions_rejected
- compliance_review
- compliance_approved
- compliance_rejected
- enrichment_pending
- enriched
- processing
- queued
- routed
- transmitted
- in_clearing
- clearing_failed
- settled
- settlement_pending
- settlement_failed
- completed
- returned
- reversed
- cancelled
- rejected
- failed
- suspended
- on_hold
- awaiting_approval
- approved
- partially_settled
```

---

### Entity 10: PaymentRelationship

**Purpose**: Captures relationships between payments (returns, reversals, covers, etc.)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| relationshipId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| sourcePaymentId | UUID | FK to PaymentInstruction, Not Null | Source payment | Yes | NULL |
| relatedPaymentId | UUID | FK to PaymentInstruction, Not Null | Related payment | Yes | NULL |
| relationshipType | ENUM('return','reversal','cancellation','cover','underlying','amendment','partial','duplicate','refund','chargeback','recall','investigation') | | Type of relationship | Yes | NULL |
| relationshipDirection | ENUM('forward','backward','bidirectional') | | Direction of relationship | Yes | 'forward' |
| relationshipReason | VARCHAR(4) | ISO 20022 codes | Reason code for relationship | No | NULL |
| relationshipReasonText | TEXT | | Reason description | No | NULL |
| relationshipTimestamp | TIMESTAMP | Not Null | When relationship created | Yes | CURRENT_TIMESTAMP |
| originalAmount | DECIMAL(18,2) | | Original payment amount | No | NULL |
| relatedAmount | DECIMAL(18,2) | | Related payment amount | No | NULL |
| partialFlag | BOOLEAN | Not Null | Indicates partial return/reversal | No | FALSE |
| percentageOfOriginal | DECIMAL(5,2) | 0-100 | Percentage of original payment | No | NULL |
| returnReasonCode | VARCHAR(4) | | Return reason code (ACH, SEPA, etc.) | No | NULL |
| returnReasonDescription | TEXT | | Return reason description | No | NULL |
| initiatingParty | ENUM('debtor','creditor','debtor_agent','creditor_agent','intermediary','central_bank') | | Who initiated the relationship | No | NULL |
| automaticReturn | BOOLEAN | | System-generated automatic return | No | NULL |
| dishonorReason | VARCHAR(200) | | Dishonor reason (for checks/ACH) | No | NULL |
| originalInstructionId | VARCHAR(35) | | Original instruction ID | No | NULL |
| originalEndToEndId | VARCHAR(35) | | Original end-to-end ID | No | NULL |
| originalUETR | UUID | | Original UETR (SWIFT) | No | NULL |
| originalTransactionReference | VARCHAR(35) | | Original transaction reference | No | NULL |
| compensationAmount | DECIMAL(18,2) | | Compensation amount (if applicable) | No | NULL |
| feesReturned | DECIMAL(18,2) | | Fees returned | No | NULL |
| effectiveDate | DATE | | Effective date of relationship | No | NULL |
| settlementImpact | ENUM('full_reversal','partial_reversal','no_impact','additional_settlement') | | Impact on settlement | No | NULL |
| accountingImpact | ENUM('debit','credit','reversal','no_impact') | | Accounting impact | No | NULL |
| regulatoryReportingRequired | BOOLEAN | Not Null | Regulatory reporting required | No | FALSE |
| investigationRequired | BOOLEAN | Not Null | Investigation required | No | FALSE |
| investigationId | VARCHAR(50) | | Investigation case ID | No | NULL |
| resolutionStatus | ENUM('open','pending','resolved','closed','escalated') | | Resolution status | No | NULL |
| resolutionTimestamp | TIMESTAMP | | Resolution timestamp | No | NULL |
| resolvedBy | VARCHAR(100) | | Who resolved | No | NULL |
| customerNotified | BOOLEAN | Not Null | Customer notified | No | FALSE |
| notificationTimestamp | TIMESTAMP | | Notification timestamp | No | NULL |
| dataSource | VARCHAR(100) | | Source system | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedBy | VARCHAR(100) | | User/system that updated | No | 'SYSTEM' |
| recordVersion | INTEGER | >= 1 | Record version | No | 1 |
| isDeleted | BOOLEAN | Not Null | Soft delete flag | No | FALSE |

---

## SUPPORTING DOMAIN ENTITIES

### Entity 11: UltimateParty

**Purpose**: Represents ultimate debtor or ultimate creditor (different from ordering/beneficiary)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| ultimatePartyId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| partyRole | ENUM('ultimate_debtor','ultimate_creditor') | | Role of ultimate party | Yes | NULL |
| partyId | UUID | FK to Party | Reference to party entity | No | NULL |
| name | VARCHAR(140) | | Ultimate party name | No | NULL |
| identification | VARCHAR(35) | | Party identification | No | NULL |
| identificationScheme | VARCHAR(35) | | Identification scheme | No | NULL |
| country | CHAR(2) | ISO 3166-1 alpha-2 | Country | No | NULL |
| taxId | VARCHAR(50) | | Tax identification | No | NULL |
| address | STRUCT | See Address structure | Address | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 12: PaymentPurpose

**Purpose**: Detailed payment purpose and classification

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| paymentPurposeId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| purposeCode | VARCHAR(4) | ISO 20022 external purpose | Purpose code | No | NULL |
| categoryPurpose | VARCHAR(4) | ISO 20022 category purpose | Category purpose code | No | NULL |
| localInstrument | VARCHAR(35) | | Local instrument | No | NULL |
| serviceLevel | VARCHAR(4) | | Service level | No | NULL |
| clearingChannel | ENUM('RTGS','book_transfer','mixed_settlement') | | Clearing channel | No | NULL |
| purposeDescription | TEXT | | Purpose description | No | NULL |
| economicPurpose | VARCHAR(200) | | Economic purpose | No | NULL |
| natureOfTransaction | VARCHAR(200) | | Nature of transaction | No | NULL |
| paymentContext | ENUM('B2B','B2C','C2B','C2C','G2B','G2C','B2G','other') | | Payment context | No | NULL |
| tradeRelated | BOOLEAN | | Trade-related payment | No | NULL |
| invoiceRelated | BOOLEAN | | Invoice-related payment | No | NULL |
| salaryPayment | BOOLEAN | | Salary payment | No | NULL |
| pensionPayment | BOOLEAN | | Pension payment | No | NULL |
| taxPayment | BOOLEAN | | Tax payment | No | NULL |
| utilityPayment | BOOLEAN | | Utility payment | No | NULL |
| loanPayment | BOOLEAN | | Loan payment | No | NULL |
| investmentRelated | BOOLEAN | | Investment-related | No | NULL |
| charityDonation | BOOLEAN | | Charity donation | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 13: ExchangeRateInfo

**Purpose**: Foreign exchange information for multi-currency payments

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| exchangeRateInfoId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Parent payment | Yes | NULL |
| sourceCurrency | CHAR(3) | ISO 4217 | Source currency | Yes | NULL |
| targetCurrency | CHAR(3) | ISO 4217 | Target currency | Yes | NULL |
| exchangeRate | DECIMAL(15,10) | > 0 | Exchange rate | Yes | NULL |
| inverseExchangeRate | DECIMAL(15,10) | > 0 | Inverse rate | No | NULL |
| rateType | ENUM('spot','forward','agreed','actual','market') | | Rate type | Yes | NULL |
| quotationDate | DATE | | Date of quotation | No | NULL |
| quotationTime | TIME | | Time of quotation | No | NULL |
| contractIdentification | VARCHAR(35) | | FX contract ID | No | NULL |
| rateSource | VARCHAR(100) | | Rate source (Bloomberg, Reuters, etc.) | No | NULL |
| sourceAmount | DECIMAL(18,2) | | Source amount | Yes | NULL |
| targetAmount | DECIMAL(18,2) | | Target amount | Yes | NULL |
| fxMarkup | DECIMAL(8,5) | | FX markup percentage | No | NULL |
| fxMarkupAmount | DECIMAL(18,2) | | FX markup amount | No | NULL |
| buyRate | DECIMAL(15,10) | | Buy rate | No | NULL |
| sellRate | DECIMAL(15,10) | | Sell rate | No | NULL |
| midRate | DECIMAL(15,10) | | Mid-market rate | No | NULL |
| rateSpread | DECIMAL(8,5) | | Rate spread | No | NULL |
| deliveryDate | DATE | | FX delivery date | No | NULL |
| fixingDate | DATE | | Rate fixing date | No | NULL |
| rateValidityPeriod | INTEGER | In hours | Rate validity period | No | NULL |
| guaranteedRate | BOOLEAN | | Rate guaranteed flag | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

## REFERENCE DATA ENTITIES

### Entity 14: Currency

**Purpose**: ISO 4217 currency reference data

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| currencyCode | CHAR(3) | PK, ISO 4217 alpha-3 | Currency code | Yes | NULL |
| currencyNumber | CHAR(3) | ISO 4217 numeric | Numeric currency code | No | NULL |
| currencyName | VARCHAR(100) | | Official currency name | Yes | NULL |
| currencySymbol | VARCHAR(10) | | Currency symbol | No | NULL |
| minorUnit | INTEGER | 0-4 | Number of decimal places | No | 2 |
| countries | ARRAY<CHAR(2)> | | Countries using currency | No | [] |
| centralBank | VARCHAR(200) | | Issuing central bank | No | NULL |
| isFiat | BOOLEAN | | Fiat vs digital currency | No | TRUE |
| isActive | BOOLEAN | Not Null | Active currency | Yes | TRUE |
| withdrawnDate | DATE | | Date withdrawn (if applicable) | No | NULL |
| replacedByCurrency | CHAR(3) | | Replacement currency code | No | NULL |
| peg | VARCHAR(50) | | Pegged to (if applicable) | No | NULL |
| volatility | ENUM('low','medium','high') | | Currency volatility classification | No | NULL |
| convertibilityStatus | ENUM('fully_convertible','partially_convertible','non_convertible') | | Convertibility status | No | NULL |
| capitalControlsApply | BOOLEAN | | Capital controls in effect | No | NULL |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | '1900-01-01' |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 15: Country

**Purpose**: ISO 3166 country/jurisdiction reference data

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| countryCode | CHAR(2) | PK, ISO 3166-1 alpha-2 | Country code | Yes | NULL |
| countryCode3 | CHAR(3) | ISO 3166-1 alpha-3 | 3-letter country code | No | NULL |
| countryNumeric | CHAR(3) | ISO 3166-1 numeric | Numeric country code | No | NULL |
| countryName | VARCHAR(100) | | Official country name | Yes | NULL |
| officialLanguage | VARCHAR(50) | | Official language | No | NULL |
| region | ENUM('AMER','EMEA','APAC','LATAM','MENA') | | Geographic region | No | NULL |
| subRegion | VARCHAR(50) | | Sub-region | No | NULL |
| continent | VARCHAR(50) | | Continent | No | NULL |
| currency | CHAR(3) | FK to Currency | Primary currency | No | NULL |
| phonePrefix | VARCHAR(10) | | International phone prefix | No | NULL |
| timezone | VARCHAR(50) | | Primary timezone | No | NULL |
| capitalCity | VARCHAR(100) | | Capital city | No | NULL |
| isEUMember | BOOLEAN | | EU member state | No | FALSE |
| isOECDMember | BOOLEAN | | OECD member | No | FALSE |
| isSEPACountry | BOOLEAN | | SEPA participating country | No | FALSE |
| fatfMember | BOOLEAN | | FATF member | No | FALSE |
| fatfJurisdiction | ENUM('compliant','monitored','blacklist','greylist') | | FATF jurisdiction status | No | NULL |
| highRiskJurisdiction | BOOLEAN | Not Null | High-risk for AML/CFT | No | FALSE |
| sanctionedCountry | BOOLEAN | Not Null | Country under sanctions | No | FALSE |
| sanctioningAuthorities | ARRAY<VARCHAR> | | Authorities imposing sanctions | No | [] |
| dataPrivacyRegime | VARCHAR(100) | | Data privacy regime (GDPR, etc.) | No | NULL |
| taxHaven | BOOLEAN | | Identified as tax haven | No | NULL |
| crsParticipant | BOOLEAN | | CRS participant | No | NULL |
| fatcaIGA | ENUM('none','model_1','model_2') | | FATCA IGA type | No | NULL |
| politicalStabilityRating | ENUM('stable','moderate','unstable') | | Political stability | No | NULL |
| corruptionIndex | DECIMAL(5,2) | 0-100 | Transparency International CPI | No | NULL |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | '1900-01-01' |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 16: ClearingSystem

**Purpose**: Payment clearing system reference data

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| clearingSystemCode | VARCHAR(50) | PK | Clearing system code | Yes | NULL |
| clearingSystemName | VARCHAR(200) | | Full name | Yes | NULL |
| clearingSystemType | ENUM('RTGS','ACH','card','check','securities','multi_currency') | | Type of system | Yes | NULL |
| country | CHAR(2) | ISO 3166-1 alpha-2 | Operating country/region | No | NULL |
| region | VARCHAR(50) | | Operating region | No | NULL |
| operator | VARCHAR(200) | | System operator | No | NULL |
| operatorType | ENUM('central_bank','private','consortium') | | Operator type | No | NULL |
| supportedCurrencies | ARRAY<CHAR(3)> | | Supported currencies | No | [] |
| settlementCurrency | CHAR(3) | | Primary settlement currency | No | NULL |
| settlementModel | ENUM('gross','net','hybrid') | | Settlement model | No | NULL |
| operatingHours | VARCHAR(100) | | Operating hours | No | NULL |
| operatingDays | VARCHAR(100) | | Operating days | No | NULL |
| cutoffTime | TIME | | Daily cutoff time | No | NULL |
| averageSettlementTime | INTEGER | In minutes | Average settlement time | No | NULL |
| realTimeSettlement | BOOLEAN | | Real-time settlement capability | No | NULL |
| iso20022Compliant | BOOLEAN | | ISO 20022 compliant | No | NULL |
| messageFormats | ARRAY<VARCHAR> | | Supported message formats | No | [] |
| averageDailyVolume | DECIMAL(18,0) | | Average daily transaction volume | No | NULL |
| averageDailyValue | DECIMAL(18,2) | In millions | Average daily value | No | NULL |
| minimumTransactionAmount | DECIMAL(18,2) | | Minimum transaction | No | NULL |
| maximumTransactionAmount | DECIMAL(18,2) | | Maximum transaction | No | NULL |
| membershipRequired | BOOLEAN | | Membership required | No | TRUE |
| directParticipants | INTEGER | | Number of direct participants | No | NULL |
| indirectParticipants | INTEGER | | Number of indirect participants | No | NULL |
| website | VARCHAR(255) | | Official website | No | NULL |
| regulatoryOversight | VARCHAR(200) | | Regulatory oversight authority | No | NULL |
| pfmiCompliant | BOOLEAN | | CPMI-IOSCO PFMI compliant | No | NULL |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| isActive | BOOLEAN | Not Null | Active system | Yes | TRUE |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 17: PurposeCode

**Purpose**: ISO 20022 external purpose codes

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| purposeCode | VARCHAR(4) | PK | Purpose code | Yes | NULL |
| purposeName | VARCHAR(200) | | Purpose name | Yes | NULL |
| purposeDescription | TEXT | | Detailed description | No | NULL |
| categoryPurpose | VARCHAR(4) | | Parent category purpose | No | NULL |
| iso20022Usage | TEXT | | ISO 20022 usage context | No | NULL |
| applicablePaymentTypes | ARRAY<VARCHAR> | | Applicable payment types | No | [] |
| regulatoryRelevance | ARRAY<VARCHAR> | | Regulatory contexts | No | [] |
| isActive | BOOLEAN | Not Null | Active code | Yes | TRUE |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 18: StatusReasonCode

**Purpose**: ISO 20022 status reason codes

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| statusReasonCode | VARCHAR(4) | PK | Status reason code | Yes | NULL |
| statusReasonName | VARCHAR(200) | | Reason name | Yes | NULL |
| statusReasonDescription | TEXT | | Detailed description | No | NULL |
| statusCategory | ENUM('pending','rejection','return','cancellation','amendment','other') | | Category | No | NULL |
| severity | ENUM('info','warning','error','critical') | | Severity level | No | NULL |
| applicableSchemes | ARRAY<VARCHAR> | | Applicable payment schemes | No | [] |
| requiresAction | BOOLEAN | | Requires action | No | NULL |
| customerFacing | BOOLEAN | | Show to customer | No | TRUE |
| isActive | BOOLEAN | Not Null | Active code | Yes | TRUE |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 19: ChargeType

**Purpose**: Charge/fee type reference data

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| chargeTypeCode | VARCHAR(10) | PK | Charge type code | Yes | NULL |
| chargeTypeName | VARCHAR(200) | | Charge type name | Yes | NULL |
| chargeTypeDescription | TEXT | | Description | No | NULL |
| chargeCategory | ENUM('transaction','service','regulatory','penalty','fx','other') | | Charge category | No | NULL |
| applicablePaymentTypes | ARRAY<VARCHAR> | | Applicable payment types | No | [] |
| defaultChargeBearer | ENUM('DEBT','CRED','SHAR','SLEV') | | Default charge bearer | No | NULL |
| calculationMethod | ENUM('fixed','percentage','tiered','custom') | | Calculation method | No | NULL |
| taxable | BOOLEAN | | Subject to tax | No | NULL |
| glAccountDefault | VARCHAR(50) | | Default GL account | No | NULL |
| revenueType | VARCHAR(50) | | Revenue classification | No | NULL |
| isActive | BOOLEAN | Not Null | Active charge type | Yes | TRUE |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 20: SchemeCode

**Purpose**: Payment scheme reference data

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| schemeCode | VARCHAR(50) | PK | Scheme code | Yes | NULL |
| schemeName | VARCHAR(200) | | Scheme name | Yes | NULL |
| schemeDescription | TEXT | | Description | No | NULL |
| schemeType | ENUM('domestic_ach','international_wire','card','instant','sepa','swift','other') | | Scheme type | No | NULL |
| operator | VARCHAR(200) | | Scheme operator | No | NULL |
| country | CHAR(2) | | Primary country | No | NULL |
| region | VARCHAR(50) | | Operating region | No | NULL |
| supportedCurrencies | ARRAY<CHAR(3)> | | Supported currencies | No | [] |
| clearingSystem | VARCHAR(50) | FK to ClearingSystem | Associated clearing system | No | NULL |
| iso20022Compliant | BOOLEAN | | ISO 20022 support | No | NULL |
| messageStandard | VARCHAR(50) | | Message standard | No | NULL |
| maxTransactionAmount | DECIMAL(18,2) | | Maximum transaction | No | NULL |
| minTransactionAmount | DECIMAL(18,2) | | Minimum transaction | No | NULL |
| settlementSpeed | ENUM('real_time','same_day','next_day','T+2','T+3') | | Settlement speed | No | NULL |
| operatingHours | VARCHAR(100) | | Operating hours | No | NULL |
| isActive | BOOLEAN | Not Null | Active scheme | Yes | TRUE |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 21: PaymentType

**Purpose**: Payment product type classification

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| paymentTypeCode | VARCHAR(50) | PK | Payment type code | Yes | NULL |
| paymentTypeName | VARCHAR(200) | | Payment type name | Yes | NULL |
| paymentTypeDescription | TEXT | | Description | No | NULL |
| paymentCategory | ENUM('credit_transfer','direct_debit','card','check','cash','securities','fx','other') | | Payment category | No | NULL |
| domesticOrCrossBorder | ENUM('domestic','cross_border','both') | | Domestic/cross-border | No | NULL |
| schemeCode | VARCHAR(50) | FK to SchemeCode | Associated scheme | No | NULL |
| clearingSystem | VARCHAR(50) | FK to ClearingSystem | Clearing system | No | NULL |
| typicalUseCase | TEXT | | Typical use case | No | NULL |
| targetCustomerSegment | ARRAY<VARCHAR> | | Target segments | No | [] |
| supportedCurrencies | ARRAY<CHAR(3)> | | Supported currencies | No | [] |
| requiredDataElements | ARRAY<VARCHAR> | | Required data elements | No | [] |
| optionalDataElements | ARRAY<VARCHAR> | | Optional data elements | No | [] |
| regulatoryClassification | VARCHAR(100) | | Regulatory classification | No | NULL |
| sanctionsScreeningRequired | BOOLEAN | | Sanctions screening required | No | TRUE |
| fraudScreeningRequired | BOOLEAN | | Fraud screening required | No | TRUE |
| isActive | BOOLEAN | Not Null | Active payment type | Yes | TRUE |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 22: RegulatoryReportType

**Purpose**: Regulatory report type reference data

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| reportTypeCode | VARCHAR(50) | PK | Report type code | Yes | NULL |
| reportTypeName | VARCHAR(200) | | Report type name | Yes | NULL |
| reportTypeDescription | TEXT | | Description | No | NULL |
| regulatoryAuthority | VARCHAR(200) | | Regulatory authority | No | NULL |
| jurisdiction | CHAR(2) | | Jurisdiction | No | NULL |
| reportFrequency | ENUM('real_time','daily','weekly','monthly','quarterly','annual','ad_hoc') | | Frequency | No | NULL |
| filingDeadline | VARCHAR(100) | | Filing deadline | No | NULL |
| penaltyForNonCompliance | TEXT | | Penalties | No | NULL |
| requiredDataElements | ARRAY<VARCHAR> | | Required data | No | [] |
| reportFormat | VARCHAR(50) | | Report format | No | NULL |
| submissionMethod | VARCHAR(100) | | Submission method | No | NULL |
| thresholdAmount | DECIMAL(18,2) | | Threshold amount | No | NULL |
| applicablePaymentTypes | ARRAY<VARCHAR> | | Applicable payment types | No | [] |
| isActive | BOOLEAN | Not Null | Active report type | Yes | TRUE |
| effectiveFrom | DATE | Not Null | Effective start date | Yes | NULL |
| effectiveTo | DATE | | Effective end date | No | NULL |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

## COMPLIANCE AND REGULATORY ENTITIES

### Entity 23: ScreeningResult

**Purpose**: Sanctions and watchlist screening results

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| screeningResultId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction | Related payment | No | NULL |
| partyId | UUID | FK to Party | Screened party | No | NULL |
| screeningType | ENUM('sanctions','pep','adverse_media','watchlist','internal_blacklist') | | Screening type | Yes | NULL |
| screeningTimestamp | TIMESTAMP | Not Null | Screening timestamp | Yes | CURRENT_TIMESTAMP |
| screeningSystem | VARCHAR(100) | | Screening system/vendor | No | NULL |
| screeningVersion | VARCHAR(50) | | System version | No | NULL |
| screeningResult | ENUM('clear','potential_match','confirmed_match','false_positive','pending_review') | Not Null | Result | Yes | NULL |
| matchScore | DECIMAL(5,2) | 0-100 | Match confidence score | No | NULL |
| matchedListName | VARCHAR(200) | | Matched list name | No | NULL |
| matchedListType | ENUM('OFAC_SDN','UN_1267','EU_sanctions','UK_sanctions','FATF','PEP','other') | | List type | No | NULL |
| matchedEntityName | VARCHAR(200) | | Matched entity name | No | NULL |
| matchedEntityId | VARCHAR(100) | | Matched entity ID on list | No | NULL |
| matchedFields | ARRAY<VARCHAR> | | Fields that matched | No | [] |
| matchReason | TEXT | | Reason for match | No | NULL |
| falsePositiveReason | TEXT | | Why determined false positive | No | NULL |
| reviewedBy | VARCHAR(100) | | Reviewer | No | NULL |
| reviewTimestamp | TIMESTAMP | | Review timestamp | No | NULL |
| reviewDecision | ENUM('clear','escalate','block','reject') | | Review decision | No | NULL |
| reviewNotes | TEXT | | Review notes | No | NULL |
| escalationLevel | INTEGER | | Escalation level | No | NULL |
| escalatedTo | VARCHAR(100) | | Escalated to | No | NULL |
| escalationTimestamp | TIMESTAMP | | Escalation timestamp | No | NULL |
| blockedTransaction | BOOLEAN | Not Null | Transaction blocked | No | FALSE |
| rejectedTransaction | BOOLEAN | Not Null | Transaction rejected | No | FALSE |
| ofacReported | BOOLEAN | Not Null | Reported to OFAC | No | FALSE |
| ofacReportTimestamp | TIMESTAMP | | OFAC report timestamp | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 24: ComplianceCase

**Purpose**: Compliance investigation case management

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| complianceCaseId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| caseNumber | VARCHAR(50) | Unique | Case reference number | Yes | NULL |
| caseType | ENUM('aml_investigation','sanctions_review','fraud_investigation','kyc_review','edd_review','sar_filing','ctr_filing','other') | | Case type | Yes | NULL |
| caseStatus | ENUM('open','in_progress','pending_information','escalated','resolved','closed','referred_to_authorities') | Not Null | Case status | Yes | 'open' |
| casePriority | ENUM('low','medium','high','critical') | | Case priority | No | 'medium' |
| caseOpenedDate | DATE | Not Null | Case opened date | Yes | CURRENT_DATE |
| caseOpenedBy | VARCHAR(100) | | Who opened case | No | NULL |
| caseOwner | VARCHAR(100) | | Case owner | No | NULL |
| caseTeam | VARCHAR(100) | | Assigned team | No | NULL |
| relatedPayments | ARRAY<UUID> | FK to PaymentInstruction | Related payments | No | [] |
| relatedParties | ARRAY<UUID> | FK to Party | Related parties | No | [] |
| relatedAccounts | ARRAY<UUID> | FK to Account | Related accounts | No | [] |
| triggerEvent | TEXT | | Event that triggered case | No | NULL |
| alertSource | VARCHAR(100) | | Source of alert | No | NULL |
| riskRating | ENUM('low','medium','high','very_high') | | Case risk rating | No | NULL |
| totalExposure | DECIMAL(18,2) | | Total financial exposure | No | NULL |
| transactionCount | INTEGER | | Number of transactions | No | NULL |
| caseSummary | TEXT | | Case summary | No | NULL |
| investigationFindings | TEXT | | Investigation findings | No | NULL |
| evidenceCollected | ARRAY<VARCHAR> | | Evidence collected (doc IDs) | No | [] |
| interviewsConducted | INTEGER | | Number of interviews | No | NULL |
| externalPartiesContacted | ARRAY<VARCHAR> | | External parties contacted | No | [] |
| regulatoryFilingRequired | BOOLEAN | Not Null | Regulatory filing required | No | FALSE |
| sarFiled | BOOLEAN | Not Null | SAR filed | No | FALSE |
| sarFilingDate | DATE | | SAR filing date | No | NULL |
| sarReferenceNumber | VARCHAR(50) | | SAR reference number | No | NULL |
| ctrFiled | BOOLEAN | Not Null | CTR filed | No | FALSE |
| ctrFilingDate | DATE | | CTR filing date | No | NULL |
| ctrReferenceNumber | VARCHAR(50) | | CTR reference number | No | NULL |
| lawEnforcementReferred | BOOLEAN | Not Null | Referred to law enforcement | No | FALSE |
| referralDate | DATE | | Referral date | No | NULL |
| referralAuthority | VARCHAR(200) | | Authority referred to | No | NULL |
| caseResolutionDate | DATE | | Resolution date | No | NULL |
| caseResolution | TEXT | | Resolution details | No | NULL |
| actionsTaken | ARRAY<VARCHAR> | | Actions taken | No | [] |
| caseClosedDate | DATE | | Case closed date | No | NULL |
| caseClosedBy | VARCHAR(100) | | Who closed case | No | NULL |
| caseNotes | TEXT | | Case notes | No | NULL |
| sarNarrative | TEXT | Max 71,600 chars | Detailed SAR narrative | No | NULL |
| sarActivityTypeCheckboxes | ARRAY<VARCHAR> | | Selected activity types | No | [] |
| lawEnforcementContactDate | DATE | | Date law enforcement was contacted | No | NULL |
| lawEnforcementContactName | VARCHAR(140) | | Law enforcement contact name | No | NULL |
| lawEnforcementAgency | VARCHAR(200) | | Law enforcement agency name | No | NULL |
| recoveredAmount | DECIMAL(18,2) | | Amount recovered from fraud/loss | No | NULL |
| suspectFledIndicator | BOOLEAN | | Suspect has fled jurisdiction | No | FALSE |
| suspectArrestDate | DATE | | Date suspect was arrested | No | NULL |
| suspectConvictionDate | DATE | | Date of conviction | No | NULL |
| investigationStatus | ENUM('open','under_investigation','closed','referred_to_law_enforcement','prosecuted') | | Investigation status | No | 'open' |
| referralToFIU | BOOLEAN | | Referred to Financial Intelligence Unit | No | FALSE |
| fiuReferralDate | DATE | | Date referred to FIU | No | NULL |
| fiuReferenceNumber | VARCHAR(100) | | FIU reference number | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

**Regulatory Reporting Notes:**
- `sarNarrative`: Required for FinCEN SAR Item 104 (Detailed narrative, max 71,600 characters)
- `sarActivityTypeCheckboxes`: Required for FinCEN SAR Items 52-68 (17 suspicious activity type checkboxes)
- `lawEnforcementContactDate`, `lawEnforcementContactName`, `lawEnforcementAgency`: Required for FinCEN SAR Item 92
- `suspectFledIndicator`: Required for FinCEN SAR Item 51
- `investigationStatus`: Internal case management for SAR follow-up
- `referralToFIU`: Required for global AML/CTF reporting (AUSTRAC, EBA, etc.)

---

### Entity 25: RegulatoryReport

**Purpose**: Regulatory report filings and submissions

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| regulatoryReportId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| reportType | VARCHAR(50) | FK to RegulatoryReportType | Report type | Yes | NULL |
| reportReferenceNumber | VARCHAR(100) | Unique | Report reference number | Yes | NULL |
| reportingPeriodStart | DATE | | Reporting period start | No | NULL |
| reportingPeriodEnd | DATE | | Reporting period end | No | NULL |
| reportingEntity | VARCHAR(200) | | Reporting legal entity | Yes | NULL |
| reportingEntityId | VARCHAR(100) | | Entity identifier (LEI, etc.) | No | NULL |
| regulatoryAuthority | VARCHAR(200) | | Reporting authority | Yes | NULL |
| jurisdiction | CHAR(2) | | Jurisdiction | Yes | NULL |
| reportStatus | ENUM('draft','pending_review','approved','submitted','accepted','rejected','amended') | Not Null | Report status | Yes | 'draft' |
| dueDate | DATE | | Report due date | No | NULL |
| submissionDate | DATE | | Actual submission date | No | NULL |
| submittedBy | VARCHAR(100) | | Who submitted | No | NULL |
| submissionMethod | VARCHAR(100) | | Submission method | No | NULL |
| confirmationNumber | VARCHAR(100) | | Submission confirmation | No | NULL |
| includedTransactions | ARRAY<UUID> | FK to PaymentInstruction | Included transactions | No | [] |
| transactionCount | INTEGER | >= 0 | Transaction count | No | 0 |
| totalReportedValue | DECIMAL(18,2) | | Total reported value | No | NULL |
| reportingCurrency | CHAR(3) | | Reporting currency | No | NULL |
| reportContent | TEXT | | Report content | No | NULL |
| reportFormat | VARCHAR(50) | | Report format (XML, CSV, PDF) | No | NULL |
| reportFilePath | VARCHAR(500) | | File path/URL | No | NULL |
| validationErrors | ARRAY<VARCHAR> | | Validation errors | No | [] |
| rejectionReason | TEXT | | Rejection reason (if rejected) | No | NULL |
| amendmentReason | TEXT | | Amendment reason | No | NULL |
| originalReportId | UUID | FK to RegulatoryReport | Original report (if amendment) | No | NULL |
| approvedBy | VARCHAR(100) | | Approver | No | NULL |
| approvalTimestamp | TIMESTAMP | | Approval timestamp | No | NULL |
| reportingEntityABN | VARCHAR(11) | | Australian Business Number | No | NULL |
| reportingEntityBranch | VARCHAR(100) | | Branch name/identifier | No | NULL |
| reportingEntityContactName | VARCHAR(140) | | Contact person name | No | NULL |
| reportingEntityContactPhone | VARCHAR(25) | | Contact phone number | No | NULL |
| filingType | ENUM('initial','amendment','correction','late') | | Type of filing | No | 'initial' |
| priorReportBSAID | VARCHAR(50) | | Prior report BSA identifier (for amendments) | No | NULL |
| reportingPeriodType | ENUM('single_transaction','aggregated','periodic') | | Type of reporting period | No | 'single_transaction' |
| totalCashIn | DECIMAL(18,2) | | Total cash received (CTR-specific) | No | NULL |
| totalCashOut | DECIMAL(18,2) | | Total cash disbursed (CTR-specific) | No | NULL |
| foreignCashIn | ARRAY<STRUCT{country:CHAR(2), currency:CHAR(3), amount:DECIMAL(18,2)}> | | Foreign cash received by country | No | [] |
| foreignCashOut | ARRAY<STRUCT{country:CHAR(2), currency:CHAR(3), amount:DECIMAL(18,2)}> | | Foreign cash disbursed by country | No | [] |
| multiplePersonsFlag | BOOLEAN | | Multiple persons involved in transaction | No | FALSE |
| aggregationMethod | VARCHAR(100) | | How transactions were aggregated | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

**Regulatory Reporting Notes:**
- `reportingEntityABN`: Required for AUSTRAC IFTI-E Field 1.1
- `reportingEntityBranch`: Required for AUSTRAC IFTI-E Field 1.3
- `reportingEntityContactName`, `reportingEntityContactPhone`: Required for AUSTRAC IFTI-E Fields 1.4-1.5, FinCEN SAR Part IV
- `filingType`: Required for AUSTRAC IFTI-E Field 1.10, FinCEN CTR Item 1
- `priorReportBSAID`: Required for FinCEN CTR Item 2, SAR Item 3 (amendments)
- `totalCashIn`, `totalCashOut`: Required for FinCEN CTR Part II aggregation
- `foreignCashIn`, `foreignCashOut`: Required for FinCEN CTR Items 62-66, 68-72
- `multiplePersonsFlag`: Required for FinCEN CTR Item 3

---

### Entity 26: SanctionsList

**Purpose**: Sanctions list reference data (OFAC, UN, EU, etc.)

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| sanctionsListId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| listName | VARCHAR(200) | Not Null | List name | Yes | NULL |
| listCode | VARCHAR(50) | | List code | No | NULL |
| issuingAuthority | VARCHAR(200) | | Issuing authority | Yes | NULL |
| jurisdiction | CHAR(2) | | Jurisdiction | No | NULL |
| listType | ENUM('comprehensive_sanctions','targeted_sanctions','sectoral_sanctions','secondary_sanctions') | | List type | Yes | NULL |
| listCategory | ENUM('SDN','SSI','non_SDN','EU_sanctions','UN_1267','UK_sanctions','OFSI','other') | | List category | No | NULL |
| entityName | VARCHAR(200) | Not Null | Entity name | Yes | NULL |
| entityType | ENUM('individual','organization','vessel','aircraft','other') | | Entity type | No | NULL |
| aliases | ARRAY<VARCHAR(200)> | | Known aliases | No | [] |
| dateOfBirth | DATE | | Date of birth (individuals) | No | NULL |
| placeOfBirth | VARCHAR(200) | | Place of birth | No | NULL |
| nationality | ARRAY<CHAR(2)> | | Nationalities | No | [] |
| passportNumbers | ARRAY<VARCHAR(50)> | | Passport numbers | No | [] |
| nationalIdNumbers | ARRAY<VARCHAR(50)> | | National ID numbers | No | [] |
| taxIdNumbers | ARRAY<VARCHAR(50)> | | Tax IDs | No | [] |
| addresses | ARRAY<STRUCT> | See Address structure | Known addresses | No | [] |
| sanctionsProgram | VARCHAR(200) | | Sanctions program | No | NULL |
| sanctionsReason | TEXT | | Reason for sanctions | No | NULL |
| addedToListDate | DATE | | Date added to list | No | NULL |
| removedFromListDate | DATE | | Date removed (if applicable) | No | NULL |
| isActive | BOOLEAN | Not Null | Active on list | Yes | TRUE |
| listUpdateDate | DATE | | Last list update | No | NULL |
| remarks | TEXT | | Additional remarks | No | NULL |
| relatedEntities | ARRAY<UUID> | | Related sanctioned entities | No | [] |
| sourceURL | VARCHAR(500) | | Source URL | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 27: AMLAlert

**Purpose**: AML alert/suspicious activity tracking

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| amlAlertId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| alertNumber | VARCHAR(50) | Unique | Alert reference number | Yes | NULL |
| alertType | ENUM('transaction_monitoring','behavior_analysis','threshold_breach','structuring','rapid_movement','high_risk_country','pep_transaction','watchlist_hit','other') | | Alert type | Yes | NULL |
| alertStatus | ENUM('new','under_review','escalated','false_positive','confirmed_suspicious','sar_filed','closed') | Not Null | Alert status | Yes | 'new' |
| alertPriority | ENUM('low','medium','high','critical') | | Alert priority | No | 'medium' |
| alertGeneratedTimestamp | TIMESTAMP | Not Null | Alert generation timestamp | Yes | CURRENT_TIMESTAMP |
| alertSource | VARCHAR(100) | | Alert source system | No | NULL |
| detectionScenario | VARCHAR(200) | | Detection scenario/rule | No | NULL |
| scenarioVersion | VARCHAR(50) | | Scenario version | No | NULL |
| riskScore | DECIMAL(5,2) | 0-100 | Risk score | No | NULL |
| paymentId | UUID | FK to PaymentInstruction | Related payment | No | NULL |
| partyId | UUID | FK to Party | Related party | No | NULL |
| accountId | UUID | FK to Account | Related account | No | NULL |
| relatedTransactions | ARRAY<UUID> | | Related transactions | No | [] |
| transactionCount | INTEGER | | Number of transactions | No | NULL |
| totalAmount | DECIMAL(18,2) | | Total amount | No | NULL |
| timeWindow | VARCHAR(100) | | Time window analyzed | No | NULL |
| alertReason | TEXT | | Alert reason | No | NULL |
| suspiciousIndicators | ARRAY<VARCHAR> | | Suspicious indicators | No | [] |
| assignedTo | VARCHAR(100) | | Alert owner | No | NULL |
| assignedTeam | VARCHAR(100) | | Assigned team | No | NULL |
| reviewStartedTimestamp | TIMESTAMP | | Review started timestamp | No | NULL |
| reviewedBy | VARCHAR(100) | | Reviewer | No | NULL |
| reviewNotes | TEXT | | Review notes | No | NULL |
| investigationRequired | BOOLEAN | Not Null | Investigation required | No | FALSE |
| complianceCaseId | UUID | FK to ComplianceCase | Related case | No | NULL |
| disposition | ENUM('false_positive','true_positive','escalated','pending') | | Alert disposition | No | NULL |
| dispositionReason | TEXT | | Disposition reason | No | NULL |
| dispositionTimestamp | TIMESTAMP | | Disposition timestamp | No | NULL |
| sarRequired | BOOLEAN | Not Null | SAR required | No | FALSE |
| sarFiled | BOOLEAN | Not Null | SAR filed | No | FALSE |
| sarReferenceNumber | VARCHAR(50) | | SAR reference | No | NULL |
| closedTimestamp | TIMESTAMP | | Alert closed timestamp | No | NULL |
| closedBy | VARCHAR(100) | | Who closed alert | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

## OPERATIONAL ENTITIES

### Entity 28: PaymentException

**Purpose**: Payment processing exceptions and errors

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| exceptionId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Related payment | Yes | NULL |
| exceptionType | ENUM('validation_error','format_error','routing_error','enrichment_failure','screening_failure','system_error','timeout','connectivity_issue','data_quality','other') | | Exception type | Yes | NULL |
| exceptionCategory | ENUM('technical','business','data','external') | | Exception category | No | NULL |
| exceptionStatus | ENUM('new','acknowledged','in_progress','resolved','escalated','closed') | Not Null | Exception status | Yes | 'new' |
| severity | ENUM('info','warning','error','critical') | Not Null | Severity level | Yes | 'error' |
| exceptionTimestamp | TIMESTAMP | Not Null | When exception occurred | Yes | CURRENT_TIMESTAMP |
| exceptionSource | VARCHAR(100) | | Source system/component | No | NULL |
| processingStage | VARCHAR(100) | | Processing stage when exception occurred | No | NULL |
| errorCode | VARCHAR(20) | | Error code | No | NULL |
| errorMessage | TEXT | | Error message | No | NULL |
| errorDetails | JSON | | Detailed error information | No | {} |
| stackTrace | TEXT | | Stack trace (technical errors) | No | NULL |
| validationFailures | ARRAY<VARCHAR> | | List of validation failures | No | [] |
| affectedFields | ARRAY<VARCHAR> | | Fields causing exception | No | [] |
| expectedValue | VARCHAR(500) | | Expected value | No | NULL |
| actualValue | VARCHAR(500) | | Actual value received | No | NULL |
| retryable | BOOLEAN | Not Null | Exception can be retried | No | TRUE |
| retryAttempts | INTEGER | >= 0 | Number of retry attempts | No | 0 |
| maxRetries | INTEGER | | Maximum retries allowed | No | 3 |
| lastRetryTimestamp | TIMESTAMP | | Last retry timestamp | No | NULL |
| nextRetryTimestamp | TIMESTAMP | | Next scheduled retry | No | NULL |
| autoResolved | BOOLEAN | Not Null | Automatically resolved | No | FALSE |
| manualInterventionRequired | BOOLEAN | Not Null | Manual intervention required | No | FALSE |
| assignedTo | VARCHAR(100) | | Assigned to user | No | NULL |
| assignedTeam | VARCHAR(100) | | Assigned team | No | NULL |
| resolutionAction | TEXT | | Resolution action taken | No | NULL |
| resolutionTimestamp | TIMESTAMP | | Resolution timestamp | No | NULL |
| resolvedBy | VARCHAR(100) | | Who resolved | No | NULL |
| resolutionNotes | TEXT | | Resolution notes | No | NULL |
| impactAssessment | TEXT | | Impact assessment | No | NULL |
| customerImpact | BOOLEAN | Not Null | Customer impacting | No | FALSE |
| customerNotified | BOOLEAN | Not Null | Customer notified | No | FALSE |
| slaBreached | BOOLEAN | Not Null | SLA breached | No | FALSE |
| escalatedToManagement | BOOLEAN | Not Null | Escalated to management | No | FALSE |
| relatedExceptions | ARRAY<UUID> | FK to PaymentException | Related exceptions | No | [] |
| rootCauseException | UUID | FK to PaymentException | Root cause exception | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 29: ManualIntervention

**Purpose**: Manual intervention and approval workflow tracking

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| interventionId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction, Not Null | Related payment | Yes | NULL |
| interventionType | ENUM('approval_required','exception_handling','compliance_review','fraud_review','data_correction','investigation','escalation','other') | | Intervention type | Yes | NULL |
| interventionReason | TEXT | | Reason for intervention | No | NULL |
| interventionStatus | ENUM('pending','in_progress','approved','rejected','cancelled','on_hold') | Not Null | Status | Yes | 'pending' |
| priority | ENUM('low','medium','high','critical') | | Priority | No | 'medium' |
| requestedTimestamp | TIMESTAMP | Not Null | Intervention requested timestamp | Yes | CURRENT_TIMESTAMP |
| requestedBy | VARCHAR(100) | | Who requested intervention | No | NULL |
| requestingSystem | VARCHAR(100) | | Requesting system | No | NULL |
| assignedTo | VARCHAR(100) | | Assigned to user | No | NULL |
| assignedTeam | VARCHAR(100) | | Assigned team | No | NULL |
| assignmentTimestamp | TIMESTAMP | | Assignment timestamp | No | NULL |
| dueTimestamp | TIMESTAMP | | Due timestamp | No | NULL |
| approvalLevel | INTEGER | | Required approval level | No | NULL |
| approvalChain | ARRAY<VARCHAR> | | Approval chain | No | [] |
| currentApprover | VARCHAR(100) | | Current approver | No | NULL |
| approvalHistory | ARRAY<STRUCT{approver:VARCHAR, decision:ENUM, timestamp:TIMESTAMP, comments:TEXT}> | | Approval history | No | [] |
| decision | ENUM('approved','rejected','cancelled','escalated') | | Final decision | No | NULL |
| decisionTimestamp | TIMESTAMP | | Decision timestamp | No | NULL |
| decisionBy | VARCHAR(100) | | Who made decision | No | NULL |
| decisionReason | TEXT | | Decision reason | No | NULL |
| comments | TEXT | | Comments | No | NULL |
| attachments | ARRAY<VARCHAR> | | Attachment document IDs | No | [] |
| fieldsToCorrect | ARRAY<VARCHAR> | | Fields requiring correction | No | [] |
| correctedValues | JSON | | Corrected values | No | {} |
| originalValues | JSON | | Original values | No | {} |
| slaTarget | INTEGER | In minutes | SLA target (minutes) | No | NULL |
| slaStatus | ENUM('on_track','at_risk','breached') | | SLA status | No | NULL |
| timeSpentMinutes | INTEGER | | Time spent on intervention | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 30: AuditTrail

**Purpose**: Complete audit trail of all changes to payment records

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| auditId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| entityType | ENUM('PaymentInstruction','Party','Account','FinancialInstitution','Settlement','Charge','other') | | Entity type | Yes | NULL |
| entityId | UUID | Not Null | Entity identifier | Yes | NULL |
| auditAction | ENUM('create','update','delete','soft_delete','undelete','approve','reject','cancel') | Not Null | Action performed | Yes | NULL |
| auditTimestamp | TIMESTAMP | Not Null | Action timestamp | Yes | CURRENT_TIMESTAMP |
| auditUser | VARCHAR(100) | | User who performed action | No | NULL |
| auditSystem | VARCHAR(100) | | System that performed action | No | NULL |
| auditSource | VARCHAR(100) | | Source of change | No | NULL |
| changedFields | ARRAY<VARCHAR> | | Fields that changed | No | [] |
| oldValues | JSON | | Old field values | No | {} |
| newValues | JSON | | New field values | No | {} |
| changeReason | TEXT | | Reason for change | No | NULL |
| approvalRequired | BOOLEAN | | Change required approval | No | NULL |
| approvedBy | VARCHAR(100) | | Who approved change | No | NULL |
| approvalTimestamp | TIMESTAMP | | Approval timestamp | No | NULL |
| ipAddress | VARCHAR(45) | | IP address of change origin | No | NULL |
| userAgent | VARCHAR(500) | | User agent string | No | NULL |
| sessionId | VARCHAR(100) | | Session identifier | No | NULL |
| transactionId | VARCHAR(100) | | Transaction identifier | No | NULL |
| correlationId | VARCHAR(100) | | Correlation identifier | No | NULL |
| recordVersion | INTEGER | | Record version after change | No | NULL |
| dataClassification | ENUM('public','internal','confidential','restricted','pii','pci') | | Data classification | No | NULL |
| retentionPeriod | INTEGER | In days | Audit retention period | No | 2555 |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 31: DataQualityIssue

**Purpose**: Data quality issue tracking and resolution

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| dataQualityIssueId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| paymentId | UUID | FK to PaymentInstruction | Related payment | No | NULL |
| partyId | UUID | FK to Party | Related party | No | NULL |
| accountId | UUID | FK to Account | Related account | No | NULL |
| entityType | VARCHAR(100) | | Entity type with issue | No | NULL |
| entityId | UUID | | Entity identifier | No | NULL |
| issueType | ENUM('completeness','validity','consistency','accuracy','timeliness','uniqueness','conformity') | | DQ dimension | Yes | NULL |
| issueCategory | ENUM('missing_required_field','invalid_format','out_of_range','inconsistent_data','duplicate','stale_data','truncated_data','encoding_issue','other') | | Issue category | Yes | NULL |
| issueSeverity | ENUM('low','medium','high','critical') | Not Null | Severity | Yes | 'medium' |
| issueStatus | ENUM('open','acknowledged','in_remediation','resolved','accepted_exception','closed') | Not Null | Status | Yes | 'open' |
| detectedTimestamp | TIMESTAMP | Not Null | When issue detected | Yes | CURRENT_TIMESTAMP |
| detectedBy | VARCHAR(100) | | Detection source/system | No | NULL |
| detectionRule | VARCHAR(200) | | DQ rule that detected issue | No | NULL |
| ruleVersion | VARCHAR(50) | | Rule version | No | NULL |
| affectedField | VARCHAR(200) | | Field with issue | No | NULL |
| currentValue | VARCHAR(1000) | | Current (problematic) value | No | NULL |
| expectedValue | VARCHAR(1000) | | Expected value | No | NULL |
| validationRule | TEXT | | Validation rule violated | No | NULL |
| issueDescription | TEXT | | Issue description | No | NULL |
| dataQualityScore | DECIMAL(5,2) | 0-100 | DQ score for entity | No | NULL |
| businessImpact | TEXT | | Business impact description | No | NULL |
| impactedProcesses | ARRAY<VARCHAR> | | Impacted processes | No | [] |
| assignedTo | VARCHAR(100) | | Assigned to for resolution | No | NULL |
| assignedTeam | VARCHAR(100) | | Assigned team | No | NULL |
| remediationAction | TEXT | | Remediation action | No | NULL |
| remediationTimestamp | TIMESTAMP | | Remediation timestamp | No | NULL |
| remediatedBy | VARCHAR(100) | | Who remediated | No | NULL |
| correctedValue | VARCHAR(1000) | | Corrected value | No | NULL |
| resolutionNotes | TEXT | | Resolution notes | No | NULL |
| recurrence | BOOLEAN | Not Null | Recurring issue | No | FALSE |
| recurrenceCount | INTEGER | | Number of recurrences | No | NULL |
| rootCause | TEXT | | Root cause analysis | No | NULL |
| preventionMeasures | TEXT | | Prevention measures taken | No | NULL |
| exceptionApproved | BOOLEAN | Not Null | Accepted as exception | No | FALSE |
| exceptionApprovedBy | VARCHAR(100) | | Who approved exception | No | NULL |
| exceptionReason | TEXT | | Exception reason | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 32: ReconciliationRecord

**Purpose**: Reconciliation tracking for payment processing

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| reconciliationId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| reconciliationType | ENUM('source_to_cdm','settlement_reconciliation','nostro_reconciliation','gl_reconciliation','cross_system','position_reconciliation') | | Reconciliation type | Yes | NULL |
| reconciliationDate | DATE | Not Null | Reconciliation date | Yes | CURRENT_DATE |
| reconciliationPeriod | VARCHAR(50) | | Period (daily, monthly, etc.) | No | NULL |
| sourceSystem | VARCHAR(100) | | Source system | No | NULL |
| targetSystem | VARCHAR(100) | | Target system | No | NULL |
| reconciliationStatus | ENUM('in_progress','matched','unmatched','partially_matched','exception','resolved') | Not Null | Status | Yes | 'in_progress' |
| paymentId | UUID | FK to PaymentInstruction | Related payment | No | NULL |
| sourceRecordId | VARCHAR(200) | | Source record identifier | No | NULL |
| targetRecordId | VARCHAR(200) | | Target record identifier | No | NULL |
| sourceAmount | DECIMAL(18,2) | | Source amount | No | NULL |
| targetAmount | DECIMAL(18,2) | | Target amount | No | NULL |
| amountDifference | DECIMAL(18,2) | | Amount difference | No | NULL |
| currency | CHAR(3) | | Currency | No | NULL |
| sourceValueDate | DATE | | Source value date | No | NULL |
| targetValueDate | DATE | | Target value date | No | NULL |
| sourceRecordCount | INTEGER | | Source record count | No | NULL |
| targetRecordCount | INTEGER | | Target record count | No | NULL |
| matchedRecordCount | INTEGER | | Matched record count | No | NULL |
| unmatchedSourceCount | INTEGER | | Unmatched source records | No | NULL |
| unmatchedTargetCount | INTEGER | | Unmatched target records | No | NULL |
| matchCriteria | ARRAY<VARCHAR> | | Match criteria used | No | [] |
| matchScore | DECIMAL(5,2) | 0-100 | Match confidence | No | NULL |
| reconciliationMethod | ENUM('exact_match','fuzzy_match','rule_based','manual') | | Reconciliation method | No | NULL |
| discrepancyType | ENUM('missing_in_source','missing_in_target','amount_mismatch','date_mismatch','status_mismatch','other') | | Discrepancy type | No | NULL |
| discrepancyDetails | TEXT | | Discrepancy details | No | NULL |
| discrepancyReason | TEXT | | Reason for discrepancy | No | NULL |
| resolutionRequired | BOOLEAN | Not Null | Resolution required | No | FALSE |
| resolutionAction | TEXT | | Resolution action | No | NULL |
| resolvedTimestamp | TIMESTAMP | | Resolution timestamp | No | NULL |
| resolvedBy | VARCHAR(100) | | Who resolved | No | NULL |
| resolutionNotes | TEXT | | Resolution notes | No | NULL |
| autoReconciled | BOOLEAN | Not Null | Automatically reconciled | No | TRUE |
| manualReviewRequired | BOOLEAN | Not Null | Manual review required | No | FALSE |
| reviewedBy | VARCHAR(100) | | Reviewer | No | NULL |
| reviewTimestamp | TIMESTAMP | | Review timestamp | No | NULL |
| glImpact | DECIMAL(18,2) | | GL impact amount | No | NULL |
| glAdjustmentRequired | BOOLEAN | Not Null | GL adjustment required | No | FALSE |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

## ANALYTICS ENTITIES

### Entity 33: PaymentMetrics

**Purpose**: Aggregated payment metrics and KPIs

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| metricsId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| metricsDate | DATE | Not Null | Metrics date | Yes | NULL |
| metricsTimestamp | TIMESTAMP | Not Null | Metrics timestamp | Yes | CURRENT_TIMESTAMP |
| aggregationLevel | ENUM('payment_type','region','currency','customer_segment','product','channel','daily','monthly','yearly') | | Aggregation level | Yes | NULL |
| aggregationKey | VARCHAR(200) | | Aggregation key value | No | NULL |
| paymentType | VARCHAR(50) | | Payment type | No | NULL |
| region | VARCHAR(50) | | Region | No | NULL |
| currency | CHAR(3) | | Currency | No | NULL |
| customerSegment | VARCHAR(50) | | Customer segment | No | NULL |
| totalPaymentCount | BIGINT | >= 0 | Total payment count | No | 0 |
| totalPaymentValue | DECIMAL(18,2) | >= 0 | Total payment value | No | 0 |
| averagePaymentValue | DECIMAL(18,2) | >= 0 | Average payment value | No | 0 |
| medianPaymentValue | DECIMAL(18,2) | | Median payment value | No | NULL |
| minPaymentValue | DECIMAL(18,2) | | Minimum payment value | No | NULL |
| maxPaymentValue | DECIMAL(18,2) | | Maximum payment value | No | NULL |
| successfulPaymentCount | BIGINT | >= 0 | Successful payments | No | 0 |
| failedPaymentCount | BIGINT | >= 0 | Failed payments | No | 0 |
| cancelledPaymentCount | BIGINT | >= 0 | Cancelled payments | No | 0 |
| returnedPaymentCount | BIGINT | >= 0 | Returned payments | No | 0 |
| successRate | DECIMAL(5,2) | 0-100 | Success rate percentage | No | NULL |
| failureRate | DECIMAL(5,2) | 0-100 | Failure rate percentage | No | NULL |
| returnRate | DECIMAL(5,2) | 0-100 | Return rate percentage | No | NULL |
| averageProcessingTime | DECIMAL(10,2) | In seconds | Average processing time | No | NULL |
| medianProcessingTime | DECIMAL(10,2) | | Median processing time | No | NULL |
| slaComplianceRate | DECIMAL(5,2) | 0-100 | SLA compliance percentage | No | NULL |
| slaBreachCount | BIGINT | >= 0 | SLA breach count | No | 0 |
| crossBorderPaymentCount | BIGINT | >= 0 | Cross-border payments | No | 0 |
| domesticPaymentCount | BIGINT | >= 0 | Domestic payments | No | 0 |
| highValuePaymentCount | BIGINT | >= 0 | High value payments (>$10K) | No | 0 |
| totalChargesCollected | DECIMAL(18,2) | >= 0 | Total charges collected | No | 0 |
| averageChargeAmount | DECIMAL(18,2) | | Average charge amount | No | NULL |
| sanctionsHitCount | BIGINT | >= 0 | Sanctions hits | No | 0 |
| fraudAlertCount | BIGINT | >= 0 | Fraud alerts | No | 0 |
| amlAlertCount | BIGINT | >= 0 | AML alerts | No | 0 |
| manualInterventionCount | BIGINT | >= 0 | Manual interventions | No | 0 |
| exceptionCount | BIGINT | >= 0 | Exceptions | No | 0 |
| dataQualityScore | DECIMAL(5,2) | 0-100 | Average DQ score | No | NULL |
| uniqueDebtorCount | BIGINT | >= 0 | Unique debtors | No | 0 |
| uniqueCreditorCount | BIGINT | >= 0 | Unique creditors | No | 0 |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 34: CustomerPaymentBehavior

**Purpose**: Customer payment behavior and pattern analysis

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| behaviorId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| partyId | UUID | FK to Party, Not Null | Customer party | Yes | NULL |
| analysisDate | DATE | Not Null | Analysis date | Yes | CURRENT_DATE |
| analysisPeriod | VARCHAR(50) | | Analysis period (30d, 90d, 1y) | No | NULL |
| totalTransactionCount | BIGINT | >= 0 | Total transactions | No | 0 |
| totalTransactionValue | DECIMAL(18,2) | >= 0 | Total transaction value | No | 0 |
| averageTransactionValue | DECIMAL(18,2) | | Average transaction value | No | NULL |
| averageMonthlyVolume | BIGINT | | Average monthly volume | No | NULL |
| averageMonthlyValue | DECIMAL(18,2) | | Average monthly value | No | NULL |
| transactionFrequency | DECIMAL(10,2) | | Transactions per day | No | NULL |
| preferredPaymentTypes | ARRAY<VARCHAR> | | Preferred payment types | No | [] |
| preferredCurrencies | ARRAY<CHAR(3)> | | Preferred currencies | No | [] |
| preferredCounterparties | ARRAY<UUID> | FK to Party | Frequent counterparties | No | [] |
| peakTransactionHour | INTEGER | 0-23 | Peak transaction hour | No | NULL |
| peakTransactionDayOfWeek | INTEGER | 1-7 | Peak day of week | No | NULL |
| crossBorderPercentage | DECIMAL(5,2) | 0-100 | % cross-border | No | NULL |
| highValuePercentage | DECIMAL(5,2) | 0-100 | % high value (>$10K) | No | NULL |
| roundDollarPercentage | DECIMAL(5,2) | 0-100 | % round dollar amounts | No | NULL |
| averageValueDateDelay | DECIMAL(5,2) | In days | Avg value date delay | No | NULL |
| returnRate | DECIMAL(5,2) | 0-100 | Return rate | No | NULL |
| failureRate | DECIMAL(5,2) | 0-100 | Failure rate | No | NULL |
| behaviorScore | DECIMAL(5,2) | 0-100 | Behavior consistency score | No | NULL |
| riskScore | DECIMAL(5,2) | 0-100 | Risk score | No | NULL |
| anomalyCount | INTEGER | >= 0 | Anomaly count in period | No | 0 |
| anomalyTypes | ARRAY<VARCHAR> | | Types of anomalies detected | No | [] |
| seasonalityDetected | BOOLEAN | | Seasonality pattern detected | No | NULL |
| growthTrend | ENUM('increasing','stable','decreasing') | | Transaction growth trend | No | NULL |
| growthRate | DECIMAL(8,2) | | Growth rate percentage | No | NULL |
| dormancyRisk | BOOLEAN | | Dormancy risk indicator | No | FALSE |
| lastTransactionDate | DATE | | Last transaction date | No | NULL |
| daysSinceLastTransaction | INTEGER | >= 0 | Days since last transaction | No | NULL |
| predictedNextTransactionDate | DATE | | Predicted next transaction | No | NULL |
| lifetimeValue | DECIMAL(18,2) | | Lifetime transaction value | No | NULL |
| customerSince | DATE | | Customer relationship start | No | NULL |
| customerTenureDays | INTEGER | >= 0 | Customer tenure (days) | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 35: PaymentFlowAnalysis

**Purpose**: Payment flow and routing analysis

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| flowAnalysisId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| analysisDate | DATE | Not Null | Analysis date | Yes | CURRENT_DATE |
| analysisPeriod | VARCHAR(50) | | Analysis period | No | NULL |
| paymentCorridor | VARCHAR(200) | | Payment corridor (US->UK) | No | NULL |
| sourceCountry | CHAR(2) | | Source country | No | NULL |
| destinationCountry | CHAR(2) | | Destination country | No | NULL |
| paymentType | VARCHAR(50) | | Payment type | No | NULL |
| currency | CHAR(3) | | Currency | No | NULL |
| totalFlowCount | BIGINT | >= 0 | Total flow count | No | 0 |
| totalFlowValue | DECIMAL(18,2) | >= 0 | Total flow value | No | 0 |
| averageFlowValue | DECIMAL(18,2) | | Average flow value | No | NULL |
| commonRoutingPath | ARRAY<VARCHAR> | | Most common routing path | No | [] |
| averageIntermediaryCount | DECIMAL(5,2) | | Average intermediaries | No | NULL |
| averageSettlementTime | DECIMAL(10,2) | In hours | Average settlement time | No | NULL |
| fastestSettlementTime | DECIMAL(10,2) | | Fastest settlement | No | NULL |
| slowestSettlementTime | DECIMAL(10,2) | | Slowest settlement | No | NULL |
| clearingSystems Used | ARRAY<VARCHAR> | | Clearing systems used | No | [] |
| commonCorrespondents | ARRAY<UUID> | FK to FinancialInstitution | Common correspondents | No | [] |
| averageFeeAmount | DECIMAL(18,2) | | Average fee amount | No | NULL |
| feePercentage | DECIMAL(5,2) | | Fee as % of amount | No | NULL |
| flowSuccessRate | DECIMAL(5,2) | 0-100 | Flow success rate | No | NULL |
| flowFailureRate | DECIMAL(5,2) | 0-100 | Flow failure rate | No | NULL |
| commonFailureReasons | ARRAY<VARCHAR> | | Common failure reasons | No | [] |
| peakFlowHour | INTEGER | 0-23 | Peak flow hour | No | NULL |
| averageValueDate | DECIMAL(5,2) | In days | Average value date (T+N) | No | NULL |
| flowConcentrationRisk | DECIMAL(5,2) | 0-100 | Concentration risk score | No | NULL |
| alternativeRoutesAvailable | INTEGER | >= 0 | Alternative routes | No | 0 |
| flowEfficiencyScore | DECIMAL(5,2) | 0-100 | Efficiency score | No | NULL |
| regulatoryComplexity | ENUM('low','medium','high') | | Regulatory complexity | No | NULL |
| sanctionsRiskScore | DECIMAL(5,2) | 0-100 | Sanctions risk | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |

---

### Entity 36: FraudPattern

**Purpose**: Fraud pattern detection and analysis

**Complete Attributes**:

| Attribute Name | Data Type | Constraints | Description | Mandatory | Default |
|----------------|-----------|-------------|-------------|-----------|---------|
| fraudPatternId | UUID | PK, Not Null, Unique | Unique identifier | Yes | UUID v4 |
| patternType | ENUM('account_takeover','synthetic_identity','money_mule','bust_out','authorized_push_fraud','refund_fraud','transaction_laundering','layering','other') | | Pattern type | Yes | NULL |
| detectionDate | DATE | Not Null | Detection date | Yes | CURRENT_DATE |
| detectionTimestamp | TIMESTAMP | Not Null | Detection timestamp | Yes | CURRENT_TIMESTAMP |
| detectionMethod | VARCHAR(200) | | Detection method/algorithm | No | NULL |
| confidenceScore | DECIMAL(5,2) | 0-100 | Detection confidence | No | NULL |
| riskScore | DECIMAL(5,2) | 0-100 | Risk score | No | NULL |
| severity | ENUM('low','medium','high','critical') | | Severity | No | 'medium' |
| patternStatus | ENUM('detected','under_investigation','confirmed','false_positive','closed') | Not Null | Status | Yes | 'detected' |
| affectedPayments | ARRAY<UUID> | FK to PaymentInstruction | Affected payments | No | [] |
| affectedParties | ARRAY<UUID> | FK to Party | Affected parties | No | [] |
| affectedAccounts | ARRAY<UUID> | FK to Account | Affected accounts | No | [] |
| transactionCount | INTEGER | >= 0 | Transaction count | No | NULL |
| totalExposureAmount | DECIMAL(18,2) | | Total exposure | No | NULL |
| timeWindow | VARCHAR(100) | | Time window of pattern | No | NULL |
| patternIndicators | ARRAY<VARCHAR> | | Pattern indicators | No | [] |
| anomalyFeatures | JSON | | Anomaly features detected | No | {} |
| velocityIndicators | JSON | | Velocity indicators | No | {} |
| networkAnalysis | JSON | | Network analysis results | No | {} |
| relatedPatterns | ARRAY<UUID> | FK to FraudPattern | Related patterns | No | [] |
| investigationRequired | BOOLEAN | Not Null | Investigation required | No | TRUE |
| investigationId | VARCHAR(100) | | Investigation case ID | No | NULL |
| investigator | VARCHAR(100) | | Assigned investigator | No | NULL |
| investigationStarted | TIMESTAMP | | Investigation start | No | NULL |
| investigationNotes | TEXT | | Investigation notes | No | NULL |
| confirmedFraud | BOOLEAN | | Confirmed as fraud | No | NULL |
| confirmedTimestamp | TIMESTAMP | | Confirmation timestamp | No | NULL |
| confirmedBy | VARCHAR(100) | | Who confirmed | No | NULL |
| actionsTaken | ARRAY<VARCHAR> | | Actions taken | No | [] |
| accountsBlocked | ARRAY<UUID> | | Accounts blocked | No | [] |
| lawEnforcementNotified | BOOLEAN | Not Null | Law enforcement notified | No | FALSE |
| notificationDate | DATE | | Notification date | No | NULL |
| estimatedLoss | DECIMAL(18,2) | | Estimated loss amount | No | NULL |
| recoveredAmount | DECIMAL(18,2) | | Amount recovered | No | NULL |
| preventedLoss | DECIMAL(18,2) | | Loss prevented | No | NULL |
| modelVersion | VARCHAR(50) | | Fraud model version | No | NULL |
| createdTimestamp | TIMESTAMP | Not Null | Record creation timestamp | Yes | CURRENT_TIMESTAMP |
| lastUpdatedTimestamp | TIMESTAMP | Not Null | Last update timestamp | Yes | CURRENT_TIMESTAMP |

---

## RELATIONSHIPS AND CARDINALITY

### Core Entity Relationships

| Relationship | From Entity | To Entity | Type | Cardinality | Description |
|--------------|-------------|-----------|------|-------------|-------------|
| R1 | PaymentInstruction | Party (Debtor) | Many-to-One | N:1 | Payment has one debtor party |
| R2 | PaymentInstruction | Party (Creditor) | Many-to-One | N:1 | Payment has one creditor party |
| R3 | PaymentInstruction | Account (Debtor) | Many-to-One | N:1 (optional) | Payment may have debtor account |
| R4 | PaymentInstruction | Account (Creditor) | Many-to-One | N:1 (optional) | Payment may have creditor account |
| R5 | PaymentInstruction | FinancialInstitution (DebtorAgent) | Many-to-One | N:1 (optional) | Payment may have debtor agent FI |
| R6 | PaymentInstruction | FinancialInstitution (CreditorAgent) | Many-to-One | N:1 (optional) | Payment may have creditor agent FI |
| R7 | PaymentInstruction | FinancialInstitution (Intermediary1) | Many-to-One | N:1 (optional) | Payment may have intermediary agent 1 |
| R8 | PaymentInstruction | FinancialInstitution (Intermediary2) | Many-to-One | N:1 (optional) | Payment may have intermediary agent 2 |
| R9 | PaymentInstruction | FinancialInstitution (Intermediary3) | Many-to-One | N:1 (optional) | Payment may have intermediary agent 3 |
| R10 | PaymentInstruction | Settlement | One-to-Many | 1:N (optional) | Payment may have multiple settlements |
| R11 | PaymentInstruction | Charge | One-to-Many | 1:N (optional) | Payment may have multiple charges |
| R12 | PaymentInstruction | RegulatoryInfo | One-to-Many | 1:N (optional) | Payment may have multiple regulatory records |
| R13 | PaymentInstruction | RemittanceInfo | One-to-One | 1:1 (optional) | Payment may have remittance information |
| R14 | PaymentInstruction | StatusEvent | One-to-Many | 1:N | Payment has multiple status events |
| R15 | PaymentInstruction | PaymentRelationship (Source) | One-to-Many | 1:N (optional) | Payment may be source of relationships |
| R16 | PaymentInstruction | PaymentRelationship (Related) | One-to-Many | 1:N (optional) | Payment may be target of relationships |
| R17 | PaymentInstruction | UltimateParty | One-to-Many | 1:N (optional) | Payment may have ultimate parties |
| R18 | PaymentInstruction | PaymentPurpose | One-to-One | 1:1 (optional) | Payment may have purpose details |
| R19 | PaymentInstruction | ExchangeRateInfo | One-to-One | 1:1 (optional) | Payment may have FX info |
| R20 | Settlement | Account | Many-to-One | N:1 (optional) | Settlement uses settlement account |
| R21 | Settlement | Account (NostroDebit) | Many-to-One | N:1 (optional) | Settlement debits nostro account |
| R22 | Settlement | Account (NostroCredit) | Many-to-One | N:1 (optional) | Settlement credits nostro account |
| R23 | Settlement | FinancialInstitution | Many-to-One | N:1 (optional) | Settlement has settling agent |
| R24 | Charge | FinancialInstitution | Many-to-One | N:1 (optional) | Charge levied by FI |
| R25 | Charge | Account | Many-to-One | N:1 (optional) | Charge posted to account |
| R26 | Account | FinancialInstitution | Many-to-One | N:1 (optional) | Account serviced by FI |
| R27 | Account | Party | Many-to-One | N:1 (optional) | Account owned by party |
| R28 | FinancialInstitution (Parent) | FinancialInstitution (Child) | One-to-Many | 1:N (optional) | FI has parent company |
| R29 | Currency | Country | Many-to-Many | N:N | Currency used in countries |
| R30 | SchemeCode | ClearingSystem | Many-to-One | N:1 (optional) | Scheme uses clearing system |

### Compliance and Regulatory Relationships

| Relationship | From Entity | To Entity | Type | Cardinality | Description |
|--------------|-------------|-----------|------|-------------|-------------|
| R31 | ScreeningResult | PaymentInstruction | Many-to-One | N:1 (optional) | Screening result for payment |
| R32 | ScreeningResult | Party | Many-to-One | N:1 (optional) | Screening result for party |
| R33 | ComplianceCase | PaymentInstruction | Many-to-Many | N:N | Case involves payments |
| R34 | ComplianceCase | Party | Many-to-Many | N:N | Case involves parties |
| R35 | ComplianceCase | Account | Many-to-Many | N:N | Case involves accounts |
| R36 | RegulatoryReport | PaymentInstruction | Many-to-Many | N:N | Report includes payments |
| R37 | RegulatoryReport | RegulatoryReportType | Many-to-One | N:1 | Report is of type |
| R38 | RegulatoryReport (Amendment) | RegulatoryReport (Original) | Many-to-One | N:1 (optional) | Report amends original |
| R39 | SanctionsList | ScreeningResult | One-to-Many | 1:N | Sanctions list generates screening results |
| R40 | AMLAlert | PaymentInstruction | Many-to-One | N:1 (optional) | Alert triggered by payment |
| R41 | AMLAlert | Party | Many-to-One | N:1 (optional) | Alert relates to party |
| R42 | AMLAlert | Account | Many-to-One | N:1 (optional) | Alert relates to account |
| R43 | AMLAlert | ComplianceCase | Many-to-One | N:1 (optional) | Alert escalated to case |
| R44 | RegulatoryInfo | AMLAlert | Many-to-One | N:1 (optional) | Regulatory info may trigger alert |

### Operational Relationships

| Relationship | From Entity | To Entity | Type | Cardinality | Description |
|--------------|-------------|-----------|------|-------------|-------------|
| R45 | PaymentException | PaymentInstruction | Many-to-One | N:1 | Exception relates to payment |
| R46 | PaymentException (Child) | PaymentException (Root) | Many-to-One | N:1 (optional) | Exception has root cause |
| R47 | ManualIntervention | PaymentInstruction | Many-to-One | N:1 | Intervention for payment |
| R48 | AuditTrail | PaymentInstruction | Many-to-One | N:1 (optional) | Audit for payment changes |
| R49 | AuditTrail | Party | Many-to-One | N:1 (optional) | Audit for party changes |
| R50 | AuditTrail | Account | Many-to-One | N:1 (optional) | Audit for account changes |
| R51 | AuditTrail | FinancialInstitution | Many-to-One | N:1 (optional) | Audit for FI changes |
| R52 | DataQualityIssue | PaymentInstruction | Many-to-One | N:1 (optional) | DQ issue for payment |
| R53 | DataQualityIssue | Party | Many-to-One | N:1 (optional) | DQ issue for party |
| R54 | DataQualityIssue | Account | Many-to-One | N:1 (optional) | DQ issue for account |
| R55 | ReconciliationRecord | PaymentInstruction | Many-to-One | N:1 (optional) | Reconciliation for payment |

### Analytics Relationships

| Relationship | From Entity | To Entity | Type | Cardinality | Description |
|--------------|-------------|-----------|------|-------------|-------------|
| R56 | CustomerPaymentBehavior | Party | Many-to-One | N:1 | Behavior analysis for party |
| R57 | FraudPattern | PaymentInstruction | Many-to-Many | N:N | Pattern involves payments |
| R58 | FraudPattern | Party | Many-to-Many | N:N | Pattern involves parties |
| R59 | FraudPattern | Account | Many-to-Many | N:N | Pattern involves accounts |
| R60 | FraudPattern (Child) | FraudPattern (Related) | Many-to-Many | N:N | Related fraud patterns |

### Graph Database Relationships (Neo4j)

**Key graph patterns for Neo4j implementation:**

```cypher
// Payment to Party relationships
(:PaymentInstruction)-[:HAS_DEBTOR]->(:Party)
(:PaymentInstruction)-[:HAS_CREDITOR]->(:Party)
(:PaymentInstruction)-[:HAS_ULTIMATE_DEBTOR]->(:Party)
(:PaymentInstruction)-[:HAS_ULTIMATE_CREDITOR]->(:Party)

// Payment to Account relationships
(:PaymentInstruction)-[:DEBITS]->(:Account)
(:PaymentInstruction)-[:CREDITS]->(:Account)

// Account to FI relationships
(:Account)-[:SERVICED_BY]->(:FinancialInstitution)
(:Account)-[:OWNED_BY]->(:Party)

// FI relationships
(:FinancialInstitution)-[:PARENT_OF]->(:FinancialInstitution)
(:FinancialInstitution)-[:CORRESPONDENT_OF]->(:FinancialInstitution)
(:FinancialInstitution)-[:MEMBER_OF]->(:ClearingSystem)

// Payment flow relationships
(:PaymentInstruction)-[:DEBTOR_AGENT]->(:FinancialInstitution)
(:PaymentInstruction)-[:CREDITOR_AGENT]->(:FinancialInstitution)
(:PaymentInstruction)-[:INTERMEDIARY_1]->(:FinancialInstitution)
(:PaymentInstruction)-[:INTERMEDIARY_2]->(:FinancialInstitution)
(:PaymentInstruction)-[:INTERMEDIARY_3]->(:FinancialInstitution)

// Payment lifecycle relationships
(:PaymentInstruction)-[:HAS_STATUS_EVENT]->(:StatusEvent)
(:PaymentInstruction)-[:HAS_SETTLEMENT]->(:Settlement)
(:PaymentInstruction)-[:HAS_CHARGE]->(:Charge)

// Payment relationship types
(:PaymentInstruction)-[:RETURNS]->(:PaymentInstruction)
(:PaymentInstruction)-[:REVERSES]->(:PaymentInstruction)
(:PaymentInstruction)-[:CANCELS]->(:PaymentInstruction)
(:PaymentInstruction)-[:COVERS]->(:PaymentInstruction)
(:PaymentInstruction)-[:AMENDS]->(:PaymentInstruction)

// Compliance relationships
(:PaymentInstruction)-[:SCREENED_BY]->(:ScreeningResult)
(:Party)-[:SCREENED_BY]->(:ScreeningResult)
(:Party)-[:ON_SANCTIONS_LIST]->(:SanctionsList)
(:PaymentInstruction)-[:TRIGGERS_ALERT]->(:AMLAlert)
(:AMLAlert)-[:ESCALATED_TO]->(:ComplianceCase)
(:ComplianceCase)-[:INVOLVES_PAYMENT]->(:PaymentInstruction)
(:ComplianceCase)-[:INVOLVES_PARTY]->(:Party)

// Operational relationships
(:PaymentInstruction)-[:HAS_EXCEPTION]->(:PaymentException)
(:PaymentException)-[:ROOT_CAUSE]->(:PaymentException)
(:PaymentInstruction)-[:REQUIRES_INTERVENTION]->(:ManualIntervention)
(:PaymentInstruction)-[:HAS_DQ_ISSUE]->(:DataQualityIssue)

// Analytics relationships
(:Party)-[:HAS_BEHAVIOR_PROFILE]->(:CustomerPaymentBehavior)
(:PaymentInstruction)-[:PART_OF_PATTERN]->(:FraudPattern)
(:FraudPattern)-[:RELATED_TO]->(:FraudPattern)

// Network analysis queries (examples)
// Find payment paths
MATCH path = (debtor:Party)<-[:HAS_DEBTOR]-(p:PaymentInstruction)-[:HAS_CREDITOR]->(creditor:Party)
RETURN path

// Find intermediary chains
MATCH path = (p:PaymentInstruction)-[:DEBTOR_AGENT|INTERMEDIARY_1|INTERMEDIARY_2|INTERMEDIARY_3|CREDITOR_AGENT]->(fi:FinancialInstitution)
RETURN path

// Find related payments (returns, reversals)
MATCH (p1:PaymentInstruction)-[:RETURNS|REVERSES|AMENDS]->(p2:PaymentInstruction)
RETURN p1, p2

// Fraud pattern detection
MATCH (party:Party)<-[:HAS_DEBTOR|HAS_CREDITOR]-(p:PaymentInstruction)
WHERE p.fraudScore > 80
RETURN party, collect(p) as suspiciousPayments

// Sanctions network
MATCH (party:Party)-[:ON_SANCTIONS_LIST]->(sl:SanctionsList)
MATCH (party)<-[:HAS_DEBTOR|HAS_CREDITOR]-(p:PaymentInstruction)
RETURN party, sl, collect(p) as relatedPayments
```

---

## COMPLETE ENTITY SUMMARY

| # | Entity Name | Category | Primary Key | Row Estimate (Annual) | Retention | Partitioning Strategy |
|---|-------------|----------|-------------|------------------------|-----------|----------------------|
| 1 | PaymentInstruction | Core | paymentId (UUID) | 5 billion | 7 years | Year, Month, Region, ProductType |
| 2 | Party | Core | partyId (UUID) | 100 million | Permanent (SCD Type 2) | None (dimension) |
| 3 | Account | Core | accountId (UUID) | 200 million | Permanent (SCD Type 2) | None (dimension) |
| 4 | FinancialInstitution | Core | financialInstitutionId (UUID) | 50,000 | Permanent (SCD Type 2) | None (dimension) |
| 5 | Settlement | Core | settlementId (UUID) | 5 billion | 7 years | Year, Month |
| 6 | Charge | Core | chargeId (UUID) | 5 billion | 7 years | Year, Month |
| 7 | RegulatoryInfo | Core | regulatoryInfoId (UUID) | 2 billion | 10 years | Year, Month, RegulatoryType |
| 8 | RemittanceInfo | Core | remittanceInfoId (UUID) | 3 billion | 7 years | Year, Month |
| 9 | StatusEvent | Core | statusEventId (UUID) | 50 billion | 7 years | Year, Month |
| 10 | PaymentRelationship | Core | relationshipId (UUID) | 500 million | 7 years | Year, Month |
| 11 | UltimateParty | Supporting | ultimatePartyId (UUID) | 1 billion | 7 years | Year, Month |
| 12 | PaymentPurpose | Supporting | paymentPurposeId (UUID) | 5 billion | 7 years | Year, Month |
| 13 | ExchangeRateInfo | Supporting | exchangeRateInfoId (UUID) | 1 billion | 7 years | Year, Month |
| 14 | Currency | Reference | currencyCode (CHAR(3)) | 200 | Permanent | None |
| 15 | Country | Reference | countryCode (CHAR(2)) | 250 | Permanent | None |
| 16 | ClearingSystem | Reference | clearingSystemCode (VARCHAR(50)) | 500 | Permanent | None |
| 17 | PurposeCode | Reference | purposeCode (VARCHAR(4)) | 1,000 | Permanent | None |
| 18 | StatusReasonCode | Reference | statusReasonCode (VARCHAR(4)) | 500 | Permanent | None |
| 19 | ChargeType | Reference | chargeTypeCode (VARCHAR(10)) | 200 | Permanent | None |
| 20 | SchemeCode | Reference | schemeCode (VARCHAR(50)) | 100 | Permanent | None |
| 21 | PaymentType | Reference | paymentTypeCode (VARCHAR(50)) | 350 | Permanent | None |
| 22 | RegulatoryReportType | Reference | reportTypeCode (VARCHAR(50)) | 100 | Permanent | None |
| 23 | ScreeningResult | Compliance | screeningResultId (UUID) | 10 billion | 10 years | Year, Month |
| 24 | ComplianceCase | Compliance | complianceCaseId (UUID) | 50 million | 10 years | Year |
| 25 | RegulatoryReport | Compliance | regulatoryReportId (UUID) | 10 million | 10 years | Year |
| 26 | SanctionsList | Compliance | sanctionsListId (UUID) | 100,000 | Permanent (updated) | None |
| 27 | AMLAlert | Compliance | amlAlertId (UUID) | 100 million | 10 years | Year, Month |
| 28 | PaymentException | Operational | exceptionId (UUID) | 500 million | 3 years | Year, Month |
| 29 | ManualIntervention | Operational | interventionId (UUID) | 100 million | 5 years | Year, Month |
| 30 | AuditTrail | Operational | auditId (UUID) | 100 billion | 7 years | Year, Month, EntityType |
| 31 | DataQualityIssue | Operational | dataQualityIssueId (UUID) | 200 million | 3 years | Year, Month |
| 32 | ReconciliationRecord | Operational | reconciliationId (UUID) | 5 billion | 7 years | Year, Month |
| 33 | PaymentMetrics | Analytics | metricsId (UUID) | 100 million | 5 years | Year, Month |
| 34 | CustomerPaymentBehavior | Analytics | behaviorId (UUID) | 100 million | 5 years | AnalysisDate |
| 35 | PaymentFlowAnalysis | Analytics | flowAnalysisId (UUID) | 50 million | 5 years | AnalysisDate |
| 36 | FraudPattern | Analytics | fraudPatternId (UUID) | 10 million | 10 years | Year, Month |

**Total Entities**: 36 (10 Core, 3 Supporting, 9 Reference, 5 Compliance, 5 Operational, 4 Analytics)

**Total Estimated Annual Volume**: ~100 billion records across all fact tables

**Data Lifecycle**:
- **Hot Data** (0-90 days): Full performance optimization, all queries
- **Warm Data** (91 days - 2 years): Optimized for analytics, compliance queries
- **Cold Data** (2-7 years): Archive tier, compliance/audit access only
- **Frozen Data** (7+ years): Regulatory retention only, restore on demand

**Storage Estimate**:
- Bronze Layer: ~500 TB/year (raw data)
- Silver Layer: ~400 TB/year (cleansed, enriched)
- Gold Layer: ~100 TB/year (aggregated, curated)
- Neo4j Graph: ~50 TB (relationship-heavy queries)

---

## DOCUMENT STATUS

**Completeness Level**: 100%

**Entities Documented**: 36/36
- Core Domain Entities: 10/10 ✓
- Supporting Domain Entities: 3/3 ✓
- Reference Data Entities: 9/9 ✓
- Compliance and Regulatory Entities: 5/5 ✓
- Operational Entities: 5/5 ✓
- Analytics Entities: 4/4 ✓

**Relationships Documented**: 60 primary relationships + graph patterns ✓

**Attributes Specified**: 2,000+ attributes with complete specifications ✓

**Document Version**: 1.0 - COMPLETE

**Last Updated**: December 18, 2025

**Next Steps**:
1. Create Physical Data Model (JSON schemas, Delta Lake DDL)
2. Create Complete Reconciliation Matrix
3. Create Complete Mapping Documentation
4. Create Granular Approach Documentation

---
