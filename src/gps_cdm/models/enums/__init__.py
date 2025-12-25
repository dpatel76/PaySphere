"""
GPS Payments CDM - Enumeration Types
====================================

Standard enumeration types used across CDM entities.
Covers 69 payment standards and 32+ regulatory reports.
"""

from enum import Enum


# =============================================================================
# PAYMENT TYPES
# =============================================================================

class PaymentType(str, Enum):
    """Type of payment transaction."""
    CREDIT_TRANSFER = "CREDIT_TRANSFER"
    DIRECT_DEBIT = "DIRECT_DEBIT"
    RETURN = "RETURN"
    REVERSAL = "REVERSAL"
    STATUS_REPORT = "STATUS_REPORT"
    CANCELLATION = "CANCELLATION"
    AMENDMENT = "AMENDMENT"
    INVESTIGATION = "INVESTIGATION"


# =============================================================================
# ISO 20022 MESSAGE TYPES (33 Message Types)
# =============================================================================

class ISO20022MessageType(str, Enum):
    """ISO 20022 message types - complete coverage."""
    # PAIN - Payment Initiation (6)
    PAIN_001 = "pain.001"  # Customer Credit Transfer Initiation
    PAIN_002 = "pain.002"  # Customer Payment Status Report
    PAIN_007 = "pain.007"  # Customer Payment Reversal
    PAIN_008 = "pain.008"  # Customer Direct Debit Initiation
    PAIN_013 = "pain.013"  # Creditor Payment Activation Request Amendment
    PAIN_014 = "pain.014"  # Creditor Payment Activation Request Status Report

    # PACS - Payments Clearing and Settlement (7)
    PACS_002 = "pacs.002"  # FI Payment Status Report
    PACS_003 = "pacs.003"  # FI Customer Direct Debit
    PACS_004 = "pacs.004"  # Payment Return
    PACS_007 = "pacs.007"  # FI Payment Reversal
    PACS_008 = "pacs.008"  # FI Credit Transfer
    PACS_009 = "pacs.009"  # FI Credit Transfer Own Account
    PACS_028 = "pacs.028"  # FI Payment Status Request

    # CAMT - Cash Management (16)
    CAMT_026 = "camt.026"  # Unable to Apply
    CAMT_027 = "camt.027"  # Claim Non-Receipt
    CAMT_029 = "camt.029"  # Resolution of Investigation
    CAMT_050 = "camt.050"  # Liquidity Credit Transfer
    CAMT_052 = "camt.052"  # Account Report (Intraday)
    CAMT_053 = "camt.053"  # Bank Statement
    CAMT_054 = "camt.054"  # Debit/Credit Notification
    CAMT_055 = "camt.055"  # Customer Payment Cancellation Request
    CAMT_056 = "camt.056"  # FI Payment Cancellation Request
    CAMT_057 = "camt.057"  # Notification to Receive
    CAMT_058 = "camt.058"  # Notification to Receive Cancellation Advice
    CAMT_059 = "camt.059"  # Account Reporting Request
    CAMT_060 = "camt.060"  # Account Reporting Request (Alternative)
    CAMT_086 = "camt.086"  # Bank Service Billing
    CAMT_087 = "camt.087"  # Request to Modify Payment

    # ACMT - Account Management (4)
    ACMT_001 = "acmt.001"  # Account Opening Instruction
    ACMT_002 = "acmt.002"  # Account Details Confirmation
    ACMT_003 = "acmt.003"  # Account Modification Instruction
    ACMT_007 = "acmt.007"  # Account Opening Request


# =============================================================================
# SWIFT MT MESSAGE TYPES (14 Message Types)
# =============================================================================

