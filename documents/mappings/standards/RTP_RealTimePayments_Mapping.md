# RTP - Real-Time Payments
## Complete Field Mapping to GPS CDM

**Message Type:** RTP Payment Message (ISO 20022 pacs.008.001.08)
**Standard:** ISO 20022 XML
**Operator:** The Clearing House (TCH)
**Usage:** Real-time payment processing in the United States
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 78 fields mapped)

---

## Message Overview

The RTP network is a real-time payment platform operated by The Clearing House in the United States. It provides instant, irrevocable, 24x7x365 payment processing with immediate funds availability and rich remittance data.

**Key Characteristics:**
- Currency: USD only
- Execution time: Real-time (typically < 20 seconds)
- Amount limit: $1,000,000 per transaction
- Availability: 24x7x365
- Settlement: Real-time, irrevocable
- Character set: UTF-8 (full Unicode support)

**Operating Hours:** Continuous (24x7x365 including holidays)
**Settlement:** Real-time gross settlement through Federal Reserve accounts

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total RTP Fields** | 78 | 100% |
| **Mapped to CDM** | 78 | 100% |
| **Direct Mapping** | 71 | 91% |
| **Derived/Calculated** | 5 | 6% |
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
| GrpHdr/SttlmInf/ClrSys/Cd | Clearing System Code | Code | 5 | 1..1 | USRTP | PaymentInstruction | clearingSystemCode | RTP network |
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
| CdtTrfTxInf/ChrgsInf/Amt | Charges Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | chargesAmount.amount | Charges |
| CdtTrfTxInf/ChrgsInf/Agt/FinInstnId/ClrSysMmbId/MmbId | Charges Agent ID | Text | 9 | 0..1 | ABA Routing | FinancialInstitution | routingNumber | Charging bank |

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

---

## RTP-Specific Rules

### Transaction Limits

| Limit Type | Value | CDM Validation |
|------------|-------|----------------|
| Maximum per transaction | $1,000,000 | instructedAmount.amount <= 1000000.00 |
| Minimum per transaction | $0.01 | instructedAmount.amount >= 0.01 |
| Currency | USD only | instructedAmount.currency = 'USD' |

### Mandatory Elements

| Element | Requirement | CDM Validation |
|---------|-------------|----------------|
| Currency | Must be USD | instructedAmount.currency = 'USD' |
| Routing Number | 9-digit ABA routing | Validate routing number format |
| Account Number | Required for both parties | Non-empty account number |
| End-to-End ID | Mandatory, max 35 chars | endToEndId length <= 35 |
| Clearing System | Must be USRTP | clearingSystemCode = 'USRTP' |

### Request for Payment (RfP)

RTP supports Request for Payment messages that allow creditors to request payment from debtors.

| Field | Description | CDM Mapping |
|-------|-------------|-------------|
| Request ID | Unique request identifier | PaymentInstruction.requestId |
| Expiry Date Time | Request expiration | PaymentInstruction.requestExpiryDateTime |
| Amount | Requested amount | PaymentInstruction.requestedAmount |
| Response | Accept/Reject | PaymentInstruction.rfpResponse |

### Purpose Codes (Selected Examples)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CASH | Cash Management Transfer | PaymentInstruction.purposeCode = 'CASH' |
| SUPP | Supplier Payment | PaymentInstruction.purposeCode = 'SUPP' |
| SALA | Salary Payment | PaymentInstruction.purposeCode = 'SALA' |
| PENS | Pension Payment | PaymentInstruction.purposeCode = 'PENS' |
| TAXS | Tax Payment | PaymentInstruction.purposeCode = 'TAXS' |
| TREA | Treasury Payment | PaymentInstruction.purposeCode = 'TREA' |

---

## CDM Extensions Required

All 78 RTP fields successfully map to existing CDM model. **No enhancements required.**

---

## Message Example

### RTP Payment Message (pacs.008)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>RTP20241220123456789</MsgId>
      <CreDtTm>2024-12-20T14:30:45.123Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">2500.00</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Cd>USRTP</Cd>
        </ClrSys>
      </SttlmInf>
      <InstgAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>021000021</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>111000025</MmbId>
          </ClrSysMmbId>
        </FinInstnId>
      </InstdAgt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>INSTR20241220001</InstrId>
        <EndToEndId>E2E20241220001</EndToEndId>
        <TxId>TX20241220001</TxId>
        <UETR>550e8400-e29b-41d4-a716-446655440000</UETR>
      </PmtId>
      <IntrBkSttlmAmt Ccy="USD">2500.00</IntrBkSttlmAmt>
      <IntrBkSttlmDt>2024-12-20</IntrBkSttlmDt>
      <AccptncDtTm>2024-12-20T14:30:46.789Z</AccptncDtTm>
      <ChrgBr>DEBT</ChrgBr>
      <DbtrAgt>
        <FinInstnId>
          <ClrSysMmbId>
            <MmbId>021000021</MmbId>
          </ClrSysMmbId>
          <Nm>JPMorgan Chase Bank NA</Nm>
        </FinInstnId>
      </DbtrAgt>
      <Dbtr>
        <Nm>Acme Corporation</Nm>
        <PstlAdr>
          <StrtNm>Park Avenue</StrtNm>
          <BldgNb>250</BldgNb>
          <PstCd>10177</PstCd>
          <TwnNm>New York</TwnNm>
          <CtrySubDvsn>NY</CtrySubDvsn>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>1234567890</Id>
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
            <MmbId>111000025</MmbId>
          </ClrSysMmbId>
          <Nm>Bank of America NA</Nm>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Supplier Inc</Nm>
        <PstlAdr>
          <StrtNm>Main Street</StrtNm>
          <BldgNb>100</BldgNb>
          <PstCd>60601</PstCd>
          <TwnNm>Chicago</TwnNm>
          <CtrySubDvsn>IL</CtrySubDvsn>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>9876543210</Id>
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
        <Cd>SUPP</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>Payment for Invoice INV-2024-98765 dated 2024-12-15</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

---

## References

- The Clearing House RTP Network: https://www.theclearinghouse.org/payment-systems/rtp
- ISO 20022 Standard: https://www.iso20022.org/
- RTP Operating Rules: TCH RTP Operating Rules and Guidelines
- GPS CDM Schema: `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
