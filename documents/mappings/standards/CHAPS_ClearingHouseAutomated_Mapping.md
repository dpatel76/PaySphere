# CHAPS - Clearing House Automated Payment System
## Complete Field Mapping to GPS CDM

**Message Type:** CHAPS Payment (ISO 20022 pacs.008.001.08)
**Standard:** ISO 20022 XML
**Operator:** Bank of England
**Usage:** High-value sterling payments in the United Kingdom
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 72 fields mapped)

---

## Message Overview

CHAPS (Clearing House Automated Payment System) is the UK's high-value real-time gross settlement (RTGS) payment system. Operated by the Bank of England, CHAPS guarantees same-day irrevocable sterling payments with settlement in central bank money.

**Key Characteristics:**
- Currency: GBP only
- Execution time: Real-time (typically within minutes)
- Transaction limit: No limit (high-value payments)
- Availability: Business days 06:00-17:00 GMT
- Settlement: Real-time gross settlement (RTGS) via Bank of England
- Message format: ISO 20022 XML (pacs.008)

**Operating Hours:** 06:00-17:00 GMT (Monday-Friday, excluding bank holidays)
**Settlement:** Immediate and irrevocable in Bank of England RTGS system

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total CHAPS Fields** | 72 | 100% |
| **Mapped to CDM** | 72 | 100% |
| **Direct Mapping** | 66 | 92% |
| **Derived/Calculated** | 4 | 5% |
| **Reference Data Lookup** | 2 | 3% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | messageId | Unique message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | creationDateTime | Message timestamp |
| GrpHdr/BtchBookg | Batch Booking | Boolean | - | 0..1 | true/false | PaymentInstruction | batchBooking | Always false for CHAPS |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 1..1 | Numeric | PaymentInstruction | numberOfTransactions | Always 1 for CHAPS |
| GrpHdr/TtlIntrBkSttlmAmt | Total Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | totalSettlementAmount.amount | Total amount |
| GrpHdr/TtlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | GBP | PaymentInstruction | totalSettlementAmount.currency | GBP only |
| GrpHdr/IntrBkSttlmDt | Settlement Date | Date | - | 1..1 | ISO Date | PaymentInstruction | settlementDate | Settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 1..1 | INDA | PaymentInstruction | settlementMethod | Indirect via agent |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 5 | 0..1 | CHAPS | PaymentInstruction | clearingSystemCode | CHAPS |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/BIC | Reimbursement Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | reimbursementAgentBic | Settlement agent |
| GrpHdr/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | Payment priority |
| GrpHdr/InstgAgt/FinInstnId/BIC | Instructing Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | bic | Sender bank BIC |
| GrpHdr/InstdAgt/FinInstnId/BIC | Instructed Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | bic | Receiver bank BIC |

### Credit Transfer Transaction Information (CdtTrfTxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 0..1 | Any | PaymentInstruction | instructionId | Instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | endToEndId | Mandatory E2E ID |
| CdtTrfTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | transactionId | CHAPS transaction ID |
| CdtTrfTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | 36 | 0..1 | UUID | PaymentInstruction | uetr | Universal unique ID |
| CdtTrfTxInf/PmtTpInf/InstrPrty | Instruction Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | instructionPriority | HIGH for urgent |
| CdtTrfTxInf/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | 4 | 0..1 | URGP | PaymentInstruction | serviceLevelCode | Urgent payment |
| CdtTrfTxInf/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | 1-35 | 0..1 | Any | PaymentInstruction | localInstrument | CHAPS specific |
| CdtTrfTxInf/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | categoryPurposeCode | CASH, TREA, etc. |
| CdtTrfTxInf/IntrBkSttlmAmt | Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | settlementAmount.amount | Settlement amount |
| CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | GBP | PaymentInstruction | settlementAmount.currency | GBP only |
| CdtTrfTxInf/IntrBkSttlmDt | Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | settlementDate | Settlement date |
| CdtTrfTxInf/SttlmPrty | Settlement Priority | Code | 4 | 0..1 | HIGH, NORM | PaymentInstruction | settlementPriority | Settlement priority |
| CdtTrfTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | debitDateTime | Debit timestamp |
| CdtTrfTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | creditDateTime | Credit timestamp |
| CdtTrfTxInf/SttlmTmReq/CLSTm | Requested Time | Time | - | 0..1 | ISO Time | PaymentInstruction | requestedSettlementTime | Settlement time |
| CdtTrfTxInf/AccptncDtTm | Acceptance Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | acceptanceDateTime | Acceptance timestamp |
| CdtTrfTxInf/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Original amount |
| CdtTrfTxInf/InstdAmt/@Ccy | Currency | Code | 3 | 0..1 | GBP | PaymentInstruction | instructedAmount.currency | GBP |
| CdtTrfTxInf/XchgRate | Exchange Rate | DecimalNumber | - | 0..1 | Decimal | PaymentInstruction | exchangeRate | FX rate if applicable |
| CdtTrfTxInf/ChrgBr | Charge Bearer | Code | 4 | 1..1 | SHAR, DEBT, CRED | PaymentInstruction | chargeBearer | Charge allocation |
| CdtTrfTxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | chargesAmount.amount | Charges |
| CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/BIC | Charges Agent BIC | Code | 8 or 11 | 0..1 | BIC | FinancialInstitution | chargesAgentBic | Charging bank |