class SWIFTMTMessageType(str, Enum):
    """SWIFT MT message types."""
    # Customer Payments
    MT103 = "MT103"      # Single Customer Credit Transfer
    MT103_STP = "MT103+" # STP Credit Transfer

    # Financial Institution Transfers
    MT200 = "MT200"      # FI Own Account Transfer
    MT201 = "MT201"      # Multiple FI Transfer for Own Account
    MT202 = "MT202"      # General FI Transfer
    MT202COV = "MT202COV" # General FI Transfer Cover Payment
    MT203 = "MT203"      # Multiple FI to FI Transfer
    MT204 = "MT204"      # FI Direct Debit
    MT205 = "MT205"      # FI Direct Debit (COV)

    # Confirmations
    MT900 = "MT900"      # Confirmation of Debit
    MT910 = "MT910"      # Confirmation of Credit

    # Statements
    MT940 = "MT940"      # Customer Statement Message
    MT942 = "MT942"      # Interim Transaction Report
    MT950 = "MT950"      # Statement Message


# =============================================================================
# PAYMENT SCHEME CODES (22 Regional Systems + SWIFT/ISO)
# =============================================================================

class SchemeCode(str, Enum):
    """Payment scheme/network identifier - full global coverage."""
    # ISO/SWIFT (Global)
    SWIFT = "SWIFT"
    ISO20022 = "ISO20022"

    # United States (5)
    ACH = "ACH"              # NACHA Automated Clearing House
    FEDWIRE = "FEDWIRE"      # Federal Reserve Wire Transfer
    CHIPS = "CHIPS"          # Clearing House Interbank Payment System
    RTP = "RTP"              # Real-Time Payments (The Clearing House)
    FEDNOW = "FEDNOW"        # Federal Reserve Instant Payment

    # United Kingdom (3)
    BACS = "BACS"            # Bankers Automated Clearing
    FPS = "FPS"              # Faster Payments Service
    CHAPS = "CHAPS"          # Clearing House Automated Payment System

    # Europe (5)
    SEPA_SCT = "SEPA_SCT"    # SEPA Credit Transfer
    SEPA_INST = "SEPA_INST"  # SEPA Instant Credit Transfer
    SEPA_SDD_CORE = "SEPA_SDD_CORE"  # SEPA Direct Debit Core
    SEPA_SDD_B2B = "SEPA_SDD_B2B"    # SEPA Direct Debit B2B
    TARGET2 = "TARGET2"      # Trans-European RTGS

    # Latin America (1)
    PIX = "PIX"              # Brazil Instant Payment System

    # Asia-Pacific (8)
    UPI = "UPI"              # India Unified Payments Interface
    IMPS = "IMPS"            # India Immediate Payment Service
    PAYNOW = "PAYNOW"        # Singapore Instant Payment
    PROMPTPAY = "PROMPTPAY"  # Thailand Instant Payment
    INSTAPAY = "INSTAPAY"    # Philippines Instant Payment
    NPP = "NPP"              # Australia New Payments Platform
    CNAPS = "CNAPS"          # China National Advanced Payment System
    CIPS = "CIPS"            # China Cross-border Interbank Payment System
    RTGS_HK = "RTGS_HK"      # Hong Kong Real-Time Gross Settlement

    # Other
    CHECK = "CHECK"
    MOBILE = "MOBILE"
    CARD = "CARD"
    CRYPTO = "CRYPTO"
    INTERNAL = "INTERNAL"


# =============================================================================
# REGULATORY REPORT TYPES (32+ Report Types)
# =============================================================================

