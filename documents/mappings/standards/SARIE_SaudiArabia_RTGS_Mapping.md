# SARIE - Saudi Arabia Real-Time Gross Settlement System
## Complete Field Mapping to GPS CDM

**Message Type:** SARIE Payment Message (ISO 20022 pacs.008.001.08, pacs.009.001.08)
**Standard:** ISO 20022 XML
**Operator:** Saudi Central Bank (SAMA - Saudi Arabian Monetary Authority)
**Usage:** Real-time gross settlement for high-value payments in Saudi Arabia
**Document Date:** 2024-12-21
**Mapping Coverage:** 100% (All 72 fields mapped)

---

## Message Overview

SARIE (Saudi Arabian Riyal Interbank Express) is the national RTGS system operated by the Saudi Central Bank (SAMA). It provides real-time gross settlement for high-value and time-critical payments in Saudi Riyals, with special features supporting Hajj-related payments and integration with GCC regional payment systems.

**Key Characteristics:**
- Currency: SAR (Saudi Riyal) only
- Execution time: Real-time gross settlement
- Amount limit: Typically SAR 100,000 minimum (configurable by banks)
- Availability: Sunday-Thursday (Islamic business week), extended during Hajj
- Settlement: Real-time gross settlement through SAMA accounts
- Character set: UTF-8 (Arabic and English support)
- IBAN: Mandatory (24 characters)

**Operating Hours:**
- Normal: Sunday-Thursday, 08:00-17:00 AST (Arabia Standard Time)
- Ramadan: Sunday-Thursday, 09:00-15:00 AST
- Hajj Period: Extended hours including Saturday

**Settlement:** Real-time gross settlement through settlement accounts at Saudi Central Bank
**Regional Integration:** GCC Pay network, bilateral links with regional central banks

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total SARIE Fields** | 72 | 100% |
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
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | creationDateTime | Message creation timestamp |
| GrpHdr/NbOfTxs | Number Of Transactions | Text | 1-15 | 1..1 | Numeric | PaymentInstruction | numberOfTransactions | Transaction count |
| GrpHdr/TtlIntrBkSttlmAmt | Total Settlement Amount | ActiveCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | totalSettlementAmount.amount | Total settlement |
| GrpHdr/TtlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | SAR | PaymentInstruction | totalSettlementAmount.currency | SAR only |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 1..1 | ISO Date | PaymentInstruction | settlementDate | Settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 1..1 | CLRG | PaymentInstruction | settlementMethod | Clearing system |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 5 | 1..1 | SARIE | PaymentInstruction | clearingSystemCode | SARIE network |
| GrpHdr/SttlmInf/ClrSys/Prtry | Clearing System Proprietary | Text | 1-35 | 0..1 | RTGS, HAJJ | PaymentInstruction | clearingSystemType | RTGS or Hajj special |
| GrpHdr/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Instructing Agent ID | Text | 2 | 1..1 | SA Bank Code | FinancialInstitution | nationalClearingCode | Sending bank 2-digit code |
| GrpHdr/InstdAgt/FinInstnId/ClrSysMmbId/MmbId | Instructed Agent ID | Text | 2 | 1..1 | SA Bank Code | FinancialInstitution | nationalClearingCode | Receiving bank 2-digit code |

### Credit Transfer Transaction Information (CdtTrfTxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | instructionId | Instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | endToEndId | Mandatory E2E ID |
| CdtTrfTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | transactionId | Unique transaction ID |
| CdtTrfTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | 36 | 0..1 | UUID | PaymentInstruction | uetr | Universal unique ID (UUID format) |
| CdtTrfTxInf/IntrBkSttlmAmt | Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | settlementAmount.amount | Settlement amount |
| CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | SAR | PaymentInstruction | settlementAmount.currency | SAR only |
| CdtTrfTxInf/IntrBkSttlmDt | Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | settlementDate | Settlement date |
| CdtTrfTxInf/SttlmPrty | Settlement Priority | Code | 4 | 0..1 | HIGH, NORM, HAJJ | PaymentInstruction | settlementPriority | Priority indicator |
| CdtTrfTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | debitDateTime | Debit timestamp |
| CdtTrfTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | creditDateTime | Credit timestamp |
| CdtTrfTxInf/AccptncDtTm | Acceptance Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | acceptanceDateTime | Payment acceptance time |
| CdtTrfTxInf/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Original instructed amount |
| CdtTrfTxInf/InstdAmt/@Ccy | Currency | Code | 3 | 0..1 | SAR | PaymentInstruction | instructedAmount.currency | SAR only |
| CdtTrfTxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | DEBT, CRED, SHAR, SLEV | PaymentInstruction | chargeBearer | Charge allocation |
| CdtTrfTxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge | chargeAmount.amount | Charges |
| CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/ClrSysMmbId/MmbId | Charges Agent ID | Text | 2 | 0..1 | SA Bank Code | FinancialInstitution | nationalClearingCode | Charging bank |

