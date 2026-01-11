# Legacy Format to ISO 20022 Intelligent Mapping Implementation Plan

## Executive Summary

This document outlines the implementation plan for intelligently mapping legacy payment formats to their appropriate ISO 20022 message types. The key insight is that **legacy formats support multiple message subtypes that must route to DIFFERENT ISO message types** based on transaction characteristics.

## Current State Analysis

### Formats Already ISO 20022 Native (No Mapping Required)
| Format | Status | Notes |
|--------|--------|-------|
| MT103/MT202 | Migrated Nov 2025 | Maps to pacs.008/pacs.009 |
| PIX (Brazil) | Native ISO | pacs.008, pacs.002, pacs.004 |
| PayNow/FAST (Singapore) | Native ISO | pacs.008 based |
| PromptPay (Thailand) | Native ISO | pacs.008 based |
| SARIE (Saudi Arabia) | Native ISO | pacs.008, pacs.009 |
| BOJNET (Japan) | Migrated Nov 2025 | ISO native |
| BAHTNET (Thailand) | Migrated Aug 2022 | ISO native |

### TRUE Legacy Formats Requiring Intelligent Mapping
| Format | Priority | Complexity | Key Challenge |
|--------|----------|------------|---------------|
| **US ACH** | HIGH | HIGH | Multiple SEC codes map to different ISO messages |
| **UK BACS** | MEDIUM | MEDIUM | Credit vs Debit routing |
| **UPI (India)** | HIGH | HIGH | Uses ISO 8583, NOT ISO 20022 |
| **CNAPS (China)** | MEDIUM | MEDIUM | Proprietary format |
| **KFTC (Korea)** | LOW | LOW | Migration in progress (2026) |
| **MT940** | LOW | LOW | Statement format → camt.053 |

---

## Implementation Architecture

### Phase 1: Subtype Detection Framework

#### 1.1 Message Subtype Enum
```python
# src/gps_cdm/message_formats/base/message_subtypes.py

from enum import Enum

class MessageSubtype(Enum):
    """Standardized message subtypes for routing decisions."""

    # Credit Transfer Types
    CREDIT_TRANSFER_CUSTOMER = "CREDIT_TRANSFER_CUSTOMER"      # → pacs.008
    CREDIT_TRANSFER_FI = "CREDIT_TRANSFER_FI"                  # → pacs.009
    CREDIT_TRANSFER_BULK = "CREDIT_TRANSFER_BULK"              # → pain.001

    # Debit Types
    DIRECT_DEBIT_INITIATION = "DIRECT_DEBIT_INITIATION"        # → pain.008
    DIRECT_DEBIT_EXECUTION = "DIRECT_DEBIT_EXECUTION"          # → pacs.003

    # Status/Return Types
    PAYMENT_RETURN = "PAYMENT_RETURN"                          # → pacs.004
    PAYMENT_STATUS = "PAYMENT_STATUS"                          # → pacs.002
    PAYMENT_REJECTION = "PAYMENT_REJECTION"                    # → pain.002

    # Statement Types
    ACCOUNT_STATEMENT = "ACCOUNT_STATEMENT"                    # → camt.053
    ACCOUNT_REPORT = "ACCOUNT_REPORT"                          # → camt.052
    DEBIT_CREDIT_NOTIFICATION = "DEBIT_CREDIT_NOTIFICATION"    # → camt.054

    # Unknown/Default
    UNKNOWN = "UNKNOWN"
```

#### 1.2 Subtype Detector Interface
```python
# src/gps_cdm/message_formats/base/subtype_detector.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from .message_subtypes import MessageSubtype

class SubtypeDetector(ABC):
    """Base class for format-specific subtype detection."""

    @abstractmethod
    def detect_subtype(self, raw_content: str, parsed_data: Dict[str, Any]) -> Tuple[MessageSubtype, str]:
        """
        Detect the message subtype from raw or parsed content.

        Returns:
            Tuple of (MessageSubtype, iso_target_format)
            e.g., (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")
        """
        pass

    @abstractmethod
    def get_routing_key(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        """
        Get a routing key for conditional mapping lookup.

        Returns:
            String key for mapping lookup, e.g., "ACH_CCD_CREDIT"
        """
        pass
```