class RegulatoryReportType(str, Enum):
    """Regulatory report types - complete global coverage."""
    # FinCEN - United States (7)
    FINCEN_CTR = "FINCEN_CTR"       # Currency Transaction Report (Form 112)
    FINCEN_SAR = "FINCEN_SAR"       # Suspicious Activity Report (Form 111)
    FINCEN_FBAR = "FINCEN_FBAR"     # Foreign Bank Account Report (Form 114)
    FINCEN_8300 = "FINCEN_8300"     # Cash Payments Over $10,000
    FINCEN_CMIR = "FINCEN_CMIR"     # Currency and Monetary Instrument Report (Form 104)
    FINCEN_314A = "FINCEN_314A"     # Information Request
    FINCEN_314B = "FINCEN_314B"     # Information Sharing Notice

    # AUSTRAC - Australia (5)
    AUSTRAC_IFTI = "AUSTRAC_IFTI"   # International Funds Transfer Instruction
    AUSTRAC_IFTI_IN = "AUSTRAC_IFTI_IN"   # IFTI Inbound
    AUSTRAC_IFTI_OUT = "AUSTRAC_IFTI_OUT" # IFTI Outbound
    AUSTRAC_TTR = "AUSTRAC_TTR"     # Threshold Transaction Report
    AUSTRAC_SMR = "AUSTRAC_SMR"     # Suspicious Matter Report

    # FINTRAC - Canada (4)
    FINTRAC_LCTR = "FINTRAC_LCTR"   # Large Cash Transaction Report
    FINTRAC_STR = "FINTRAC_STR"     # Suspicious Transaction Report
    FINTRAC_EFTR = "FINTRAC_EFTR"   # Electronic Funds Transfer Report
    FINTRAC_TPR = "FINTRAC_TPR"     # Terrorist Property Report

    # IRS/OECD - Tax Compliance (4)
    FATCA_8966 = "FATCA_8966"       # FATCA Form 8966
    FATCA_POOL = "FATCA_POOL"       # FATCA Pool Report
    OECD_CRS = "OECD_CRS"           # Common Reporting Standard
    OECD_CRS_CP = "OECD_CRS_CP"     # CRS Controlling Person Report

    # EBA - European Banking Authority (1)
    EBA_PSD2_FRAUD = "EBA_PSD2_FRAUD"  # PSD2 Payment Fraud Statistical Report

    # ESMA - European Securities and Markets Authority (3)
    ESMA_MIFID_II = "ESMA_MIFID_II"    # MiFID II Transaction Report
    ESMA_EMIR = "ESMA_EMIR"             # EMIR Trade Report
    ESMA_MAR_STOR = "ESMA_MAR_STOR"     # Suspicious Transaction and Order Report

    # EU General (2)
    EU_AMLD5_BO = "EU_AMLD5_BO"        # AMLD5 Beneficial Ownership
    EU_TFR_ART15 = "EU_TFR_ART15"      # Terrorism Financing Regulation Article 15

    # UK NCA - National Crime Agency (2)
    UK_SAR = "UK_SAR"                  # UK Suspicious Activity Report
    UK_DAML_SAR = "UK_DAML_SAR"        # Defence Against Money Laundering SAR

    # Asia-Pacific (3) - Filed with FIUs
    JFIU_STR = "JFIU_STR"              # Hong Kong STR (filed with JFIU, supervised by HKMA)
    STRO_STR = "STRO_STR"              # Singapore STR (filed with STRO, supervised by MAS)
    JAFIC_STR = "JAFIC_STR"            # Japan STR (filed with JAFIC, supervised by FSA)

    # OFAC - US Treasury (1)
    OFAC_BLOCKING = "OFAC_BLOCKING"    # OFAC Blocked Property Report

    # Multi-jurisdiction (1)
    TERRORIST_PROPERTY = "TERRORIST_PROPERTY"  # UN/National Terrorist Property Report


class Regulator(str, Enum):
    """Regulatory authority identifiers."""
    # United States
    FINCEN = "FINCEN"       # Financial Crimes Enforcement Network
    IRS = "IRS"             # Internal Revenue Service
    OFAC = "OFAC"           # Office of Foreign Assets Control
    SEC = "SEC"             # Securities and Exchange Commission
    FRB = "FRB"             # Federal Reserve Board
    OCC = "OCC"             # Office of the Comptroller of the Currency
    FDIC = "FDIC"           # Federal Deposit Insurance Corporation

    # Australia
    AUSTRAC = "AUSTRAC"     # Australian Transaction Reports and Analysis Centre
    APRA = "APRA"           # Australian Prudential Regulation Authority
    ASIC = "ASIC"           # Australian Securities and Investments Commission

    # Canada
    FINTRAC = "FINTRAC"     # Financial Transactions and Reports Analysis Centre

    # Europe
    EBA = "EBA"             # European Banking Authority
    ESMA = "ESMA"           # European Securities and Markets Authority
    ECB = "ECB"             # European Central Bank

    # United Kingdom
    UK_NCA = "UK_NCA"       # National Crime Agency
    FCA = "FCA"             # Financial Conduct Authority
    PRA = "PRA"             # Prudential Regulation Authority

    # Asia-Pacific - Financial Intelligence Units (FIUs)
    JFIU = "JFIU"           # Joint Financial Intelligence Unit (Hong Kong)
    STRO = "STRO"           # Suspicious Transaction Reporting Office (Singapore)
    JAFIC = "JAFIC"         # Japan Financial Intelligence Center

    # Asia-Pacific - Supervisory Authorities
    HKMA = "HKMA"           # Hong Kong Monetary Authority (supervisor, STRs filed with JFIU)
    MAS = "MAS"             # Monetary Authority of Singapore (supervisor, STRs filed with STRO)
    FSA_JP = "FSA_JP"       # Financial Services Agency (Japan)
    RBI = "RBI"             # Reserve Bank of India
    PBOC = "PBOC"           # People's Bank of China

    # International
    OECD = "OECD"           # Organisation for Economic Co-operation and Development
    FATF = "FATF"           # Financial Action Task Force
    BIS = "BIS"             # Bank for International Settlements