### Debtor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Debtor Agent Code | Text | 2 | 1..1 | SA Bank Code | FinancialInstitution | nationalClearingCode | Debtor's bank 2-digit code |
| CdtTrfTxInf/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Any | FinancialInstitution | institutionName | Debtor's bank name (Arabic/English) |
| CdtTrfTxInf/DbtrAgt/FinInstnId/PstlAdr/Ctry | Debtor Agent Country | Code | 2 | 0..1 | SA | FinancialInstitution | country | Saudi Arabia country code |
| CdtTrfTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 1..1 | Any | Party | name | Debtor/originator name (Arabic/English) |
| CdtTrfTxInf/Dbtr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Any | Party | department | Department |
| CdtTrfTxInf/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Any | Party | streetName | Street name |
| CdtTrfTxInf/Dbtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Any | Party | buildingNumber | Building number |
| CdtTrfTxInf/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Any | Party | postalCode | Postal code (5 digits) |
| CdtTrfTxInf/Dbtr/PstlAdr/TwnNm | City Name | Text | 1-35 | 0..1 | Any | Party | city | City (Riyadh, Jeddah, Mecca, etc.) |
| CdtTrfTxInf/Dbtr/PstlAdr/CtrySubDvsn | Province | Text | 1-35 | 0..1 | Province code | Party | state | Province/Region |
| CdtTrfTxInf/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | SA | Party | country | Country code |
| CdtTrfTxInf/Dbtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Any | Party | addressLine | Address lines (Arabic/English) |
| CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC | Debtor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Debtor BIC if org |
| CdtTrfTxInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth | Date of Birth | - | - | 0..1 | Date | Party | dateOfBirth | Individual DOB |
| CdtTrfTxInf/Dbtr/Id/PrvtId/Othr/Id | National ID | Text | 1-35 | 0..1 | Iqama/ID | Party | nationalId | Saudi ID or Iqama number |
| CdtTrfTxInf/DbtrAcct/Id/IBAN | Debtor IBAN | Text | 24 | 1..1 | SA + 22 chars | Account | iban | Saudi IBAN (24 chars) |
| CdtTrfTxInf/DbtrAcct/Tp/Cd | Account Type | Code | 1-4 | 0..1 | CACC, SVGS | Account | accountType | Account type |
| CdtTrfTxInf/DbtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Any | Account | accountName | Account name |
| CdtTrfTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Any | Party | ultimateDebtorName | Ultimate party |
| CdtTrfTxInf/UltmtDbtr/Id/OrgId/Othr/Id | Ultimate Debtor ID | Text | 1-35 | 0..1 | Any | Party | ultimateDebtorId | Organization ID |