### Phase 2: Format-Specific Subtype Detectors

#### 2.1 ACH Subtype Detector
```python
# src/gps_cdm/message_formats/ach/subtype_detector.py

class ACHSubtypeDetector(SubtypeDetector):
    """
    ACH SEC Code to ISO 20022 Message Type Mapping.

    SEC Code Categories:
    - CREDIT: CCD, CTX, PPD (single), IAT → pacs.008 / pain.001
    - DEBIT: PPD, CCD (when debit), WEB, TEL → pain.008
    - RETURN: Return entries (addenda code) → pacs.004
    - REJECT: NOC entries → pain.002
    """

    # SEC codes that are typically credits
    CREDIT_SEC_CODES = {'CCD', 'CTX', 'PPD', 'IAT', 'CIE', 'MTE', 'POS', 'SHR'}

    # SEC codes that are typically debits
    DEBIT_SEC_CODES = {'PPD', 'CCD', 'WEB', 'TEL', 'ARC', 'BOC', 'POP', 'RCK'}

    # Transaction codes for credits (22, 23, 24, 32, 33, 34)
    CREDIT_TRANSACTION_CODES = {'22', '23', '24', '32', '33', '34'}

    # Transaction codes for debits (27, 28, 29, 37, 38, 39)
    DEBIT_TRANSACTION_CODES = {'27', '28', '29', '37', '38', '39'}

    # Return transaction codes (21, 26, 31, 36)
    RETURN_TRANSACTION_CODES = {'21', '26', '31', '36'}

    def detect_subtype(self, raw_content: str, parsed_data: Dict[str, Any]) -> Tuple[MessageSubtype, str]:
        sec_code = parsed_data.get('standard_entry_class') or self._extract_sec_code(raw_content)
        transaction_code = parsed_data.get('transaction_code') or self._extract_transaction_code(raw_content)

        # Check for return entries first
        if transaction_code in self.RETURN_TRANSACTION_CODES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        # Check transaction code for credit vs debit
        if transaction_code in self.CREDIT_TRANSACTION_CODES:
            # Bulk file with multiple entries → pain.001
            if self._is_bulk_file(raw_content):
                return (MessageSubtype.CREDIT_TRANSFER_BULK, "pain.001")
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if transaction_code in self.DEBIT_TRANSACTION_CODES:
            return (MessageSubtype.DIRECT_DEBIT_INITIATION, "pain.008")

        # Fallback to SEC code analysis
        if sec_code in self.CREDIT_SEC_CODES:
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if sec_code in self.DEBIT_SEC_CODES:
            return (MessageSubtype.DIRECT_DEBIT_INITIATION, "pain.008")

        return (MessageSubtype.UNKNOWN, "pacs.008")  # Default

    def get_routing_key(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        subtype, iso_format = self.detect_subtype(raw_content, parsed_data)
        sec_code = parsed_data.get('standard_entry_class', 'UNK')
        return f"ACH_{sec_code}_{subtype.name}"

    def _extract_sec_code(self, raw_content: str) -> str:
        """Extract SEC code from batch header (position 51-53)."""
        lines = raw_content.split('\n')
        for line in lines:
            if line.startswith('5'):  # Batch header
                if len(line) >= 53:
                    return line[50:53].strip()
        return 'UNK'

    def _extract_transaction_code(self, raw_content: str) -> str:
        """Extract transaction code from entry detail (position 2-3)."""
        lines = raw_content.split('\n')
        for line in lines:
            if line.startswith('6'):  # Entry detail
                if len(line) >= 3:
                    return line[1:3]
        return ''

    def _is_bulk_file(self, raw_content: str) -> bool:
        """Check if file contains multiple entry records."""
        entry_count = sum(1 for line in raw_content.split('\n') if line.startswith('6'))
        return entry_count > 1
```