class Jurisdiction(str, Enum):
    """Jurisdiction codes."""
    US = "US"
    AU = "AU"
    CA = "CA"
    UK = "UK"
    EU = "EU"
    HK = "HK"
    SG = "SG"
    JP = "JP"
    IN = "IN"
    CN = "CN"
    BR = "BR"
    TH = "TH"
    PH = "PH"
    INTERNATIONAL = "INTERNATIONAL"


# =============================================================================
# PAYMENT STATUS AND LIFECYCLE
# =============================================================================

class PaymentStatus(str, Enum):
    """Payment lifecycle status."""
    # Initiation
    INITIATED = "initiated"
    RECEIVED = "received"
    ACCEPTED = "accepted"

    # Validation
    VALIDATION_PENDING = "validation_pending"
    VALIDATED = "validated"
    VALIDATION_FAILED = "validation_failed"

    # Fraud Screening
    FRAUD_SCREENING = "fraud_screening"
    FRAUD_CLEAR = "fraud_clear"
    FRAUD_HOLD = "fraud_hold"
    FRAUD_REJECT = "fraud_reject"

    # Sanctions Screening
    SANCTIONS_SCREENING = "sanctions_screening"
    SANCTIONS_CLEAR = "sanctions_clear"
    SANCTIONS_HIT = "sanctions_hit"
    SANCTIONS_REJECTED = "sanctions_rejected"

    # Compliance
    COMPLIANCE_REVIEW = "compliance_review"
    COMPLIANCE_APPROVED = "compliance_approved"
    COMPLIANCE_REJECTED = "compliance_rejected"

    # Processing
    ENRICHMENT_PENDING = "enrichment_pending"
    ENRICHED = "enriched"
    PROCESSING = "processing"
    QUEUED = "queued"
    ROUTED = "routed"
    TRANSMITTED = "transmitted"

    # Clearing & Settlement
    IN_CLEARING = "in_clearing"
    CLEARING_FAILED = "clearing_failed"
    SETTLEMENT_PENDING = "settlement_pending"
    SETTLED = "settled"
    SETTLEMENT_FAILED = "settlement_failed"
    PARTIALLY_SETTLED = "partially_settled"

    # Final States
    COMPLETED = "completed"
    RETURNED = "returned"
    REVERSED = "reversed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    FAILED = "failed"

    # Hold States
    SUSPENDED = "suspended"
    ON_HOLD = "on_hold"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"


class PaymentDirection(str, Enum):
    """Payment direction."""
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    INTERNAL = "INTERNAL"
    PASS_THROUGH = "PASS_THROUGH"


class Priority(str, Enum):
    """Payment priority."""
    HIGH = "HIGH"
    NORM = "NORM"
    URGP = "URGP"
    LOW = "LOW"


class ChargeBearer(str, Enum):
    """Who bears the charges."""
    DEBT = "DEBT"  # Debtor
    CRED = "CRED"  # Creditor
    SHAR = "SHAR"  # Shared
    SLEV = "SLEV"  # Service Level


