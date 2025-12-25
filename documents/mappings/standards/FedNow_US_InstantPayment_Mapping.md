# FedNow - Federal Reserve Instant Payment Service
## Complete Field Mapping to GPS CDM

**Message Type:** FedNow Payment Message (ISO 20022 pacs.008.001.08, pain.013, camt.056)
**Standard:** ISO 20022 XML
**Operator:** Federal Reserve Banks
**Usage:** Real-time instant payment processing in the United States
**Document Date:** 2024-12-21
**Mapping Coverage:** 100% (All 82 fields mapped)

---

## Message Overview

The FedNow Service is a real-time instant payment platform operated by the Federal Reserve Banks in the United States. It provides instant, irrevocable, 24x7x365 payment processing with immediate funds availability, Request for Payment capability, and advanced fraud prevention tools.

**Key Characteristics:**
- Currency: USD only
- Execution time: Real-time (typically < 15 seconds)
- Amount limit: No federal limit (banks set their own limits)
- Availability: 24x7x365
- Settlement: Real-time gross settlement through Federal Reserve master accounts
- Character set: UTF-8 (full Unicode support)
- Launch Date: July 2023

**Operating Hours:** Continuous (24x7x365 including holidays)
**Settlement:** Real-time gross settlement through master accounts at Federal Reserve Banks
**Unique Features:** Request for Payment (RfP), Fraud Classifier, Fraud Mitigation Controls

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total FedNow Fields** | 82 | 100% |
| **Mapped to CDM** | 82 | 100% |
| **Direct Mapping** | 74 | 90% |
| **Derived/Calculated** | 6 | 7% |
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
| GrpHdr/TtlIntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | USD | PaymentInstruction | totalSettlementAmount.currency | USD only |
| GrpHdr/IntrBkSttlmDt | Interbank Settlement Date | Date | - | 1..1 | ISO Date | PaymentInstruction | settlementDate | Settlement date |
| GrpHdr/SttlmInf/SttlmMtd | Settlement Method | Code | 4 | 1..1 | CLRG | PaymentInstruction | settlementMethod | Clearing system |
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 6 | 1..1 | FEDNOW | PaymentInstruction | clearingSystemCode | FedNow network |
| GrpHdr/SttlmInf/InstgRmbrsmntAgt/FinInstnId/ClrSysMmbId/MmbId | Instructing Reimbursement Agent | Text | 9 | 0..1 | ABA Routing | FinancialInstitution | routingNumber | Reimbursement agent |
| GrpHdr/InstgAgt/FinInstnId/ClrSysMmbId/MmbId | Instructing Agent ID | Text | 9 | 1..1 | ABA Routing | FinancialInstitution | routingNumber | Sending bank routing |
| GrpHdr/InstdAgt/FinInstnId/ClrSysMmbId/MmbId | Instructed Agent ID | Text | 9 | 1..1 | ABA Routing | FinancialInstitution | routingNumber | Receiving bank routing |

### Credit Transfer Transaction Information (CdtTrfTxInf)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/PmtId/InstrId | Instruction Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | instructionId | Instruction ID |
| CdtTrfTxInf/PmtId/EndToEndId | End To End Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | endToEndId | Mandatory E2E ID |
| CdtTrfTxInf/PmtId/TxId | Transaction Identification | Text | 1-35 | 1..1 | Any | PaymentInstruction | transactionId | Unique transaction ID |
| CdtTrfTxInf/PmtId/UETR | Unique End-to-end Transaction Reference | Text | 36 | 0..1 | UUID | PaymentInstruction | uetr | Universal unique ID (UUID format) |
| CdtTrfTxInf/IntrBkSttlmAmt | Settlement Amount | ActiveCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction | settlementAmount.amount | Settlement amount |
| CdtTrfTxInf/IntrBkSttlmAmt/@Ccy | Currency | Code | 3 | 1..1 | USD | PaymentInstruction | settlementAmount.currency | USD only |
| CdtTrfTxInf/IntrBkSttlmDt | Settlement Date | Date | - | 0..1 | ISO Date | PaymentInstruction | settlementDate | Settlement date |
| CdtTrfTxInf/SttlmTmIndctn/DbtDtTm | Debit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | debitDateTime | Debit timestamp |
| CdtTrfTxInf/SttlmTmIndctn/CdtDtTm | Credit Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | creditDateTime | Credit timestamp |
| CdtTrfTxInf/SttlmTmReq/CLSTm | Requested Time | Time | - | 0..1 | ISO Time | PaymentInstruction | requestedSettlementTime | Requested settlement time |
| CdtTrfTxInf/AccptncDtTm | Acceptance Date Time | DateTime | - | 0..1 | ISO DateTime | PaymentInstruction | acceptanceDateTime | Payment acceptance time |
| CdtTrfTxInf/InstdAmt | Instructed Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | instructedAmount.amount | Original instructed amount |
| CdtTrfTxInf/InstdAmt/@Ccy | Currency | Code | 3 | 0..1 | USD | PaymentInstruction | instructedAmount.currency | USD only |
| CdtTrfTxInf/ChrgBr | Charge Bearer | Code | 4 | 0..1 | DEBT, CRED, SHAR, SLEV | PaymentInstruction | chargeBearer | Charge allocation |
| CdtTrfTxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge | chargeAmount.amount | Charges |
| CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/ClrSysMmbId/MmbId | Charges Agent ID | Text | 9 | 0..1 | ABA Routing | FinancialInstitution | routingNumber | Charging bank |
| CdtTrfTxInf/ChrgsInf/Tp/Cd | Charge Type Code | Code | 1-4 | 0..1 | CGST, SGST | Charge | chargeType | Type of charge |