#### 2.2 BACS Subtype Detector
```python
# src/gps_cdm/message_formats/bacs/subtype_detector.py

class BACSSubtypeDetector(SubtypeDetector):
    """
    BACS Transaction Type to ISO 20022 Mapping.

    Transaction Types:
    - 99: Credit (BACS Credit) → pacs.008
    - 01: Debit (Direct Debit) → pain.008
    - 17: Credit (Faster Payment fallback) → pacs.008
    - 18/19: Debit variations → pain.008
    """

    CREDIT_TRANSACTION_TYPES = {'99', '17', 'CR'}
    DEBIT_TRANSACTION_TYPES = {'01', '18', '19', 'DR'}

    def detect_subtype(self, raw_content: str, parsed_data: Dict[str, Any]) -> Tuple[MessageSubtype, str]:
        transaction_type = parsed_data.get('transaction_type') or self._extract_transaction_type(raw_content)

        if transaction_type in self.CREDIT_TRANSACTION_TYPES:
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if transaction_type in self.DEBIT_TRANSACTION_TYPES:
            return (MessageSubtype.DIRECT_DEBIT_INITIATION, "pain.008")

        return (MessageSubtype.UNKNOWN, "pacs.008")

    def get_routing_key(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        transaction_type = parsed_data.get('transaction_type', 'UNK')
        return f"BACS_{transaction_type}_{subtype.name}"

    def _extract_transaction_type(self, raw_content: str) -> str:
        """Extract transaction type from BACS record."""
        # BACS uses fixed-width format with transaction type at specific position
        lines = raw_content.split('\n')
        for line in lines:
            if len(line) >= 18 and not line.startswith('VOL') and not line.startswith('HDR'):
                return line[16:18].strip()
        return 'UNK'
```

#### 2.3 UPI Subtype Detector (ISO 8583 Based)
```python
# src/gps_cdm/message_formats/upi/subtype_detector.py

class UPISubtypeDetector(SubtypeDetector):
    """
    UPI (ISO 8583) to ISO 20022 Mapping.

    UPI uses ISO 8583 Message Type Indicators (MTI):
    - 0200/0210: Financial Transaction → pacs.008
    - 0420/0430: Reversal → pacs.004
    - 0100/0110: Authorization → pain.001 (initiation)
    - 0400/0410: Cancellation → camt.056

    Processing Codes (Field 3):
    - 00: Purchase/Credit Push → pacs.008
    - 01: Cash Withdrawal → pacs.008
    - 20: Refund → pacs.004
    - 40: Account Transfer → pacs.008
    """

    # MTI to message type mapping
    MTI_CREDIT_TYPES = {'0200', '0210', '0100', '0110'}
    MTI_REVERSAL_TYPES = {'0420', '0430', '0400', '0410'}

    # Processing code prefixes
    CREDIT_PROCESSING_CODES = {'00', '01', '40'}
    REFUND_PROCESSING_CODES = {'20'}

    def detect_subtype(self, raw_content: str, parsed_data: Dict[str, Any]) -> Tuple[MessageSubtype, str]:
        mti = parsed_data.get('message_type_indicator') or parsed_data.get('mti')
        processing_code = parsed_data.get('processing_code', '')[:2]  # First 2 digits

        # Check for reversal/refund
        if mti in self.MTI_REVERSAL_TYPES or processing_code in self.REFUND_PROCESSING_CODES:
            return (MessageSubtype.PAYMENT_RETURN, "pacs.004")

        # Standard credit transactions
        if mti in self.MTI_CREDIT_TYPES or processing_code in self.CREDIT_PROCESSING_CODES:
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        return (MessageSubtype.UNKNOWN, "pacs.008")

    def get_routing_key(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        mti = parsed_data.get('message_type_indicator', 'UNK')
        return f"UPI_{mti}_{subtype.name}"
```