# =============================================================================
# PARTY TYPES
# =============================================================================

class PartyType(str, Enum):
    """Type of party."""
    INDIVIDUAL = "INDIVIDUAL"
    CORPORATE = "CORPORATE"
    ORGANIZATION = "ORGANIZATION"
    GOVERNMENT = "GOVERNMENT"
    FINANCIAL_INSTITUTION = "FINANCIAL_INSTITUTION"
    TRUST = "TRUST"
    ESTATE = "ESTATE"
    PARTNERSHIP = "PARTNERSHIP"


class PartyRole(str, Enum):
    """Role of party in transaction."""
    DEBTOR = "DEBTOR"
    CREDITOR = "CREDITOR"
    DEBTOR_AGENT = "DEBTOR_AGENT"
    CREDITOR_AGENT = "CREDITOR_AGENT"
    INSTRUCTING_AGENT = "INSTRUCTING_AGENT"
    INSTRUCTED_AGENT = "INSTRUCTED_AGENT"
    INTERMEDIARY_AGENT_1 = "INTERMEDIARY_AGENT_1"
    INTERMEDIARY_AGENT_2 = "INTERMEDIARY_AGENT_2"
    INTERMEDIARY_AGENT_3 = "INTERMEDIARY_AGENT_3"
    ULTIMATE_DEBTOR = "ULTIMATE_DEBTOR"
    ULTIMATE_CREDITOR = "ULTIMATE_CREDITOR"
    INITIATING_PARTY = "INITIATING_PARTY"
    FORWARDING_AGENT = "FORWARDING_AGENT"


class TaxIdType(str, Enum):
    """Tax identification type."""
    SSN = "SSN"               # US Social Security Number
    EIN = "EIN"               # US Employer Identification Number
    ITIN = "ITIN"             # US Individual Taxpayer Identification Number
    TIN = "TIN"               # Generic Tax Identification Number
    VAT = "VAT"               # Value Added Tax Number
    ABN = "ABN"               # Australian Business Number
    TFN = "TFN"               # Australian Tax File Number
    SIN = "SIN"               # Canada Social Insurance Number
    BN = "BN"                 # Canada Business Number
    NI_NUMBER = "NI_NUMBER"   # UK National Insurance Number
    UTR = "UTR"               # UK Unique Taxpayer Reference
    PAN = "PAN"               # India Permanent Account Number
    GSTIN = "GSTIN"           # India GST Identification Number
    CPF = "CPF"               # Brazil Individual Tax ID
    CNPJ = "CNPJ"             # Brazil Corporate Tax ID


class IdentificationType(str, Enum):
    """Party identification type."""
    # Tax IDs
    SSN = "SSN"               # US Social Security Number
    EIN = "EIN"               # US Employer Identification Number
    ITIN = "ITIN"             # US Individual Taxpayer Identification Number
    TIN = "TIN"               # Generic Tax Identification Number
    VAT = "VAT"               # Value Added Tax Number

    # National IDs - Americas
    CPF = "CPF"               # Brazil Individual Tax ID
    CNPJ = "CNPJ"             # Brazil Corporate Tax ID
    SIN = "SIN"               # Canada Social Insurance Number
    BN = "BN"                 # Canada Business Number

    # National IDs - Europe
    NI_NUMBER = "NI_NUMBER"   # UK National Insurance Number
    CRN = "CRN"               # UK Company Registration Number

    # National IDs - APAC
    AADHAR = "AADHAR"         # India Aadhar Number
    PAN = "PAN"               # India Permanent Account Number
    NRIC = "NRIC"             # Singapore National Registration Identity Card
    FIN = "FIN"               # Singapore Foreign Identification Number
    HKID = "HKID"             # Hong Kong Identity Card
    MY_NUMBER = "MY_NUMBER"   # Japan My Number
    HUKOU = "HUKOU"           # China Household Registration

    # Financial IDs
    BIC = "BIC"               # Bank Identifier Code
    LEI = "LEI"               # Legal Entity Identifier
    DUNS = "DUNS"             # Dun & Bradstreet Number

    # Other
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    NATIONAL_ID = "NATIONAL_ID"
    OTHER = "OTHER"