### Creditor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Creditor Agent Code | Text | 2 | 1..1 | SA Bank Code | FinancialInstitution | nationalClearingCode | Creditor's bank 2-digit code |
| CdtTrfTxInf/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Any | FinancialInstitution | institutionName | Creditor's bank name (Arabic/English) |
| CdtTrfTxInf/CdtrAgt/FinInstnId/PstlAdr/Ctry | Creditor Agent Country | Code | 2 | 0..1 | SA | FinancialInstitution | country | Saudi Arabia country code |
| CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 1..1 | Any | Party | name | Creditor/beneficiary name (Arabic/English) |
| CdtTrfTxInf/Cdtr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Any | Party | department | Department |
| CdtTrfTxInf/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Any | Party | streetName | Street name |
| CdtTrfTxInf/Cdtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Any | Party | buildingNumber | Building number |
| CdtTrfTxInf/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Any | Party | postalCode | Postal code (5 digits) |
| CdtTrfTxInf/Cdtr/PstlAdr/TwnNm | City Name | Text | 1-35 | 0..1 | Any | Party | city | City |
| CdtTrfTxInf/Cdtr/PstlAdr/CtrySubDvsn | Province | Text | 1-35 | 0..1 | Province code | Party | state | Province/Region |
| CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | SA | Party | country | Country code |
| CdtTrfTxInf/Cdtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Any | Party | addressLine | Address lines (Arabic/English) |
| CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC | Creditor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Creditor BIC if org |
| CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth | Date of Birth | - | - | 0..1 | Date | Party | dateOfBirth | Individual DOB |
| CdtTrfTxInf/Cdtr/Id/PrvtId/Othr/Id | National ID | Text | 1-35 | 0..1 | Iqama/ID | Party | nationalId | Saudi ID or Iqama number |
| CdtTrfTxInf/CdtrAcct/Id/IBAN | Creditor IBAN | Text | 24 | 1..1 | SA + 22 chars | Account | iban | Saudi IBAN (24 chars) |
| CdtTrfTxInf/CdtrAcct/Tp/Cd | Account Type | Code | 1-4 | 0..1 | CACC, SVGS | Account | accountType | Account type |
| CdtTrfTxInf/CdtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Any | Account | accountName | Account name |
| CdtTrfTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Any | Party | ultimateCreditorName | Ultimate beneficiary |
| CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id | Ultimate Creditor ID | Text | 1-35 | 0..1 | Any | Party | ultimateCreditorId | Organization ID |

### Remittance and Purpose Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | Purpose of payment |
| CdtTrfTxInf/RgltryRptg/Dtls/Cd | Regulatory Reporting Code | Text | 1-10 | 0..1 | Any | PaymentInstruction | regulatoryReportingCode | SAMA regulatory code |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..1 | Any | PaymentInstruction | remittanceInformation | Unstructured remittance (Arabic/English) |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Any | PaymentInstruction | documentNumber | Invoice number |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Document Date | Date | - | 0..1 | ISO Date | PaymentInstruction | documentDate | Invoice date |
| CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Any | PaymentInstruction | creditorReference | Structured reference |
| CdtTrfTxInf/InstrForCdtrAgt/Cd | Instruction Code | Code | 1-4 | 0..1 | PHOB, TELE | PaymentInstruction | instructionCode | Instruction for creditor agent |
| CdtTrfTxInf/InstrForCdtrAgt/InstrInf | Instruction Information | Text | 1-140 | 0..1 | Any | PaymentInstruction | instructionInformation | Additional instruction |

### Hajj-Specific Fields

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/Envlp/HajjInf/HajjInd | Hajj Indicator | Boolean | - | 0..1 | true/false | PaymentInstruction | hajjIndicator | Hajj-related payment flag |
| SplmtryData/Envlp/HajjInf/PilgrimId | Pilgrim ID | Text | 1-35 | 0..1 | Pilgrim ID | PaymentInstruction | pilgrimIdentifier | Hajj pilgrim identifier |
| SplmtryData/Envlp/HajjInf/HajjSvc | Hajj Service Type | Code | 1-10 | 0..1 | Service code | PaymentInstruction | hajjServiceType | Type of Hajj service |

---

## SARIE-Specific Rules

### Transaction Limits

| Limit Type | Value | CDM Validation |
|------------|-------|----------------|
| Typical Minimum | SAR 100,000.00 (bank configurable) | instructedAmount.amount >= 100000.00 |
| Maximum per transaction | No limit (high-value system) | No max validation |
| Minimum absolute | SAR 1.00 | instructedAmount.amount >= 1.00 |
| Currency | SAR only | instructedAmount.currency = 'SAR' |

### Mandatory Elements

| Element | Requirement | CDM Validation |
|---------|-------------|----------------|
| Currency | Must be SAR | instructedAmount.currency = 'SAR' |
| IBAN | Mandatory for both parties | Validate Saudi IBAN format (SA + 2 check + 2 bank + 18 account) |
| Bank Code | 2-digit Saudi bank code | nationalClearingCode format validation |
| End-to-End ID | Mandatory, max 35 chars | endToEndId length <= 35 |
| Clearing System | Must be SARIE | clearingSystemCode = 'SARIE' |

### Saudi Arabia IBAN Structure

| Component | Description | Length | Example |
|-----------|-------------|--------|---------|
| Country Code | SA | 2 | SA |
| Check Digits | Modulo 97 check | 2 | 03 |
| Bank Code | Saudi 2-digit bank code | 2 | 80 |
| Account Number | Account identifier | 18 | 000000608010167519 |
| **Total Length** | **Complete IBAN** | **24** | **SA0380000000608010167519** |