#### 2.4 CNAPS Subtype Detector
```python
# src/gps_cdm/message_formats/cnaps/subtype_detector.py

class CNAPSSubtypeDetector(SubtypeDetector):
    """
    CNAPS (China) Message Type to ISO 20022 Mapping.

    CNAPS Message Types:
    - HVPS: High Value Payment System → pacs.008/pacs.009
    - BEPS: Bulk Electronic Payment System → pain.001
    - IBPS: Internet Banking Payment System → pacs.008
    - CCPC: Check Clearing → camt.053 (settlement)
    """

    HVPS_MESSAGE_TYPES = {'HVPS', 'hvps', 'HIGH_VALUE'}
    BEPS_MESSAGE_TYPES = {'BEPS', 'beps', 'BULK'}
    IBPS_MESSAGE_TYPES = {'IBPS', 'ibps', 'INTERNET'}

    def detect_subtype(self, raw_content: str, parsed_data: Dict[str, Any]) -> Tuple[MessageSubtype, str]:
        message_type = parsed_data.get('message_type') or parsed_data.get('system_type', '')

        if message_type.upper() in {'HVPS', 'HIGH_VALUE'}:
            # Check if FI-to-FI or customer payment
            if parsed_data.get('is_fi_payment', False):
                return (MessageSubtype.CREDIT_TRANSFER_FI, "pacs.009")
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        if message_type.upper() in {'BEPS', 'BULK'}:
            return (MessageSubtype.CREDIT_TRANSFER_BULK, "pain.001")

        if message_type.upper() in {'IBPS', 'INTERNET'}:
            return (MessageSubtype.CREDIT_TRANSFER_CUSTOMER, "pacs.008")

        return (MessageSubtype.UNKNOWN, "pacs.008")

    def get_routing_key(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        subtype, _ = self.detect_subtype(raw_content, parsed_data)
        system_type = parsed_data.get('system_type', 'UNK')
        return f"CNAPS_{system_type}_{subtype.name}"
```

### Phase 3: Routing Integration

#### 3.1 Enhanced Extractor Base Class
```python
# src/gps_cdm/message_formats/base/extractor.py (modifications)

class BaseExtractor(ABC):
    """Enhanced base extractor with subtype detection."""

    def __init__(self):
        self.subtype_detector: Optional[SubtypeDetector] = None
        self._detected_subtype: Optional[MessageSubtype] = None
        self._target_iso_format: Optional[str] = None

    def detect_and_route(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        """
        Detect message subtype and determine target ISO format.

        Returns:
            Target ISO format identifier (e.g., "pacs.008", "pain.008")
        """
        if self.subtype_detector:
            self._detected_subtype, self._target_iso_format = \
                self.subtype_detector.detect_subtype(raw_content, parsed_data)
        else:
            self._detected_subtype = MessageSubtype.UNKNOWN
            self._target_iso_format = self._default_iso_format()

        return self._target_iso_format

    def get_routing_key(self, raw_content: str, parsed_data: Dict[str, Any]) -> str:
        """Get routing key for conditional mapping lookup."""
        if self.subtype_detector:
            return self.subtype_detector.get_routing_key(raw_content, parsed_data)
        return self.MESSAGE_TYPE

    @abstractmethod
    def _default_iso_format(self) -> str:
        """Return default ISO format when subtype detection fails."""
        pass
```