# =============================================================================
# TAX COMPLIANCE (FATCA/CRS)
# =============================================================================

class USTaxStatus(str, Enum):
    """FATCA US tax status."""
    US_CITIZEN = "US_CITIZEN"
    US_RESIDENT_ALIEN = "US_RESIDENT_ALIEN"
    NON_RESIDENT_ALIEN = "NON_RESIDENT_ALIEN"
    US_CORPORATION = "US_CORPORATION"
    US_PARTNERSHIP = "US_PARTNERSHIP"
    US_TRUST = "US_TRUST"
    FOREIGN_ENTITY = "FOREIGN_ENTITY"


class FATCAClassification(str, Enum):
    """FATCA entity classification."""
    ACTIVE_NFFE = "ACTIVE_NFFE"
    PASSIVE_NFFE = "PASSIVE_NFFE"
    FFI = "FFI"
    PARTICIPATING_FFI = "PARTICIPATING_FFI"
    REGISTERED_DEEMED_COMPLIANT_FFI = "REGISTERED_DEEMED_COMPLIANT_FFI"
    CERTIFIED_DEEMED_COMPLIANT_FFI = "CERTIFIED_DEEMED_COMPLIANT_FFI"
    EXCEPTED_FFI = "EXCEPTED_FFI"
    EXEMPT_BENEFICIAL_OWNER = "EXEMPT_BENEFICIAL_OWNER"
    DIRECT_REPORTING_NFFE = "DIRECT_REPORTING_NFFE"
    SPONSORED_DIRECT_REPORTING_NFFE = "SPONSORED_DIRECT_REPORTING_NFFE"
    NONPARTICIPATING_FFI = "NONPARTICIPATING_FFI"
    OWNER_DOCUMENTED_FFI = "OWNER_DOCUMENTED_FFI"


class CRSEntityType(str, Enum):
    """CRS entity type classification."""
    FINANCIAL_INSTITUTION = "FINANCIAL_INSTITUTION"
    ACTIVE_NFE = "ACTIVE_NFE"
    PASSIVE_NFE = "PASSIVE_NFE"
    INVESTMENT_ENTITY = "INVESTMENT_ENTITY"
    GOVERNMENT_ENTITY = "GOVERNMENT_ENTITY"
    INTERNATIONAL_ORGANISATION = "INTERNATIONAL_ORGANISATION"
    CENTRAL_BANK = "CENTRAL_BANK"
    DEPOSITORY_INSTITUTION = "DEPOSITORY_INSTITUTION"
    CUSTODIAL_INSTITUTION = "CUSTODIAL_INSTITUTION"
    SPECIFIED_INSURANCE_COMPANY = "SPECIFIED_INSURANCE_COMPANY"


class CRSAccountType(str, Enum):
    """CRS account type."""
    DEPOSITORY = "DEPOSITORY"
    CUSTODIAL = "CUSTODIAL"
    DEBT_INTEREST = "DEBT_INTEREST"
    EQUITY_INTEREST = "EQUITY_INTEREST"
    CASH_VALUE_INSURANCE = "CASH_VALUE_INSURANCE"
    ANNUITY_CONTRACT = "ANNUITY_CONTRACT"


# =============================================================================
# RISK AND COMPLIANCE
# =============================================================================