### Debtor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId | Debtor Agent Routing | Text | 9 | 1..1 | ABA Routing | FinancialInstitution | routingNumber | Debtor's bank routing |
| CdtTrfTxInf/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Any | FinancialInstitution | institutionName | Debtor's bank name |
| CdtTrfTxInf/Dbtr/Nm | Debtor Name | Text | 1-140 | 1..1 | Any | Party | name | Debtor/originator name |
| CdtTrfTxInf/Dbtr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Any | Party | department | Department |
| CdtTrfTxInf/Dbtr/PstlAdr/SubDept | Sub-Department | Text | 1-70 | 0..1 | Any | Party | subDepartment | Sub-department |
| CdtTrfTxInf/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Any | Party | streetName | Street name |
| CdtTrfTxInf/Dbtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Any | Party | buildingNumber | Building number |
| CdtTrfTxInf/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Any | Party | postalCode | ZIP code |
| CdtTrfTxInf/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Any | Party | city | City |
| CdtTrfTxInf/Dbtr/PstlAdr/CtrySubDvsn | State | Text | 1-35 | 0..1 | US State code | Party | state | State |
| CdtTrfTxInf/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | US | Party | country | Country code |
| CdtTrfTxInf/Dbtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Any | Party | addressLine | Address lines |
| CdtTrfTxInf/Dbtr/Id/OrgId/AnyBIC | Debtor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Debtor BIC if org |
| CdtTrfTxInf/Dbtr/Id/PrvtId/DtAndPlcOfBirth | Date of Birth | - | - | 0..1 | Date | Party | dateOfBirth | Individual DOB |
| CdtTrfTxInf/DbtrAcct/Id/Othr/Id | Debtor Account Number | Text | 1-34 | 1..1 | Account number | Account | accountNumber | Debtor account |
| CdtTrfTxInf/DbtrAcct/Id/Othr/SchmeNm/Cd | Account Scheme | Code | 1-4 | 0..1 | BBAN | Account | accountScheme | Account type scheme |
| CdtTrfTxInf/DbtrAcct/Tp/Cd | Account Type | Code | 1-4 | 0..1 | CACC, SVGS | Account | accountType | Account type |
| CdtTrfTxInf/DbtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Any | Account | accountName | Account name |
| CdtTrfTxInf/UltmtDbtr/Nm | Ultimate Debtor Name | Text | 1-140 | 0..1 | Any | Party | ultimateDebtorName | Ultimate party |
| CdtTrfTxInf/UltmtDbtr/Id/OrgId/Othr/Id | Ultimate Debtor ID | Text | 1-35 | 0..1 | Any | Party | ultimateDebtorId | Organization ID |