#### 3.2 Conditional Mapping Support
```sql
-- Add routing_key column to gold_field_mappings
ALTER TABLE mapping.gold_field_mappings
ADD COLUMN IF NOT EXISTS routing_key VARCHAR(100);

-- Example: ACH credit mappings
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, routing_key, is_active)
VALUES
    ('ACH', 'cdm_pacs_fi_customer_credit_transfer', 'message_id', 'batch_id', NULL, 'ACH_CCD_CREDIT_TRANSFER_CUSTOMER', true),
    ('ACH', 'cdm_pacs_fi_customer_credit_transfer', 'amount', 'amount', NULL, 'ACH_CCD_CREDIT_TRANSFER_CUSTOMER', true);

-- Example: ACH debit mappings (to different table)
INSERT INTO mapping.gold_field_mappings
    (format_id, gold_table, gold_column, source_expression, entity_role, routing_key, is_active)
VALUES
    ('ACH', 'cdm_pain_direct_debit_initiation', 'message_id', 'batch_id', NULL, 'ACH_PPD_DIRECT_DEBIT_INITIATION', true),
    ('ACH', 'cdm_pain_direct_debit_initiation', 'amount', 'amount', NULL, 'ACH_PPD_DIRECT_DEBIT_INITIATION', true);
```

#### 3.3 DynamicGoldMapper Enhancement
```python
# src/gps_cdm/orchestration/dynamic_gold_mapper.py (modifications)

class DynamicGoldMapper:
    """Enhanced mapper with routing key support."""

    def _load_mappings(self, format_id: str, routing_key: Optional[str] = None) -> Dict:
        """Load mappings filtered by routing key if provided."""
        query = """
            SELECT gold_table, gold_column, source_expression, entity_role,
                   transform_expression, default_value
            FROM mapping.gold_field_mappings
            WHERE format_id = %s
              AND is_active = true
              AND (routing_key IS NULL OR routing_key = %s OR %s IS NULL)
            ORDER BY gold_table, entity_role NULLS FIRST, gold_column
        """
        # ... execute query with routing_key parameter
```

### Phase 4: Test File Strategy

#### 4.1 Test File Naming Convention
```
{FORMAT}-{SUBTYPE}-e2e-test.{ext}

Examples:
- ACH-CCD-CREDIT-e2e-test.ach      (CCD credit → pacs.008)
- ACH-PPD-DEBIT-e2e-test.ach       (PPD debit → pain.008)
- ACH-RETURN-e2e-test.ach          (Return → pacs.004)
- BACS-CREDIT-e2e-test.txt         (Credit → pacs.008)
- BACS-DEBIT-e2e-test.txt          (Debit → pain.008)
- UPI-PAY-e2e-test.json            (Payment → pacs.008)
- UPI-REFUND-e2e-test.json         (Refund → pacs.004)
```

#### 4.2 Required Test Files Per Format

| Format | Test Files Needed | Target ISO |
|--------|-------------------|------------|
| **ACH** | ACH-CCD-CREDIT, ACH-PPD-DEBIT, ACH-RETURN | pacs.008, pain.008, pacs.004 |
| **BACS** | BACS-CREDIT, BACS-DEBIT | pacs.008, pain.008 |
| **UPI** | UPI-PAY, UPI-REFUND | pacs.008, pacs.004 |
| **CNAPS** | CNAPS-HVPS, CNAPS-BEPS | pacs.008, pain.001 |
| **KFTC** | KFTC-CREDIT | pacs.008 |
| **MT940** | MT940-STATEMENT | camt.053 |

### Phase 5: Implementation Timeline

#### Week 1: Framework Setup
1. Create `message_subtypes.py` enum
2. Create `SubtypeDetector` base class
3. Implement ACH subtype detector (highest priority)
4. Add `routing_key` column to database

#### Week 2: Detector Implementation
1. Implement BACS subtype detector
2. Implement UPI subtype detector
3. Implement CNAPS subtype detector
4. Create test files for each subtype

#### Week 3: Integration
1. Enhance `BaseExtractor` with routing support
2. Modify `DynamicGoldMapper` for conditional mappings
3. Update zone_consumers to pass routing context
4. Add database mappings with routing keys

#### Week 4: Testing & Validation
1. Run E2E tests for all subtypes
2. Validate correct table routing
3. Fix any mapping gaps
4. Document final coverage

---

## Database Schema Changes