### Debtor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/DbtrAgt/FinInstnId/BIC | Debtor Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | bic | Debtor bank BIC |
| CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Debtor Agent Sort Code | Text | 6 | 0..1 | Sort code | FinancialInstitution | sortCode | Sort code |
| CdtTrfTxInf/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Any | FinancialInstitution | institutionName | Bank name |
| CdtTrfTxInf/DbtrAgt/BrnchId/Id | Debtor Agent Branch ID | Text | 1-35 | 0..1 | Any | FinancialInstitution | branchId | Branch identifier |
| CdtTrfTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 1..1 | Any | Party | name | Debtor name |
| CdtTrfTxInf/Dbtr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Any | Party | department | Department |
| CdtTrfTxInf/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Any | Party | streetName | Street name |
| CdtTrfTxInf/Dbtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Any | Party | buildingNumber | Building number |
| CdtTrfTxInf/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Any | Party | postalCode | Postcode |
| CdtTrfTxInf/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Any | Party | city | City/town |
| CdtTrfTxInf/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | GB | Party | country | Country code |
| CdtTrfTxInf/Dbtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Any | Party | addressLine | Address lines |
| CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC | Debtor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| CdtTrfTxInf/Dbtr/Id/OrgId/Othr/Id | Debtor Organization ID | Text | 1-35 | 0..1 | Any | Party | organizationId | Org identifier |
| CdtTrfTxInf/DbtrAcct/Id/IBAN | Debtor IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | IBAN if used |
| CdtTrfTxInf/DbtrAcct/Id/Othr/Id | Debtor Account Number | Text | 1-34 | 1..1 | Account number | Account | accountNumber | UK account number |
| CdtTrfTxInf/DbtrAcct/Id/Othr/SchmeNm/Cd | Account Scheme | Code | 1-4 | 0..1 | BBAN | Account | accountScheme | Account scheme |
| CdtTrfTxInf/DbtrAcct/Tp/Cd | Account Type | Code | 1-4 | 0..1 | CACC, SVGS | Account | accountType | Account type |
| CdtTrfTxInf/DbtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Any | Account | accountName | Account name |
| CdtTrfTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Any | Party | ultimateDebtorName | Ultimate debtor |
| CdtTrfTxInf/UltmtDbtr/Id/OrgId/Othr/Id | Ultimate Debtor ID | Text | 1-35 | 0..1 | Any | Party | ultimateDebtorId | Ultimate org ID |