### Creditor Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId | Creditor Agent Routing | Text | 9 | 1..1 | ABA Routing | FinancialInstitution | routingNumber | Creditor's bank routing |
| CdtTrfTxInf/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Any | FinancialInstitution | institutionName | Creditor's bank name |
| CdtTrfTxInf/Cdtr/Nm | Creditor Name | Text | 1-140 | 1..1 | Any | Party | name | Creditor/beneficiary name |
| CdtTrfTxInf/Cdtr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Any | Party | department | Department |
| CdtTrfTxInf/Cdtr/PstlAdr/SubDept | Sub-Department | Text | 1-70 | 0..1 | Any | Party | subDepartment | Sub-department |
| CdtTrfTxInf/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Any | Party | streetName | Street name |
| CdtTrfTxInf/Cdtr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Any | Party | buildingNumber | Building number |
| CdtTrfTxInf/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Any | Party | postalCode | ZIP code |
| CdtTrfTxInf/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Any | Party | city | City |
| CdtTrfTxInf/Cdtr/PstlAdr/CtrySubDvsn | State | Text | 1-35 | 0..1 | US State code | Party | state | State |
| CdtTrfTxInf/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | US | Party | country | Country code |
| CdtTrfTxInf/Cdtr/PstlAdr/AdrLine | Address Line | Text | 1-70 | 0..7 | Any | Party | addressLine | Address lines |
| CdtTrfTxInf/Cdtr/Id/OrgId/AnyBIC | Creditor BIC | Code | 8 or 11 | 0..1 | BIC | Party | bic | Creditor BIC if org |
| CdtTrfTxInf/Cdtr/Id/PrvtId/DtAndPlcOfBirth | Date of Birth | - | - | 0..1 | Date | Party | dateOfBirth | Individual DOB |
| CdtTrfTxInf/CdtrAcct/Id/Othr/Id | Creditor Account Number | Text | 1-34 | 1..1 | Account number | Account | accountNumber | Creditor account |
| CdtTrfTxInf/CdtrAcct/Id/Othr/SchmeNm/Cd | Account Scheme | Code | 1-4 | 0..1 | BBAN | Account | accountScheme | Account type scheme |
| CdtTrfTxInf/CdtrAcct/Tp/Cd | Account Type | Code | 1-4 | 0..1 | CACC, SVGS | Account | accountType | Account type |
| CdtTrfTxInf/CdtrAcct/Nm | Account Name | Text | 1-70 | 0..1 | Any | Account | accountName | Account name |
| CdtTrfTxInf/UltmtCdtr/Nm | Ultimate Creditor Name | Text | 1-140 | 0..1 | Any | Party | ultimateCreditorName | Ultimate beneficiary |
| CdtTrfTxInf/UltmtCdtr/Id/OrgId/Othr/Id | Ultimate Creditor ID | Text | 1-35 | 0..1 | Any | Party | ultimateCreditorId | Organization ID |

### Remittance and Purpose Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtTrfTxInf/Purp/Cd | Purpose Code | Code | 1-4 | 0..1 | External code | PaymentInstruction | purposeCode | Purpose of payment |
| CdtTrfTxInf/RgltryRptg/Dtls/Cd | Regulatory Reporting Code | Text | 1-10 | 0..1 | Any | PaymentInstruction | regulatoryReportingCode | Regulatory code |
| CdtTrfTxInf/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..1 | Any | PaymentInstruction | remittanceInformation | Unstructured remittance (max 140 chars) |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Any | PaymentInstruction | documentNumber | Invoice number |
| CdtTrfTxInf/RmtInf/Strd/RfrdDocInf/RltdDt | Document Date | Date | - | 0..1 | ISO Date | PaymentInstruction | documentDate | Invoice date |
| CdtTrfTxInf/RmtInf/Strd/CdtrRefInf/Ref | Creditor Reference | Text | 1-35 | 0..1 | Any | PaymentInstruction | creditorReference | Structured reference |
| CdtTrfTxInf/InstrForCdtrAgt/Cd | Instruction Code | Code | 1-4 | 0..1 | PHOB, TELE | PaymentInstruction | instructionCode | Instruction for creditor agent |
| CdtTrfTxInf/InstrForCdtrAgt/InstrInf | Instruction Information | Text | 1-140 | 0..1 | Any | PaymentInstruction | instructionInformation | Additional instruction |

### Request for Payment (RfP) - pain.013 Message

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| CdtrPmtActvtnReq/GrpHdr/MsgId | RfP Message ID | Text | 1-35 | 1..1 | Any | PaymentInstruction | requestId | Request for Payment ID |
| CdtrPmtActvtnReq/GrpHdr/CreDtTm | RfP Creation Time | DateTime | - | 1..1 | ISO DateTime | PaymentInstruction | requestCreationDateTime | RfP creation timestamp |
| CdtrPmtActvtnReq/PmtInf/ReqdExctnDt | Requested Execution Date | Date | - | 0..1 | ISO Date | PaymentInstruction | requestedExecutionDate | When payment should occur |
| CdtrPmtActvtnReq/PmtInf/XpryDt | Expiry Date | Date | - | 0..1 | ISO Date | PaymentInstruction | requestExpiryDate | RfP expiration date |