### New Tables
```sql
-- Subtype routing rules
CREATE TABLE IF NOT EXISTS mapping.subtype_routing_rules (
    rule_id SERIAL PRIMARY KEY,
    format_id VARCHAR(50) NOT NULL,
    subtype_code VARCHAR(50) NOT NULL,           -- e.g., "CCD_CREDIT"
    subtype_description VARCHAR(255),
    target_iso_format VARCHAR(50) NOT NULL,      -- e.g., "pacs.008"
    target_gold_table VARCHAR(100) NOT NULL,     -- e.g., "cdm_pacs_fi_customer_credit_transfer"
    detection_expression TEXT,                    -- JSON expression for detection logic
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (format_id, subtype_code)
);

-- Populate with initial rules
INSERT INTO mapping.subtype_routing_rules (format_id, subtype_code, target_iso_format, target_gold_table) VALUES
    ('ACH', 'CCD_CREDIT', 'pacs.008', 'cdm_pacs_fi_customer_credit_transfer'),
    ('ACH', 'CTX_CREDIT', 'pacs.008', 'cdm_pacs_fi_customer_credit_transfer'),
    ('ACH', 'PPD_DEBIT', 'pain.008', 'cdm_pain_direct_debit_initiation'),
    ('ACH', 'CCD_DEBIT', 'pain.008', 'cdm_pain_direct_debit_initiation'),
    ('ACH', 'RETURN', 'pacs.004', 'cdm_pacs_payment_return'),
    ('BACS', 'CREDIT', 'pacs.008', 'cdm_pacs_fi_customer_credit_transfer'),
    ('BACS', 'DEBIT', 'pain.008', 'cdm_pain_direct_debit_initiation'),
    ('UPI', 'PAY', 'pacs.008', 'cdm_pacs_fi_customer_credit_transfer'),
    ('UPI', 'REFUND', 'pacs.004', 'cdm_pacs_payment_return'),
    ('CNAPS', 'HVPS', 'pacs.008', 'cdm_pacs_fi_customer_credit_transfer'),
    ('CNAPS', 'BEPS', 'pain.001', 'cdm_pain_customer_credit_transfer_initiation');
```

### Modified Tables
```sql
-- Add routing_key to gold_field_mappings
ALTER TABLE mapping.gold_field_mappings
ADD COLUMN IF NOT EXISTS routing_key VARCHAR(100);

-- Add index for routing_key lookups
CREATE INDEX IF NOT EXISTS idx_gold_mappings_routing
ON mapping.gold_field_mappings (format_id, routing_key)
WHERE is_active = true;
```

---

## Success Criteria

1. **Subtype Detection Accuracy**: ≥99% correct classification for all legacy formats
2. **Routing Correctness**: 100% of messages route to correct ISO target table
3. **Test Coverage**: All subtypes have dedicated test files
4. **E2E Pass Rate**: 100% of subtype test files pass Bronze→Silver→Gold
5. **No Data Loss**: All source fields preserved in either CDM tables or extension tables

---

## Appendix A: ACH SEC Code Reference

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

## Appendix B: UPI Message Type Indicators (MTI)

| MTI | Description | ISO Target |
|-----|-------------|------------|
| 0100 | Authorization Request | pain.001 |
| 0110 | Authorization Response | pain.002 |
| 0200 | Financial Request | pacs.008 |
| 0210 | Financial Response | pacs.002 |
| 0400 | Reversal Request | pacs.004 |
| 0410 | Reversal Response | pacs.002 |
| 0420 | Reversal Advice | pacs.004 |
| 0430 | Reversal Advice Response | pacs.002 |

## Appendix C: BACS Transaction Types

| Type | Description | ISO Target |
|------|-------------|------------|
| 99 | BACS Credit | pacs.008 |
| 01 | Direct Debit | pain.008 |
| 17 | Faster Payment Credit | pacs.008 |
| 18 | Direct Debit (variation) | pain.008 |
| 19 | Direct Debit (variation) | pain.008 |