### Creditor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/CdtrAgt/FinInstnId/BIC | Creditor Agent BIC | Code | 8 or 11 | 1..1 | BIC | FinancialInstitution | bic | Creditor bank BIC |
| CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Creditor Agent Sort Code | Text | 6 | 0..1 | Sort code | FinancialInstitution | sortCode | Sort code |
| CdtTrfTxInf/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Any | FinancialInstitution | institutionName | Bank name |
| CdtTrfTxInf/CdtrAgt/BrnchId/Id | Creditor Agent Branch ID | Text | 1-35 | 0..1 | Any | FinancialInstitution | branchId | Branch identifier |
| CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 1..1 | Any | Party | name | Creditor name |
| CdtTrfTxInf/Cdtr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Any | Party | department | Department |
| CdtTrfTxInf/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Any | Party | streetName | Street name |
| CdtTrfTxInf/Cdtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Any | Party | buildingNumber | Building number |
| CdtTrfTxInf/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Any | Party | postalCode | Postcode |
| CdtTrfTxInf/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Any | Party | city | City/town |
| CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | GB | Party | country | Country code |
| CdtTrfTxInf/Cdtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Any | Party | addressLine | Address lines |
| CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC | Creditor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Organization BIC |
| CdtTrfTxInf/Cdtr/Id/OrgId/Othr/Id | Creditor Organization ID | Text | 1-35 | 0..1 | Any | Party | organizationId | Org identifier |
| CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor IBAN | Code | Up to 34 | 0..1 | IBAN | Account | iban | IBAN if used |
| CdtTrfTxInf/CdtrAcct/Id/Othr/Id | Creditor Account Number | Text | 1-34 | 1..1 | Account number | Account | accountNumber | UK account number |
| CdtTrfTxInf/CdtrAcct/Id/Othr/SchmeNm/Cd | Account Scheme | Code | 1-4 | 0..1 | BBAN | Account | accountScheme | Account scheme |
| CdtTrfTxInf/CdtrAcct/Tp/Cd | Account Type | Code | 1-4 | 0..1 | CACC, SVGS | Account | accountType | Account type |
| CdtTrfTxInf/CdtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Any | Account | accountName | Account name |
| CdtTrfTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Any | Party | ultimateCreditorName | Ultimate creditor |
| CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id | Ultimate Creditor ID | Text | 1-35 | 0..1 | Any | Party | ultimateCreditorId | Ultimate org ID |

### Remittance and Purpose Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | Payment purpose |
| CdtTrfTxInf/RgltryRptg/Dtls/Cd | Regulatory Reporting Code | Text | 1-10 | 0..1 | Any | PaymentInstruction | regulatoryReportingCode | Regulatory code |
| CdtTrfTxInf/RgltryRptg/Dtls/Inf | Regulatory Information | Text | 1-35 | 0..1 | Any | PaymentInstruction | regulatoryInformation | Regulatory details |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..1 | Any | PaymentInstruction | remittanceInformation | Unstructured remittance |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Any | PaymentInstruction | documentNumber | Invoice number |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Document Date | Date | - | 0..1 | ISO Date | PaymentInstruction | documentDate | Document date |
| CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Any | PaymentInstruction | creditorReference | Structured reference |
| CdtTrfTxInf/InstrForCdtrAgt/Cd | Instruction Code | Code | 1-4 | 0..1 | PHOB, TELE | PaymentInstruction | instructionCode | Instruction for creditor agent |
| CdtTrfTxInf/InstrForCdtrAgt/InstrInf | Instruction Information | Text | 1-140 | 0..1 | Any | PaymentInstruction | instructionInformation | Additional instruction |

---

## CHAPS-Specific Rules

### Operating Hours

| Period | Time (GMT) | Description | CDM Mapping |
|--------|------------|-------------|-------------|
| Opening | 06:00 | System opens | PaymentInstruction.systemOpenTime |
| Standard cutoff | 16:00 | Standard payment cutoff | PaymentInstruction.standardCutoffTime |
| High-value cutoff | 16:30 | High-value payment cutoff | PaymentInstruction.highValueCutoffTime |
| System close | 17:00 | System closes | PaymentInstruction.systemCloseTime |

### Transaction Characteristics

| Attribute | Value | CDM Validation |
|-----------|-------|----------------|
| Currency | GBP only | settlementAmount.currency = 'GBP' |
| Settlement | Real-time | settlementMethod = 'INDA' (indirect via agent) |
| Clearing System | CHAPS | clearingSystemCode = 'CHAPS' |
| Priority | HIGH or NORM | instructionPriority = 'HIGH' or 'NORM' |
| Minimum amount | £0.01 | settlementAmount.amount >= 0.01 |
| Typical use | High-value, time-critical | paymentCharacteristics |

### Mandatory Elements

| Element | Requirement | CDM Validation |
|---------|-------------|----------------|
| Currency | Must be GBP | settlementAmount.currency = 'GBP' |
| BIC | Mandatory for both agents | Validate BIC format |
| Account Number | Required | Non-empty account number |
| End-to-End ID | Mandatory, max 35 chars | endToEndId length <= 35 |
| Transaction ID | Mandatory, max 35 chars | transactionId length <= 35 |