class RiskRating(str, Enum):
    """Risk rating level."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    PROHIBITED = "prohibited"


class SanctionsStatus(str, Enum):
    """Sanctions screening status."""
    NOT_SCREENED = "not_screened"
    CLEAR = "clear"
    POTENTIAL_MATCH = "potential_match"
    HIT = "hit"
    PENDING = "pending"
    FALSE_POSITIVE = "false_positive"
    TRUE_POSITIVE = "true_positive"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class PEPStatus(str, Enum):
    """Politically Exposed Person status."""
    NOT_PEP = "NOT_PEP"
    PEP_DOMESTIC = "PEP_DOMESTIC"
    PEP_FOREIGN = "PEP_FOREIGN"
    PEP_INTERNATIONAL_ORG = "PEP_INTERNATIONAL_ORG"
    RCA = "RCA"  # Relative or Close Associate
    FORMER_PEP = "FORMER_PEP"


class SARIndicator(str, Enum):
    """SAR filing indicators."""
    STRUCTURING = "STRUCTURING"
    TERRORIST_FINANCING = "TERRORIST_FINANCING"
    FRAUD = "FRAUD"
    MONEY_LAUNDERING = "MONEY_LAUNDERING"
    BRIBERY_CORRUPTION = "BRIBERY_CORRUPTION"
    TAX_EVASION = "TAX_EVASION"
    IDENTITY_THEFT = "IDENTITY_THEFT"
    CYBER_EVENT = "CYBER_EVENT"
    ELDER_ABUSE = "ELDER_ABUSE"
    HUMAN_TRAFFICKING = "HUMAN_TRAFFICKING"
    DRUG_TRAFFICKING = "DRUG_TRAFFICKING"
    OTHER = "OTHER"


# =============================================================================
# ACCOUNT TYPES
# =============================================================================

class AccountType(str, Enum):
    """Account type."""
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    MONEY_MARKET = "MONEY_MARKET"
    CD = "CD"
    LOAN = "LOAN"
    CREDIT_CARD = "CREDIT_CARD"
    INVESTMENT = "INVESTMENT"
    BROKERAGE = "BROKERAGE"
    RETIREMENT = "RETIREMENT"
    IRA = "IRA"
    TRUST = "TRUST"
    CUSTODIAL = "CUSTODIAL"
    ESCROW = "ESCROW"
    NOSTRO = "NOSTRO"
    VOSTRO = "VOSTRO"
    LORO = "LORO"
    SUSPENSE = "SUSPENSE"
    CORRESPONDENT = "CORRESPONDENT"
    OTHER = "OTHER"


class AccountStatus(str, Enum):
    """Account status."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DORMANT = "DORMANT"
    CLOSED = "CLOSED"
    FROZEN = "FROZEN"
    SUSPENDED = "SUSPENDED"
    RESTRICTED = "RESTRICTED"


class OwnershipType(str, Enum):
    """Account ownership type."""
    PRIMARY = "PRIMARY"
    JOINT = "JOINT"
    BENEFICIAL = "BENEFICIAL"
    AUTHORIZED_SIGNER = "AUTHORIZED_SIGNER"
    POWER_OF_ATTORNEY = "POWER_OF_ATTORNEY"
    TRUSTEE = "TRUSTEE"
    NOMINEE = "NOMINEE"
    CUSTODIAN = "CUSTODIAN"
    CONTROLLING_PERSON = "CONTROLLING_PERSON"


# =============================================================================
# SETTLEMENT
# =============================================================================

class SettlementMethod(str, Enum):
    """Settlement method."""
    INDA = "INDA"  # Instructed Agent
    INGA = "INGA"  # Instructing Agent
    COVE = "COVE"  # Cover Method
    CLRG = "CLRG"  # Clearing System