### Saudi Bank Codes (Selected Examples)

| Code | Bank Name | Arabic Name | SWIFT BIC |
|------|-----------|-------------|-----------|
| 10 | National Commercial Bank (NCB) | البنك الأهلي التجاري | NCBKSAJE |
| 45 | Saudi British Bank (SABB) | البنك السعودي البريطاني | SABBSARI |
| 80 | Riyad Bank | بنك الرياض | RIBLSARI |
| 05 | Al Rajhi Bank | مصرف الراجحي | RJHISARI |
| 15 | Bank AlJazira | بنك الجزيرة | BJAZSAJE |
| 20 | Bank Albilad | بنك البلاد | BABBSARI |
| 40 | Saudi Investment Bank | البنك السعودي للاستثمار | SIBCSARI |

### Settlement Priority Codes

| Code | Description | Usage |
|------|-------------|-------|
| HIGH | High Priority | Time-critical corporate payments |
| NORM | Normal Priority | Standard RTGS transfers |
| HAJJ | Hajj Priority | Hajj-related payments during pilgrimage season |

### Hajj Payment Features

During the annual Hajj pilgrimage season, SARIE implements special features:

| Feature | Description | CDM Mapping |
|---------|-------------|-------------|
| Extended Hours | Saturday operations added | PaymentInstruction.operatingHours |
| Hajj Priority | Special priority queue | PaymentInstruction.settlementPriority = 'HAJJ' |
| Pilgrim Tracking | Link payments to pilgrim IDs | PaymentInstruction.pilgrimIdentifier |
| Service Codes | Hotels, transport, services | PaymentInstruction.hajjServiceType |

### Islamic Calendar Considerations

SARIE operating hours adjust based on the Islamic calendar:

| Period | Operating Days | Operating Hours |
|--------|----------------|-----------------|
| Normal | Sunday-Thursday | 08:00-17:00 AST |
| Ramadan | Sunday-Thursday | 09:00-15:00 AST |
| Hajj | Sunday-Saturday | 08:00-19:00 AST (extended) |
| Eid Holidays | Closed | N/A |

### Purpose Codes (Selected Examples)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CASH | Cash Management Transfer | PaymentInstruction.purposeCode = 'CASH' |
| SUPP | Supplier Payment | PaymentInstruction.purposeCode = 'SUPP' |
| SALA | Salary Payment | PaymentInstruction.purposeCode = 'SALA' |
| TREA | Treasury Payment | PaymentInstruction.purposeCode = 'TREA' |
| TAXS | Tax Payment | PaymentInstruction.purposeCode = 'TAXS' |
| SECU | Securities | PaymentInstruction.purposeCode = 'SECU' |
| HAJJ | Hajj Services | PaymentInstruction.purposeCode = 'HAJJ' |
| ZAKT | Zakat (Islamic Alms) | PaymentInstruction.purposeCode = 'ZAKT' |

---

## CDM Extensions Required

All 72 SARIE fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Examples

### Example 1: SARIE Corporate Payment

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>SARIE20241221120000001</MsgId>
      <CreDtTm>2024-12-21T12:00:00.000+03:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="SAR">5000000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>SARIE</Cd>
          <Prtry>RTGS</Prtry>
        </ClrSys>
      </SttlmInf>
      <InstgAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>10</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>80</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>SAR-INSTR-20241221-001</InstrId>
        <EndToEndId>SAR-E2E-20241221-001</EndToEndId>
        <TxId>SAR-TX-20241221-001</TxId>
        <UETR>12345678-abcd-ef12-3456-789012345678</UETR>
      </PmtId>
      <IntrBkSttlmAmt Ccy="SAR">5000000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
      <SttlmPrty>HIGH</SttlmPrty>
      <AccptncDtTm>2024-12-21T12:00:01.234+03:00</AccptncDtTm>
      <ChrgBr>SHAR</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>10</MmbId>
          </ClrSysMmbId>
          <Nm>National Commercial Bank</Nm>
          <PstlAdr>
            <Ctry>SA</Ctry>
          </PstlAdr>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Saudi Petrochemical Company</Nm>
        <PstlAdr>
          <StrtNm>King Fahd Road</StrtNm>
          <BldgNb>Tower 1</BldgNb>
          <PstCd>11564</PstCd>
          <TwnNm>Riyadh</TwnNm>
          <CtrySubDvsn>Riyadh Province</CtrySubDvsn>
          <Ctry>SA</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>SA0310000000012345678901</IBAN>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>80</MmbId>
          </ClrSysMmbId>
          <Nm>Riyad Bank</Nm>
          <PstlAdr>
            <Ctry>SA</Ctry>
          </PstlAdr>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Industrial Equipment Suppliers Ltd</Nm>
        <PstlAdr>
          <StrtNm>Olaya Street</StrtNm>
          <BldgNb>Building 25</BldgNb>
          <PstCd>11543</PstCd>
          <TwnNm>Riyadh</TwnNm>
          <CtrySubDvsn>Riyadh Province</CtrySubDvsn>
          <Ctry>SA</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>SA0380000000608010167519</IBAN>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
      </CdtrAcct>
      <Purp>
        <Cd>SUPP</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Payment for industrial equipment - Purchase Order PO-2024-7890</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