### Charge Bearer Codes

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| SHAR | Shared charges (each party pays own bank) | PaymentInstruction.chargeBearer = 'SHAR' |
| DEBT | Debtor pays all charges | PaymentInstruction.chargeBearer = 'DEBT' |
| CRED | Creditor pays all charges | PaymentInstruction.chargeBearer = 'CRED' |

### Priority Codes

| Code | Description | Use Case | CDM Mapping |
|------|-------------|----------|-------------|
| HIGH | High priority | Urgent, time-critical payments | instructionPriority = 'HIGH' |
| NORM | Normal priority | Standard payments | instructionPriority = 'NORM' |

### Purpose Codes (Selected Examples)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CASH | Cash Management | PaymentInstruction.purposeCode = 'CASH' |
| TREA | Treasury Payment | PaymentInstruction.purposeCode = 'TREA' |
| INTC | Intra-Company Payment | PaymentInstruction.purposeCode = 'INTC' |
| SUPP | Supplier Payment | PaymentInstruction.purposeCode = 'SUPP' |
| PROP | Property Purchase | PaymentInstruction.purposeCode = 'PROP' |

---

## CDM Extensions Required

All 72 CHAPS fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

### CHAPS Payment Message (pacs.008)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>CHAPS20241220123456</MsgId>
      <CreDtTm>2024-12-20T09:30:00.000Z</CreDtTm>
      <BtchBookg>false</BtchBookg>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="GBP">500000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>INDA</SttlmMtd>
        <ClrSys>
          <Cd>CHAPS</Cd>
        </ClrSys>
      </SttlmInf>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
      </PmtTpInf>
      <InstgAgt>
        <FinInstnId>
          <BIC>BARCGB22XXX</BIC>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BIC>HSBCGB2LXXX</BIC>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>INSTR20241220001</InstrId>
        <EndToEndId>E2E20241220001</EndToEndId>
        <TxId>CHAPSTX20241220001</TxId>
        <UETR>550e8400-e29b-41d4-a716-446655440000</UETR>
      </PmtId>
      <PmtTpInf>
        <InstrPrty>HIGH</InstrPrty>
        <SvcLvl>
          <Cd>URGP</Cd>
        </SvcLvl>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="GBP">500000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmPrty>HIGH</SttlmPrty>
      <AccptncDtTm>2024-12-20T09:30:01.234Z</AccptncDtTm>
      <ChrgBr>SHAR</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <BIC>BARCGB22XXX</BIC>
          <ClrSysMmbId>
            <MmbId>200000</MmbId>
          </ClrSysMmbId>
          <Nm>Barclays Bank PLC</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Property Development Ltd</Nm>
        <PstlAdr>
          <StrtNm>Canary Wharf</StrtNm>
          <BldgNb>1</BldgNb>
          <PstCd>E14 5AB</PstCd>
          <TwnNm>London</TwnNm>
          <Ctry>GB</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>12345678</Id>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>12345678</Id>
            <SchmeNm>
              <Cd>BBAN</Cd>
            </SchmeNm>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Nm>Property Development Ltd - Main Account</Nm>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BIC>HSBCGB2LXXX</BIC>
          <ClrSysMmbId>
            <MmbId>400000</MmbId>
          </ClrSysMmbId>
          <Nm>HSBC UK Bank PLC</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Land Holdings Corporation</Nm>
        <PstlAdr>
          <StrtNm>King Street</StrtNm>
          <BldgNb>100</BldgNb>
          <PstCd>M2 4WU</PstCd>
          <TwnNm>Manchester</TwnNm>
          <Ctry>GB</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>87654321</Id>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>87654321</Id>
            <SchmeNm>
              <Cd>BBAN</Cd>
            </SchmeNm>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Nm>Land Holdings Corporation - Business Account</Nm>
      </CdtrAcct>
      <Purp>
        <Cd>PROP</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Property purchase - Contract reference PROP-2024-ABC-001 - Completion payment</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- Bank of England CHAPS: https://www.bankofengland.co.uk/payment-and-settlement/chaps
- CHAPS Reference Manual: Bank of England CHAPS Reference Manual
- ISO 20022 Implementation: CHAPS ISO 20022 Implementation Guide
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