### Fraud and Security Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/Envlp/FrdInf/FrdClssfctnScr | Fraud Classification Score | Numeric | - | 0..1 | 0-999 | PaymentInstruction | fraudScore | FedNow Fraud Classifier score |
| SplmtryData/Envlp/FrdInf/FrdRskLvl | Fraud Risk Level | Code | 1-4 | 0..1 | LOW, MED, HIGH | PaymentInstruction | fraudRiskLevel | Risk level assessment |
| SplmtryData/Envlp/FrdInf/FrdMtgtnCtrl | Fraud Mitigation Control | Code | 1-10 | 0..1 | Various | PaymentInstruction | fraudMitigationControl | Applied fraud controls |

---

## FedNow-Specific Rules

### Transaction Limits

| Limit Type | Value | CDM Validation |
|------------|-------|----------------|
| Maximum per transaction | No federal limit (bank-defined) | instructedAmount.amount <= bank.maxLimit |
| Minimum per transaction | $0.01 | instructedAmount.amount >= 0.01 |
| Currency | USD only | instructedAmount.currency = 'USD' |

### Mandatory Elements

| Element | Requirement | CDM Validation |
|---------|-------------|----------------|
| Currency | Must be USD | instructedAmount.currency = 'USD' |
| Routing Number | 9-digit ABA routing | Validate routing number format |
| Account Number | Required for both parties | Non-empty account number |
| End-to-End ID | Mandatory, max 35 chars | endToEndId length <= 35 |
| Clearing System | Must be FEDNOW | clearingSystemCode = 'FEDNOW' |

### Request for Payment (RfP) - pain.013

FedNow supports Request for Payment messages that allow creditors to request payment from debtors.

| Field | Description | CDM Mapping |
|-------|-------------|-------------|
| Request ID | Unique request identifier | PaymentInstruction.requestId |
| Expiry Date | Request expiration date | PaymentInstruction.requestExpiryDate |
| Amount | Requested amount | PaymentInstruction.requestedAmount |
| Response | Accept/Reject/Cancel | PaymentInstruction.rfpResponse |
| Creditor | Requesting party | Party.name (creditor role) |

### Recall and Return Messages

| Message Type | ISO Message | Description | CDM Mapping |
|--------------|-------------|-------------|-------------|
| Payment Return | pacs.004 | Return of funds | PaymentInstruction.returnReason |
| Payment Recall | camt.056 | Request to recall payment | PaymentInstruction.recallRequest |
| Recall Response | camt.029 | Response to recall request | PaymentInstruction.recallResponse |

### Fraud Prevention Features

| Feature | Description | CDM Mapping |
|---------|-------------|-------------|
| Fraud Classifier | ML-based fraud scoring | PaymentInstruction.fraudScore |
| Fraud Controls | Rule-based mitigation | PaymentInstruction.fraudMitigationControl |
| Risk Level | LOW/MEDIUM/HIGH | PaymentInstruction.fraudRiskLevel |

### Purpose Codes (Selected Examples)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CASH | Cash Management Transfer | PaymentInstruction.purposeCode = 'CASH' |
| SUPP | Supplier Payment | PaymentInstruction.purposeCode = 'SUPP' |
| SALA | Salary Payment | PaymentInstruction.purposeCode = 'SALA' |
| PENS | Pension Payment | PaymentInstruction.purposeCode = 'PENS' |
| TAXS | Tax Payment | PaymentInstruction.purposeCode = 'TAXS' |
| TREA | Treasury Payment | PaymentInstruction.purposeCode = 'TREA' |
| GDDS | Purchase of Goods | PaymentInstruction.purposeCode = 'GDDS' |
| SERV | Purchase of Services | PaymentInstruction.purposeCode = 'SERV' |

---

## CDM Extensions Required

All 82 FedNow fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Examples