class SettlementStatus(str, Enum):
    """Settlement status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SETTLED = "SETTLED"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"


class ClearingSystemType(str, Enum):
    """Clearing system type."""
    RTGS = "RTGS"           # Real-Time Gross Settlement
    ACH = "ACH"             # Automated Clearing House
    HYBRID = "HYBRID"       # Hybrid (DNS/RTGS)
    NETTING = "NETTING"     # Net Settlement
    INSTANT = "INSTANT"     # Instant Payment
    DEFERRED = "DEFERRED"   # Deferred Net Settlement


# =============================================================================
# EVENTS AND AUDIT
# =============================================================================

class EventType(str, Enum):
    """Payment event type."""
    # Lifecycle
    CREATED = "CREATED"
    RECEIVED = "RECEIVED"
    STATUS_CHANGE = "STATUS_CHANGE"

    # Validation
    VALIDATION_STARTED = "VALIDATION_STARTED"
    VALIDATION_PASSED = "VALIDATION_PASSED"
    VALIDATION_FAILED = "VALIDATION_FAILED"

    # Sanctions
    SANCTIONS_SCREENING_STARTED = "SANCTIONS_SCREENING_STARTED"
    SANCTIONS_SCREENING_PASSED = "SANCTIONS_SCREENING_PASSED"
    SANCTIONS_SCREENING_HIT = "SANCTIONS_SCREENING_HIT"

    # Fraud
    FRAUD_SCREENING_STARTED = "FRAUD_SCREENING_STARTED"
    FRAUD_SCREENING_PASSED = "FRAUD_SCREENING_PASSED"
    FRAUD_SCREENING_ALERT = "FRAUD_SCREENING_ALERT"

    # Regulatory
    REGULATORY_REPORT_GENERATED = "REGULATORY_REPORT_GENERATED"
    REGULATORY_REPORT_SUBMITTED = "REGULATORY_REPORT_SUBMITTED"
    CTR_TRIGGERED = "CTR_TRIGGERED"
    SAR_TRIGGERED = "SAR_TRIGGERED"

    # Settlement
    SETTLEMENT_INITIATED = "SETTLEMENT_INITIATED"
    SETTLEMENT_COMPLETED = "SETTLEMENT_COMPLETED"
    SETTLEMENT_FAILED = "SETTLEMENT_FAILED"

    # Final
    COMPLETED = "COMPLETED"
    ERROR_OCCURRED = "ERROR_OCCURRED"


class ActorType(str, Enum):
    """Actor type for events/audit."""
    SYSTEM = "SYSTEM"
    USER = "USER"
    EXTERNAL = "EXTERNAL"
    BATCH = "BATCH"
    API = "API"
    SCHEDULER = "SCHEDULER"
    REGULATOR = "REGULATOR"


class TransformationType(str, Enum):
    """Data transformation type."""
    DIRECT = "DIRECT"
    DERIVED = "DERIVED"
    LOOKUP = "LOOKUP"
    AGGREGATED = "AGGREGATED"
    CONSTANT = "CONSTANT"
    DEFAULT = "DEFAULT"
    CONCATENATION = "CONCATENATION"
    SPLIT = "SPLIT"
    CONDITIONAL = "CONDITIONAL"
    FORMAT = "FORMAT"
    PARSE = "PARSE"
    ENRICHMENT = "ENRICHMENT"
    CALCULATED = "CALCULATED"
    MAPPED = "MAPPED"


class AuditAction(str, Enum):
    """Audit trail action type."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SOFT_DELETE = "SOFT_DELETE"
    RESTORE = "RESTORE"
    READ = "READ"
    EXPORT = "EXPORT"
    ARCHIVE = "ARCHIVE"
    REGULATORY_REPORT = "REGULATORY_REPORT"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"


# =============================================================================
# GEOGRAPHIC
# =============================================================================

class Region(str, Enum):
    """Geographic region."""
    US = "US"
    EMEA = "EMEA"
    APAC = "APAC"
    LATAM = "LATAM"
    CANADA = "CANADA"
    MENA = "MENA"
    AFRICA = "AFRICA"


class CorridorType(str, Enum):
    """Payment corridor type."""
    DOMESTIC = "DOMESTIC"
    CROSS_BORDER = "CROSS_BORDER"
    INTRA_REGION = "INTRA_REGION"
    INTER_REGION = "INTER_REGION"


# =============================================================================
# DATA QUALITY
# =============================================================================

class DataQualityLevel(str, Enum):
    """Data quality level."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


class DataQualityDimension(str, Enum):
    """Data quality dimension."""
    COMPLETENESS = "COMPLETENESS"
    ACCURACY = "ACCURACY"
    CONSISTENCY = "CONSISTENCY"
    TIMELINESS = "TIMELINESS"
    VALIDITY = "VALIDITY"
    UNIQUENESS = "UNIQUENESS"


# =============================================================================
# FILING FREQUENCY
# =============================================================================

class FilingFrequency(str, Enum):
    """Regulatory filing frequency."""
    REAL_TIME = "REAL_TIME"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMI_ANNUAL = "SEMI_ANNUAL"
    ANNUAL = "ANNUAL"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    AD_HOC = "AD_HOC"
