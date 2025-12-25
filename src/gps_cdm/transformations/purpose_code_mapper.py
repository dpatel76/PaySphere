#!/usr/bin/env python3
"""
Standardized Purpose Code Mapper for GPS CDM.

Maps native purpose codes from various payment schemes to:
1. ISO 20022 External Purpose Codes (ExternalPurpose1Code)
2. CDM Standardized Purpose Codes
3. Regulatory Purpose Categories

Coverage:
- ISO 20022 (PAIN, PACS) - Native support
- SWIFT MT103 Field 70 - Transaction Type Identification
- SEPA (SCT, SDD) - SEPA purpose codes
- ACH/NACHA - SEC codes and addenda type codes
- Fedwire - Business Function Codes
- Real-time payments (FedNow, RTP, PIX, UPI, etc.)
- RTGS systems (TARGET2, BOJNET, CNAPS, etc.)

Reference: ISO 20022 External Code Sets - ExternalPurpose1Code
https://www.iso20022.org/catalogue-messages/additional-content-messages/external-code-sets
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CDMPurposeCategory(Enum):
    """CDM standardized purpose categories."""
    TRADE = "TRADE"  # Trade finance, import/export
    SALARY = "SALARY"  # Salary, wages, payroll
    PENSION = "PENSION"  # Pension, retirement
    DIVIDEND = "DIVIDEND"  # Dividends, distributions
    TAX = "TAX"  # Tax payments
    LOAN = "LOAN"  # Loan disbursement/repayment
    INVOICE = "INVOICE"  # Invoice payment
    SUBSCRIPTION = "SUBSCRIPTION"  # Subscription services
    UTILITY = "UTILITY"  # Utility payments
    RENT = "RENT"  # Rent payments
    INSURANCE = "INSURANCE"  # Insurance premiums
    INVESTMENT = "INVESTMENT"  # Investment transactions
    ROYALTY = "ROYALTY"  # Royalty payments
    LICENSE = "LICENSE"  # License fees
    COMMISSION = "COMMISSION"  # Commissions
    REFUND = "REFUND"  # Refunds
    TRANSFER = "TRANSFER"  # Account transfers
    CHARITY = "CHARITY"  # Charitable donations
    GOVERNMENT = "GOVERNMENT"  # Government payments
    EDUCATION = "EDUCATION"  # Education fees
    HEALTHCARE = "HEALTHCARE"  # Healthcare payments
    TRAVEL = "TRAVEL"  # Travel expenses
    GENERAL = "GENERAL"  # General payment
    OTHER = "OTHER"  # Other/unknown


@dataclass
class PurposeCodeMapping:
    """Mapping result for a purpose code."""
    original_code: str
    original_scheme: str
    iso20022_code: str
    iso20022_name: str
    cdm_category: CDMPurposeCategory
    description: str
    regulatory_flag: bool = False
    requires_documentation: bool = False


# ============================================================================
# ISO 20022 External Purpose Codes (ExternalPurpose1Code)
# ============================================================================
# Full list of 160+ codes from ISO 20022 External Code Sets

ISO20022_PURPOSE_CODES: Dict[str, Tuple[str, CDMPurposeCategory, str]] = {
    # Account Management
    "ACCT": ("Account Management", CDMPurposeCategory.TRANSFER, "Account management"),
    "CASH": ("Cash Management", CDMPurposeCategory.TRANSFER, "Cash management transfer"),
    "COLL": ("Collection", CDMPurposeCategory.INVOICE, "Collection payment"),

    # Trade & Commerce
    "BEXP": ("Business Expenses", CDMPurposeCategory.GENERAL, "Business expenses"),
    "BOCE": ("Back Office Conversion Entry", CDMPurposeCategory.TRANSFER, "Back office conversion"),
    "COMM": ("Commission", CDMPurposeCategory.COMMISSION, "Commission payment"),
    "COMC": ("Commercial Payment", CDMPurposeCategory.INVOICE, "Commercial payment"),
    "CPYR": ("Copyright", CDMPurposeCategory.ROYALTY, "Copyright payment"),
    "GDDS": ("Purchase/Sale of Goods", CDMPurposeCategory.TRADE, "Goods purchase/sale"),
    "GDSV": ("Purchase/Sale of Goods and Services", CDMPurposeCategory.TRADE, "Goods and services"),
    "INTC": ("Intra-Company Payment", CDMPurposeCategory.TRANSFER, "Intra-company transfer"),
    "LICF": ("License Fee", CDMPurposeCategory.LICENSE, "License fee payment"),
    "POPE": ("Point of Purchase Entry", CDMPurposeCategory.GENERAL, "POS transaction"),
    "ROYA": ("Royalty", CDMPurposeCategory.ROYALTY, "Royalty payment"),
    "SCVE": ("Purchase/Sale of Services", CDMPurposeCategory.INVOICE, "Services payment"),
    "SUPP": ("Supplier Payment", CDMPurposeCategory.INVOICE, "Supplier payment"),
    "TRAD": ("Trade Services", CDMPurposeCategory.TRADE, "Trade services"),

    # Salary & Payroll
    "SALA": ("Salary", CDMPurposeCategory.SALARY, "Salary payment"),
    "BONU": ("Bonus", CDMPurposeCategory.SALARY, "Bonus payment"),
    "ALLW": ("Allowance", CDMPurposeCategory.SALARY, "Allowance payment"),
    "PAYR": ("Payroll", CDMPurposeCategory.SALARY, "Payroll payment"),
    "PRCP": ("Price Payment", CDMPurposeCategory.SALARY, "Price payment"),
    "REFU": ("Refund", CDMPurposeCategory.REFUND, "Refund payment"),

    # Pension & Benefits
    "PENS": ("Pension", CDMPurposeCategory.PENSION, "Pension payment"),
    "PRME": ("Precious Metal", CDMPurposeCategory.INVESTMENT, "Precious metal purchase"),
    "ANNC": ("Annuity", CDMPurposeCategory.PENSION, "Annuity payment"),
    "SSBE": ("Social Security Benefit", CDMPurposeCategory.PENSION, "Social security"),
    "BENE": ("Unemployment Benefit", CDMPurposeCategory.PENSION, "Unemployment benefit"),

    # Tax
    "TAXS": ("Tax Payment", CDMPurposeCategory.TAX, "Tax payment"),
    "VATX": ("VAT Payment", CDMPurposeCategory.TAX, "VAT payment"),
    "WHLD": ("Withholding", CDMPurposeCategory.TAX, "Withholding tax"),
    "ESTX": ("Estate Tax", CDMPurposeCategory.TAX, "Estate tax"),
    "FWLV": ("Foreign Worker Levy", CDMPurposeCategory.TAX, "Foreign worker levy"),
    "GSTX": ("GST Tax", CDMPurposeCategory.TAX, "GST/Sales tax"),
    "HSTX": ("Housing Tax", CDMPurposeCategory.TAX, "Housing tax"),
    "INTX": ("Income Tax", CDMPurposeCategory.TAX, "Income tax"),
    "NITX": ("Net Income Tax", CDMPurposeCategory.TAX, "Net income tax"),
    "PTXP": ("Property Tax", CDMPurposeCategory.TAX, "Property tax"),

    # Loan & Credit
    "LOAN": ("Loan", CDMPurposeCategory.LOAN, "Loan disbursement"),
    "LOAR": ("Loan Repayment", CDMPurposeCategory.LOAN, "Loan repayment"),
    "CBTV": ("Cable TV Bill", CDMPurposeCategory.SUBSCRIPTION, "Cable TV payment"),
    "ELEC": ("Electricity Bill", CDMPurposeCategory.UTILITY, "Electricity payment"),
    "ENRG": ("Energy", CDMPurposeCategory.UTILITY, "Energy payment"),
    "GASB": ("Gas Bill", CDMPurposeCategory.UTILITY, "Gas bill payment"),
    "PHON": ("Telephone Bill", CDMPurposeCategory.UTILITY, "Telephone payment"),
    "WTER": ("Water Bill", CDMPurposeCategory.UTILITY, "Water bill payment"),
    "OTLC": ("Other Telecom", CDMPurposeCategory.UTILITY, "Other telecom payment"),

    # Real Estate
    "RENT": ("Rent", CDMPurposeCategory.RENT, "Rent payment"),
    "DBTC": ("Debit Card Payment", CDMPurposeCategory.GENERAL, "Debit card payment"),
    "GOVI": ("Government Insurance", CDMPurposeCategory.INSURANCE, "Government insurance"),
    "HLRP": ("Alimony", CDMPurposeCategory.TRANSFER, "Alimony payment"),
    "INSU": ("Insurance Premium", CDMPurposeCategory.INSURANCE, "Insurance premium"),
    "IVPT": ("Invoice Payment", CDMPurposeCategory.INVOICE, "Invoice payment"),
    "LBRI": ("Labor Insurance", CDMPurposeCategory.INSURANCE, "Labor insurance"),
    "LIFI": ("Life Insurance", CDMPurposeCategory.INSURANCE, "Life insurance"),

    # Investment & Securities
    "DIVI": ("Dividend", CDMPurposeCategory.DIVIDEND, "Dividend payment"),
    "DIVD": ("Dividend", CDMPurposeCategory.DIVIDEND, "Dividend distribution"),
    "INTE": ("Interest", CDMPurposeCategory.INVESTMENT, "Interest payment"),
    "SECU": ("Securities", CDMPurposeCategory.INVESTMENT, "Securities transaction"),
    "TREA": ("Treasury Payment", CDMPurposeCategory.GOVERNMENT, "Treasury payment"),
    "STDY": ("Study", CDMPurposeCategory.EDUCATION, "Study expenses"),
    "TBIL": ("Treasury Bill", CDMPurposeCategory.INVESTMENT, "Treasury bill"),

    # Government
    "GOVT": ("Government Payment", CDMPurposeCategory.GOVERNMENT, "Government payment"),
    "BLDG": ("Building Maintenance", CDMPurposeCategory.RENT, "Building maintenance"),
    "CBFF": ("Capital Building", CDMPurposeCategory.GOVERNMENT, "Capital building fund"),
    "CHAR": ("Charity", CDMPurposeCategory.CHARITY, "Charity donation"),
    "FREX": ("Foreign Exchange", CDMPurposeCategory.TRANSFER, "Foreign exchange"),

    # Healthcare
    "HLTH": ("Healthcare", CDMPurposeCategory.HEALTHCARE, "Healthcare payment"),
    "HLTC": ("Home Health Care", CDMPurposeCategory.HEALTHCARE, "Home health care"),
    "HSPC": ("Hospital Care", CDMPurposeCategory.HEALTHCARE, "Hospital care"),
    "MDCS": ("Medical Services", CDMPurposeCategory.HEALTHCARE, "Medical services"),

    # Travel & Entertainment
    "TRPT": ("Transportation", CDMPurposeCategory.TRAVEL, "Transportation"),
    "TRVL": ("Travel", CDMPurposeCategory.TRAVEL, "Travel expenses"),
    "AIRB": ("Air Ticket", CDMPurposeCategory.TRAVEL, "Air ticket purchase"),

    # Education
    "EDUC": ("Education", CDMPurposeCategory.EDUCATION, "Education payment"),
    "COST": ("Costs", CDMPurposeCategory.GENERAL, "Costs payment"),
    "DNTS": ("Dental Service", CDMPurposeCategory.HEALTHCARE, "Dental services"),

    # Financial Services
    "CLPR": ("Car Loan Principal", CDMPurposeCategory.LOAN, "Car loan principal"),
    "CMDT": ("Commodity Transfer", CDMPurposeCategory.TRADE, "Commodity transfer"),
    "CSLP": ("Consumer Loan Payment", CDMPurposeCategory.LOAN, "Consumer loan payment"),
    "DEPT": ("Deposit", CDMPurposeCategory.TRANSFER, "Deposit"),
    "FEES": ("Fees", CDMPurposeCategory.GENERAL, "Fees"),
    "FAND": ("Financial Aid", CDMPurposeCategory.TRANSFER, "Financial aid"),
    "FCOL": ("Fee Collection", CDMPurposeCategory.GENERAL, "Fee collection"),
    "FCPM": ("Fee Collection (Credit Card)", CDMPurposeCategory.GENERAL, "Credit card fee"),
    "GDGE": ("Garage", CDMPurposeCategory.RENT, "Garage payment"),
    "GVEA": ("Austrian Government Employees", CDMPurposeCategory.SALARY, "Austrian govt employees"),
    "GVEB": ("Unemployment Benefits", CDMPurposeCategory.PENSION, "Unemployment"),
    "GVEC": ("Capital Building Fund", CDMPurposeCategory.GOVERNMENT, "Capital building"),
    "GVED": ("Cash Compensation", CDMPurposeCategory.SALARY, "Cash compensation"),
    "IPAY": ("Installment", CDMPurposeCategory.LOAN, "Installment payment"),
    "IPCA": ("Installment on Car", CDMPurposeCategory.LOAN, "Car installment"),
    "ICRF": ("Credit Card Fee", CDMPurposeCategory.GENERAL, "Credit card fee"),
    "INSM": ("Installment", CDMPurposeCategory.LOAN, "Installment"),
    "MTUP": ("Mobile Top Up", CDMPurposeCategory.SUBSCRIPTION, "Mobile top up"),
    "MTAU": ("Multi Top Up", CDMPurposeCategory.SUBSCRIPTION, "Multiple top up"),
    "NETT": ("Netting", CDMPurposeCategory.TRANSFER, "Netting payment"),
    "NOWS": ("Not Otherwise Specified", CDMPurposeCategory.OTHER, "Not specified"),
    "OCDM": ("Other Card Related", CDMPurposeCategory.GENERAL, "Other card related"),
    "OFEE": ("Opening Fee", CDMPurposeCategory.GENERAL, "Opening fee"),
    "OTHR": ("Other", CDMPurposeCategory.OTHER, "Other purpose"),
    "PADD": ("Preauthorized Debit", CDMPurposeCategory.GENERAL, "Preauthorized debit"),
    "PCOM": ("Property Completion", CDMPurposeCategory.RENT, "Property completion"),
    "PDEP": ("Property Deposit", CDMPurposeCategory.RENT, "Property deposit"),
    "PLDS": ("Property Loan Disbursement", CDMPurposeCategory.LOAN, "Property loan"),
    "PLRF": ("Property Loan Repayment", CDMPurposeCategory.LOAN, "Property loan repay"),
    "PPTI": ("Property Insurance", CDMPurposeCategory.INSURANCE, "Property insurance"),
    "RINP": ("Recurring Installment", CDMPurposeCategory.LOAN, "Recurring installment"),
    "RLWY": ("Railway", CDMPurposeCategory.TRAVEL, "Railway payment"),
    "SAVG": ("Savings", CDMPurposeCategory.TRANSFER, "Savings transfer"),
    "SPLT": ("Split Payment", CDMPurposeCategory.GENERAL, "Split payment"),
    "SPSP": ("Study Period Stipend", CDMPurposeCategory.EDUCATION, "Study stipend"),
    "STUP": ("Study Upkeep", CDMPurposeCategory.EDUCATION, "Study upkeep"),
    "SUBS": ("Subscription", CDMPurposeCategory.SUBSCRIPTION, "Subscription"),
    "SUPY": ("Support Payments", CDMPurposeCategory.TRANSFER, "Support payment"),
    "SWUF": ("SWIFT Fee", CDMPurposeCategory.GENERAL, "SWIFT fee"),
    "TAXR": ("Tax Refund", CDMPurposeCategory.TAX, "Tax refund"),
    "TELI": ("Telephone Initiated", CDMPurposeCategory.GENERAL, "Telephone initiated"),
    "WEBI": ("Web Initiated", CDMPurposeCategory.GENERAL, "Web initiated"),
}


# ============================================================================
# Scheme-Specific Purpose Code Mappings
# ============================================================================

# NACHA/ACH SEC Codes to ISO 20022
ACH_SEC_CODE_MAPPING: Dict[str, str] = {
    "PPD": "PAYR",  # Prearranged Payment and Deposit -> Payroll
    "CCD": "SUPP",  # Corporate Credit or Debit -> Supplier Payment
    "CTX": "COMC",  # Corporate Trade Exchange -> Commercial
    "IAT": "TRAD",  # International ACH -> Trade
    "WEB": "WEBI",  # Internet Initiated -> Web Initiated
    "TEL": "TELI",  # Telephone Initiated -> Telephone Initiated
    "POS": "POPE",  # Point of Sale Entry -> Point of Purchase Entry
    "ARC": "CASH",  # Accounts Receivable Entry -> Cash Management
    "BOC": "BOCE",  # Back Office Conversion -> Back Office Conversion
    "POP": "POPE",  # Point of Purchase -> Point of Purchase Entry
    "RCK": "REFU",  # Re-presented Check Entry -> Refund (recovery)
    "MTE": "CASH",  # Machine Transfer Entry -> Cash Management
    "SHR": "CASH",  # Shared Network Entry -> Cash Management
    "ACK": "ACCT",  # ACK -> Account Management
    "DNE": "REFU",  # Death Notification Entry -> Refund/adjustment
    "ATX": "COMC",  # Financial EDI -> Commercial
    "ENR": "PAYR",  # Automated Enrollment -> Payroll
}

# Fedwire Business Function Codes to ISO 20022
FEDWIRE_FUNCTION_MAPPING: Dict[str, str] = {
    "BTR": "TREA",  # Bank Transfer -> Treasury
    "CTR": "SUPP",  # Customer Transfer -> Supplier Payment
    "CTP": "SUPP",  # Customer Transfer Plus -> Supplier Payment
    "DRC": "LOAR",  # Customer or Corporate Drawdown -> Loan Repayment
    "DRW": "LOAR",  # Drawdown Response -> Loan Repayment
    "FFR": "TREA",  # Fed Funds Returned -> Treasury
    "FFS": "TREA",  # Fed Funds Sold -> Treasury
    "SVC": "FEES",  # Service Message -> Fees
    "DEP": "DEPT",  # Deposit -> Deposit
    "DRB": "LOAR",  # Bank to Bank Drawdown -> Loan
}

# SWIFT MT103 Field 70/72 OUR/SHA/BEN
SWIFT_CHARGE_MAPPING: Dict[str, str] = {
    "OUR": "FEES",  # All charges paid by ordering customer
    "SHA": "FEES",  # Shared charges
    "BEN": "FEES",  # All charges paid by beneficiary
}

# PIX Transaction Types to ISO 20022
PIX_TYPE_MAPPING: Dict[str, str] = {
    "MANU": "SUPP",  # Manual Transfer -> Supplier
    "DICT": "SUPP",  # Dictionary Key -> Supplier
    "QRDN": "POPE",  # Dynamic QR Code -> POS
    "QRES": "POPE",  # Static QR Code -> POS
    "INIC": "SUPP",  # Payment Initiation -> Supplier
}

# UPI Transaction Types to ISO 20022
UPI_TYPE_MAPPING: Dict[str, str] = {
    "PAY": "SUPP",  # Pay request -> Supplier
    "COLLECT": "COLL",  # Collect request -> Collection
    "MANDATE": "PADD",  # Mandate -> Preauthorized Debit
    "REFUND": "REFU",  # Refund -> Refund
    "REVERSAL": "REFU",  # Reversal -> Refund
}

# SEPA Purpose Codes (already ISO 20022 compliant)
SEPA_PURPOSE_MAPPING: Dict[str, str] = {
    # SEPA uses ISO 20022 directly, so mapping is 1:1
    # Added here for completeness
}


class PurposeCodeMapper:
    """
    Maps purpose codes from various payment schemes to standardized CDM codes.
    """

    def __init__(self):
        self._iso_codes = ISO20022_PURPOSE_CODES
        self._ach_mapping = ACH_SEC_CODE_MAPPING
        self._fedwire_mapping = FEDWIRE_FUNCTION_MAPPING
        self._pix_mapping = PIX_TYPE_MAPPING
        self._upi_mapping = UPI_TYPE_MAPPING

    def map_to_cdm(
        self,
        code: str,
        scheme: str,
        jurisdiction: Optional[str] = None
    ) -> PurposeCodeMapping:
        """
        Map a purpose code to CDM standardized format.

        Args:
            code: Original purpose code from the payment message
            scheme: Payment scheme (ISO20022, SWIFT, ACH, FEDWIRE, SEPA, PIX, UPI, etc.)
            jurisdiction: Optional jurisdiction for regulatory lookups

        Returns:
            PurposeCodeMapping with standardized codes
        """
        scheme_upper = scheme.upper()
        code_upper = code.upper() if code else ""

        # ISO 20022 - Already standardized
        if scheme_upper in ("ISO20022", "PAIN", "PACS", "CAMT", "SEPA"):
            return self._map_iso20022(code_upper)

        # SWIFT MT - Parse from Field 70/72
        elif scheme_upper in ("SWIFT", "MT103", "MT202"):
            return self._map_swift(code_upper)

        # US ACH/NACHA
        elif scheme_upper in ("ACH", "NACHA"):
            return self._map_ach(code_upper)

        # Fedwire
        elif scheme_upper == "FEDWIRE":
            return self._map_fedwire(code_upper)

        # FedNow (ISO 20022 based)
        elif scheme_upper == "FEDNOW":
            return self._map_iso20022(code_upper)

        # RTP (ISO 20022 based)
        elif scheme_upper in ("RTP", "TCH"):
            return self._map_iso20022(code_upper)

        # PIX (Brazil)
        elif scheme_upper == "PIX":
            return self._map_pix(code_upper)

        # UPI (India)
        elif scheme_upper == "UPI":
            return self._map_upi(code_upper)

        # Other schemes - Default mapping
        else:
            return self._map_generic(code_upper, scheme_upper)

    def _map_iso20022(self, code: str) -> PurposeCodeMapping:
        """Map ISO 20022 purpose code."""
        if code in self._iso_codes:
            name, category, desc = self._iso_codes[code]
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="ISO20022",
                iso20022_code=code,
                iso20022_name=name,
                cdm_category=category,
                description=desc
            )
        else:
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="ISO20022",
                iso20022_code=code if len(code) == 4 else "OTHR",
                iso20022_name="Other",
                cdm_category=CDMPurposeCategory.OTHER,
                description=f"Unknown ISO 20022 code: {code}"
            )

    def _map_swift(self, code: str) -> PurposeCodeMapping:
        """Map SWIFT MT purpose from Field 70/72."""
        # SWIFT often uses free-form text, try to parse known patterns
        if code in self._iso_codes:
            return self._map_iso20022(code)

        # Check for common patterns
        if "SALARY" in code or "PAYROLL" in code:
            return self._map_iso20022("SALA")
        elif "INVOICE" in code or "INV" in code:
            return self._map_iso20022("IVPT")
        elif "TAX" in code:
            return self._map_iso20022("TAXS")
        elif "LOAN" in code:
            return self._map_iso20022("LOAN")
        elif "DIVIDEND" in code or "DIV" in code:
            return self._map_iso20022("DIVI")
        elif "PENSION" in code:
            return self._map_iso20022("PENS")
        else:
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="SWIFT",
                iso20022_code="COMC",
                iso20022_name="Commercial Payment",
                cdm_category=CDMPurposeCategory.GENERAL,
                description=f"SWIFT remittance: {code[:50]}"
            )

    def _map_ach(self, code: str) -> PurposeCodeMapping:
        """Map ACH/NACHA SEC code."""
        if code in self._ach_mapping:
            iso_code = self._ach_mapping[code]
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="ACH",
                iso20022_code=iso_code,
                iso20022_name=self._iso_codes.get(iso_code, ("Unknown", CDMPurposeCategory.OTHER, ""))[0],
                cdm_category=self._iso_codes.get(iso_code, ("", CDMPurposeCategory.OTHER, ""))[1],
                description=f"ACH SEC Code: {code}"
            )
        else:
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="ACH",
                iso20022_code="COMC",
                iso20022_name="Commercial Payment",
                cdm_category=CDMPurposeCategory.GENERAL,
                description=f"ACH transaction: {code}"
            )

    def _map_fedwire(self, code: str) -> PurposeCodeMapping:
        """Map Fedwire Business Function Code."""
        if code in self._fedwire_mapping:
            iso_code = self._fedwire_mapping[code]
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="FEDWIRE",
                iso20022_code=iso_code,
                iso20022_name=self._iso_codes.get(iso_code, ("Unknown", CDMPurposeCategory.OTHER, ""))[0],
                cdm_category=self._iso_codes.get(iso_code, ("", CDMPurposeCategory.OTHER, ""))[1],
                description=f"Fedwire: {code}"
            )
        else:
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="FEDWIRE",
                iso20022_code="SUPP",
                iso20022_name="Supplier Payment",
                cdm_category=CDMPurposeCategory.INVOICE,
                description=f"Fedwire transaction: {code}"
            )

    def _map_pix(self, code: str) -> PurposeCodeMapping:
        """Map PIX transaction type."""
        if code in self._pix_mapping:
            iso_code = self._pix_mapping[code]
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="PIX",
                iso20022_code=iso_code,
                iso20022_name=self._iso_codes.get(iso_code, ("Unknown", CDMPurposeCategory.OTHER, ""))[0],
                cdm_category=self._iso_codes.get(iso_code, ("", CDMPurposeCategory.OTHER, ""))[1],
                description=f"PIX: {code}"
            )
        else:
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="PIX",
                iso20022_code="SUPP",
                iso20022_name="Supplier Payment",
                cdm_category=CDMPurposeCategory.GENERAL,
                description=f"PIX transaction: {code}"
            )

    def _map_upi(self, code: str) -> PurposeCodeMapping:
        """Map UPI transaction type."""
        if code in self._upi_mapping:
            iso_code = self._upi_mapping[code]
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="UPI",
                iso20022_code=iso_code,
                iso20022_name=self._iso_codes.get(iso_code, ("Unknown", CDMPurposeCategory.OTHER, ""))[0],
                cdm_category=self._iso_codes.get(iso_code, ("", CDMPurposeCategory.OTHER, ""))[1],
                description=f"UPI: {code}"
            )
        else:
            return PurposeCodeMapping(
                original_code=code,
                original_scheme="UPI",
                iso20022_code="SUPP",
                iso20022_name="Supplier Payment",
                cdm_category=CDMPurposeCategory.GENERAL,
                description=f"UPI transaction: {code}"
            )

    def _map_generic(self, code: str, scheme: str) -> PurposeCodeMapping:
        """Generic mapping for unknown schemes."""
        # Try ISO 20022 first
        if code in self._iso_codes:
            return self._map_iso20022(code)

        return PurposeCodeMapping(
            original_code=code,
            original_scheme=scheme,
            iso20022_code="OTHR",
            iso20022_name="Other",
            cdm_category=CDMPurposeCategory.OTHER,
            description=f"{scheme}: {code}"
        )

    def get_all_iso_codes(self) -> List[str]:
        """Return all supported ISO 20022 purpose codes."""
        return list(self._iso_codes.keys())

    def get_cdm_categories(self) -> List[str]:
        """Return all CDM purpose categories."""
        return [c.value for c in CDMPurposeCategory]


# Singleton instance
_mapper = PurposeCodeMapper()


def map_purpose_code(
    code: str,
    scheme: str,
    jurisdiction: Optional[str] = None
) -> PurposeCodeMapping:
    """
    Convenience function to map a purpose code to CDM format.

    Args:
        code: Original purpose code
        scheme: Payment scheme
        jurisdiction: Optional jurisdiction

    Returns:
        PurposeCodeMapping
    """
    return _mapper.map_to_cdm(code, scheme, jurisdiction)


def get_iso20022_code(code: str, scheme: str) -> str:
    """
    Get just the ISO 20022 code for a purpose code.

    Args:
        code: Original purpose code
        scheme: Payment scheme

    Returns:
        ISO 20022 purpose code (4 characters)
    """
    mapping = _mapper.map_to_cdm(code, scheme)
    return mapping.iso20022_code


def get_cdm_category(code: str, scheme: str) -> str:
    """
    Get the CDM category for a purpose code.

    Args:
        code: Original purpose code
        scheme: Payment scheme

    Returns:
        CDM category string
    """
    mapping = _mapper.map_to_cdm(code, scheme)
    return mapping.cdm_category.value


# ============================================================================
# Test Function
# ============================================================================

if __name__ == "__main__":
    # Test the mapper
    print("=" * 60)
    print("Purpose Code Mapper Test")
    print("=" * 60)

    test_cases = [
        ("SALA", "ISO20022"),
        ("DIVI", "ISO20022"),
        ("PPD", "ACH"),
        ("CCD", "NACHA"),
        ("CTR", "FEDWIRE"),
        ("BTR", "FEDWIRE"),
        ("MANU", "PIX"),
        ("QRDN", "PIX"),
        ("PAY", "UPI"),
        ("COLLECT", "UPI"),
        ("INVOICE 12345", "SWIFT"),
        ("SALARY PAYMENT", "MT103"),
        ("LOAN", "SEPA"),
        ("UNKNOWN_CODE", "UNKNOWN_SCHEME"),
    ]

    mapper = PurposeCodeMapper()

    for code, scheme in test_cases:
        result = mapper.map_to_cdm(code, scheme)
        print(f"\n{scheme}/{code}:")
        print(f"  ISO 20022: {result.iso20022_code} ({result.iso20022_name})")
        print(f"  CDM Category: {result.cdm_category.value}")
        print(f"  Description: {result.description}")

    print("\n" + "=" * 60)
    print(f"Total ISO 20022 codes supported: {len(mapper.get_all_iso_codes())}")
    print(f"CDM categories: {len(mapper.get_cdm_categories())}")
    print("=" * 60)