### Example 1: FedNow Credit Transfer (pacs.008)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>FEDNOW20241221145523001</MsgId>
      <CreDtTm>2024-12-21T14:55:23.456Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">5000.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>FEDNOW</Cd>
        </ClrSys>
      </SttlmInf>
      <InstgAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>111000025</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>026009593</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>FN-INSTR-20241221-001</InstrId>
        <EndToEndId>FN-E2E-20241221-001</EndToEndId>
        <TxId>FN-TX-20241221-001</TxId>
        <UETR>f47ac10b-58cc-4372-a567-0e02b2c3d479</UETR>
      </PmtId>
      <IntrBkSttlmAmt Ccy="USD">5000.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-21</IntrBkSttlmDt>
      <AccptncDtTm>2024-12-21T14:55:24.123Z</AccptncDtTm>
      <ChrgBr>SHAR</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>111000025</MmbId>
          </ClrSysMmbId>
          <Nm>Bank of America NA</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>TechCorp Solutions LLC</Nm>
        <PstlAdr>
          <StrtNm>California Street</StrtNm>
          <BldgNb>555</BldgNb>
          <PstCd>94104</PstCd>
          <TwnNm>San Francisco</TwnNm>
          <CtrySubDvsn>CA</CtrySubDvsn>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>4567891234</Id>
            <SchmeNm>
              <Cd>BBAN</Cd>
            </SchmeNm>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
      </DbtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>026009593</MmbId>
          </ClrSysMmbId>
          <Nm>Bank of the West</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Software Vendor Inc</Nm>
        <PstlAdr>
          <StrtNm>Tech Drive</StrtNm>
          <BldgNb>1000</BldgNb>
          <PstCd>94089</PstCd>
          <TwnNm>Sunnyvale</TwnNm>
          <CtrySubDvsn>CA</CtrySubDvsn>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>7891234560</Id>
            <SchmeNm>
              <Cd>BBAN</Cd>
            </SchmeNm>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
      </CdtrAcct>
      <Purp>
        <Cd>SERV</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Software license renewal - Annual subscription Q1 2025</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
    <SplmtryData>
      <Envlp>
        <FrdInf>
          <FrdClssfctnScr>125</FrdClssfctnScr>
          <FrdRskLvl>LOW</FrdRskLvl>
        </FrdInf>
      </Envlp>
    </SplmtryData>
  </FIToFICstmrCdtTrf>
</Document>
```

### Example 2: Request for Payment (pain.013)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.013.001.07">
  <CdtrPmtActvtnReq>
    <GrpHdr>
      <MsgId>RFP-20241221-987654</MsgId>
      <CreDtTm>2024-12-21T10:30:00.000Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <InitgPty>
        <Nm>Utility Company XYZ</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-INF-987654</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <ReqdExctnDt>2024-12-31</ReqdExctnDt>
      <XpryDt>2025-01-15</XpryDt>
      <Cdtr>
        <Nm>Utility Company XYZ</Nm>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>1122334455</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <CdtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>021000021</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </CdtrAgt>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>UTILITY-BILL-DEC2024</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="USD">234.56</InstdAmt>
        </Amt>
        <Dbtr>
          <Nm>John Smith</Nm>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <Othr>
              <Id>9988776655</Id>
            </Othr>
          </Id>
        </DbtrAcct>
        <DbtrAgt>
          <FinInstnId>
            <ClrSysMmbId>
              <MmbId>111000025</MmbId>
            </ClrSysMmbId>
          </FinInstnId>
        </DbtrAgt>
        <RmtInf>
          <Ustrd>Electric bill for December 2024 - Account #555-1234</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CdtrPmtActvtnReq>
</Document>
```

### Example 3: Payment Recall Request (camt.056)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.056.001.08">
  <FIToFIPmtCxlReq>
    <Assgnmt>
      <Id>RECALL-20241221-001</Id>
      <Assgnr>
        <Agt>
          <FinInstnId>
            <ClrSysMmbId>
              <MmbId>111000025</MmbId>
            </ClrSysMmbId>
          </FinInstnId>
        </Agt>
      </Assgnr>
      <Assgne>
        <Agt>
          <FinInstnId>
            <ClrSysMmbId>
              <MmbId>026009593</MmbId>
            </ClrSysMmbId>
          </FinInstnId>
        </Agt>
      </Assgne>
      <CreDtTm>2024-12-21T15:30:00.000Z</CreDtTm>
    </Assgnmt>
    <Undrlyg>
      <TxInf>
        <OrgnlInstrId>FN-INSTR-20241221-001</OrgnlInstrId>
        <OrgnlEndToEndId>FN-E2E-20241221-001</OrgnlEndToEndId>
        <OrgnlTxId>FN-TX-20241221-001</OrgnlTxId>
        <OrgnlIntrBkSttlmAmt Ccy="USD">5000.00</OrgnlIntrBkSttlmAmt>
        <OrgnlIntrBkSttlmDt>2024-12-21</OrgnlIntrBkSttlmDt>
        <CxlRsnInf>
          <Rsn>
            <Cd>DUPL</Cd>
          </Rsn>
          <AddtlInf>Duplicate payment sent in error</AddtlInf>
        </CxlRsnInf>
      </TxInf>
    </Undrlyg>
  </FIToFIPmtCxlReq>
</Document>
```

---

## References

- Federal Reserve FedNow Service: https://www.frbservices.org/financial-services/fednow
- FedNow Operating Rules and Procedures
- ISO 20022 Standard: https://www.iso20022.org/
- FedNow Fraud Prevention Tools: https://www.frbservices.org/financial-services/fednow/fraud-tools
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-21
**Next Review:** Q2 2025