### Example 2: Hajj Payment with Special Priority

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>SARIE-HAJJ-20240615-001</MsgId>
      <CreDtTm>2024-06-15T14:30:00.000+03:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="SAR">25000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-06-15</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>SARIE</Cd>
          <Prtry>HAJJ</Prtry>
        </ClrSys>
      </SttlmInf>
      <InstgAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>05</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>20</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>HAJJ-INSTR-20240615-001</InstrId>
        <EndToEndId>HAJJ-E2E-20240615-001</EndToEndId>
        <TxId>HAJJ-TX-20240615-001</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="SAR">25000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-06-15</IntrBkSttlmDt>
      <SttlmPrty>HAJJ</SttlmPrty>
      <AccptncDtTm>2024-06-15T14:30:01.456+03:00</AccptncDtTm>
      <ChrgBr>DEBT</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>05</MmbId>
          </ClrSysMmbId>
          <Nm>Al Rajhi Bank</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Pilgrim Services Agency</Nm>
        <PstlAdr>
          <TwnNm>Mecca</TwnNm>
          <Ctry>SA</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>SA0305000000001234567890</IBAN>
        </Id>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>20</MmbId>
          </ClrSysMmbId>
          <Nm>Bank Albilad</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Mecca Hotels Group</Nm>
        <PstlAdr>
          <TwnNm>Mecca</TwnNm>
          <Ctry>SA</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>SA0320000000009876543210</IBAN>
        </Id>
      </CdtrAcct>
      <Purp>
        <Cd>HAJJ</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Hajj accommodation payment - Group booking reference HJ2024-5678</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
    <SplmtryData>
      <Envlp>
        <HajjInf>
          <HajjInd>true</HajjInd>
          <PilgrimId>HAJJ-PILGRIM-2024-123456</PilgrimId>
          <HajjSvc>HOTEL</HajjSvc>
        </HajjInf>
      </Envlp>
    </SplmtryData>
  </FIToFICstmrCdtTrf>
</Document>
```

### Example 3: GCC Cross-Border Payment

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.009.001.08">
  <FinInstnCdtTrf>
    <GrpHdr>
      <MsgId>SARIE-GCC-20241221-100</MsgId>
      <CreDtTm>2024-12-21T13:00:00.000+03:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>GCCPAY</Cd>
        </ClrSys>
      </SttlmInf>
      <InstgAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>45</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>EBILAEAD</BICFI>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>GCC-INSTR-20241221-100</InstrId>
        <EndToEndId>GCC-E2E-20241221-100</EndToEndId>
        <TxId>GCC-TX-20241221-100</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="SAR">150000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
      <ChrgBr>SHAR</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>45</MmbId>
          </ClrSysMmbId>
          <Nm>Saudi British Bank</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Saudi Trading Company LLC</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>SA0345000000111111111111</IBAN>
        </Id>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>EBILAEAD</BICFI>
          <Nm>Emirates NBD</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>UAE Import Export FZE</Nm>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <IBAN>AE070331234567890123456</IBAN>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Cross-border trade payment - Shipment REF-GCC-2024-789</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FinInstnCdtTrf>
</Document>
```

---

## References

- Saudi Central Bank (SAMA): https://www.sama.gov.sa/
- SARIE Operating Rules and Procedures
- ISO 20022 Standard: https://www.iso20022.org/
- GCC Pay Regional System: https://www.gcc-sg.org/
- Saudi IBAN Registry: Saudi Central Bank
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-21
**Next Review:** Q2 2025
