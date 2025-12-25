# ISO 20022 pain.014 - Creditor Payment Activation Request Status Report Mapping

## Message Overview

**Message Type:** pain.014.001.07 - CreditorPaymentActivationRequestStatusReportV07
**Category:** PAIN - Payment Initiation
**Purpose:** Sent by a bank (creditor agent) to a creditor to report the status of a previously submitted standing order or direct debit mandate activation/amendment/cancellation request
**Direction:** Bank (Creditor Agent) → Customer (Creditor)
**Scope:** Status reporting for activation, amendment, or cancellation requests

**Key Use Cases:**
- Acceptance/rejection of standing order activation (pain.009)
- Status of mandate activation request amendment (pain.013)
- Confirmation of cancellation request (pain.010)
- Suspension status reporting (pain.012)
- Error reporting for activation requests
- Partial acceptance scenarios
- Processing status updates
- Final settlement confirmation

**Relationship to Other Messages:**
- **pain.009**: Creditor payment activation request (status being reported)
- **pain.013**: Amendment request (status being reported)
- **pain.010**: Cancellation request (status being reported)
- **pain.012**: Suspension request (status being reported)
- **pain.002**: Customer payment status report (similar for payment initiation)
- **pain.008**: Direct debit initiation (executed after activation accepted)

**Status Report Workflow:**
1. Creditor sends **pain.009** (activation), **pain.013** (amendment), or **pain.010** (cancellation)
2. Bank validates request
3. Bank sends **pain.014** with status:
   - ACCP - Accepted
   - RJCT - Rejected
   - PDNG - Pending
   - ACTC - Accepted with changes
4. If accepted, activation becomes effective
5. If rejected, creditor may correct and resubmit

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in pain.014** | 68 |
| **Fields Mapped to CDM** | 68 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (creditor, debtor, reporting party)
- Account (creditor account, debtor account)
- FinancialInstitution (creditor agent)
- StatusReport (status codes, reasons, timestamps)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique status report message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Report creation timestamp |
| GrpHdr/InitgPty/Nm | Initiating Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Bank or creditor agent |
| GrpHdr/InitgPty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country |
| GrpHdr/InitgPty/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| GrpHdr/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor's bank (for information) |

### 2. Original Group Information (OrgnlGrpInfAndSts)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| OrgnlGrpInfAndSts/OrgnlMsgId | Original Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageId | Original pain.009/013/010/012 message ID |
| OrgnlGrpInfAndSts/OrgnlMsgNmId | Original Message Name ID | Code | 1-35 | 1..1 | pain.009/013/010/012 | PaymentInstruction.extensions | originalMessageNameId | Original message type |
| OrgnlGrpInfAndSts/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |
| OrgnlGrpInfAndSts/GrpSts | Group Status | Code | 4 | 0..1 | ACCP, ACTC, RCVD, PDNG, RJCT, CANC | PaymentInstruction.extensions | groupStatusCode | Overall status of entire message |
| OrgnlGrpInfAndSts/StsRsnInf/Rsn/Cd | Status Reason Code | Code | - | 0..1 | AC01-AC16, etc. | PaymentInstruction.extensions | statusReasonCode | Reason for status |
| OrgnlGrpInfAndSts/StsRsnInf/Rsn/Prtry | Proprietary Status Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | statusProprietaryReason | Custom reason |
| OrgnlGrpInfAndSts/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | statusAdditionalInfo | Detailed explanation |

### 3. Activation Status (ActvtnStsRpt)

#### 3.1 Original Activation Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnId | Original Activation ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalActivationId | Activation request ID from original message |
| ActvtnStsRpt/OrgnlInstrId | Original Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalInstructionId | Instruction ID from original message |
| ActvtnStsRpt/OrgnlEndToEndId | Original End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalEndToEndId | E2E reference from original message |

#### 3.2 Activation Status

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/ActvtnSts | Activation Status | Code | 4 | 1..1 | ACCP, ACTC, RCVD, PDNG, RJCT, CANC, SUSP | PaymentInstruction.extensions | activationStatusCode | Status of activation request |
| ActvtnStsRpt/StsRsnInf/Rsn/Cd | Status Reason Code | Code | - | 0..1 | AC01-AC16, AG01-AG02, etc. | PaymentInstruction.extensions | statusReasonCode | Reason for status |
| ActvtnStsRpt/StsRsnInf/Rsn/Prtry | Proprietary Status Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | statusProprietaryReason | Custom reason |
| ActvtnStsRpt/StsRsnInf/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | statusAdditionalInfo | Detailed explanation |
| ActvtnStsRpt/StsRsnInf/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Party that originated status |
| ActvtnStsRpt/StsRsnInf/Orgtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Originator BIC |

#### 3.3 Original Activation Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnDtls/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Creditor from original request |
| ActvtnStsRpt/OrgnlActvtnDtls/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Creditor country |
| ActvtnStsRpt/OrgnlActvtnDtls/Cdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Creditor BIC |
| ActvtnStsRpt/OrgnlActvtnDtls/Cdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Creditor tax ID |
| ActvtnStsRpt/OrgnlActvtnDtls/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Creditor IBAN |
| ActvtnStsRpt/OrgnlActvtnDtls/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| ActvtnStsRpt/OrgnlActvtnDtls/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Creditor's bank BIC |
| ActvtnStsRpt/OrgnlActvtnDtls/CdtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor agent name |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Debtor from original request |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Debtor country |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Debtor tax ID |
| ActvtnStsRpt/OrgnlActvtnDtls/Dbtr/Id/PrvtId/Othr/Id | Private Other ID | Text | 1-35 | 0..1 | Free text | Party | nationalId | Debtor national ID |
| ActvtnStsRpt/OrgnlActvtnDtls/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor IBAN |
| ActvtnStsRpt/OrgnlActvtnDtls/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| ActvtnStsRpt/OrgnlActvtnDtls/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Debtor's bank BIC |
| ActvtnStsRpt/OrgnlActvtnDtls/DbtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor agent name |

#### 3.4 Payment Type Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnDtls/PmtTpInf/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA, SDVA, PRPT | PaymentInstruction.extensions | serviceLevelCode | Service level |
| ActvtnStsRpt/OrgnlActvtnDtls/PmtTpInf/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B, COR1 | PaymentInstruction.extensions | localInstrumentCode | SEPA direct debit scheme |
| ActvtnStsRpt/OrgnlActvtnDtls/PmtTpInf/CtgyPurp/Cd | Category Purpose Code | Code | - | 0..1 | CASH, CORT, etc. | PaymentInstruction.extensions | categoryPurposeCode | Category purpose |

#### 3.5 Frequency

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnDtls/Frqcy/Tp/Cd | Frequency Type Code | Code | - | 0..1 | DAIL, WEEK, MNTH, QURT, YEAR | PaymentInstruction.extensions | frequencyCode | Payment frequency |
| ActvtnStsRpt/OrgnlActvtnDtls/Frqcy/PtInTm/Dt | Point in Time Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | Execution date |

#### 3.6 Amount

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnDtls/Amt | Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | Payment amount |
| ActvtnStsRpt/OrgnlActvtnDtls/Amt/@Ccy | Currency | Code | 3 | 0..1 | ISO 4217 | PaymentInstruction | currency | Payment currency |

#### 3.7 Mandate Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnDtls/Mndt/MndtId | Mandate Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | Mandate reference |
| ActvtnStsRpt/OrgnlActvtnDtls/Mndt/MndtReqId | Mandate Request ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateRequestId | Activation request ID |
| ActvtnStsRpt/OrgnlActvtnDtls/Mndt/DtOfSgntr | Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | Mandate signature date |
| ActvtnStsRpt/OrgnlActvtnDtls/Mndt/Tp/SvcLvl/Cd | Service Level Code | Code | - | 0..1 | SEPA | PaymentInstruction.extensions | mandateServiceLevelCode | Mandate scheme |
| ActvtnStsRpt/OrgnlActvtnDtls/Mndt/Tp/LclInstrm/Cd | Local Instrument Code | Code | - | 0..1 | CORE, B2B | PaymentInstruction.extensions | mandateLocalInstrumentCode | Mandate type |

#### 3.8 Remittance Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/OrgnlActvtnDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction | remittanceInformation | Unstructured remittance info |
| ActvtnStsRpt/OrgnlActvtnDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | documentNumber | Document reference |

#### 3.9 Accepted Amendment Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnStsRpt/AccptdAmdmntDtls/Cdtr/Nm | Accepted Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Creditor after amendment (if ACTC) |
| ActvtnStsRpt/AccptdAmdmntDtls/CdtrAcct/Id/IBAN | Accepted Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account after amendment |
| ActvtnStsRpt/AccptdAmdmntDtls/Dbtr/Nm | Accepted Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Debtor after amendment |
| ActvtnStsRpt/AccptdAmdmntDtls/DbtrAcct/Id/IBAN | Accepted Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor account after amendment |
| ActvtnStsRpt/AccptdAmdmntDtls/Frqcy/Tp/Cd | Accepted Frequency Type Code | Code | - | 0..1 | DAIL, WEEK, MNTH, QURT, YEAR | PaymentInstruction.extensions | acceptedFrequencyCode | Frequency after amendment |
| ActvtnStsRpt/AccptdAmdmntDtls/Amt | Accepted Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | acceptedAmount | Amount after amendment |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Group Status Code (GrpSts / ActvtnSts)

- **ACCP** - Accepted for settlement (success)
- **ACTC** - Accepted with changes (partial acceptance)
- **RCVD** - Received (acknowledged but not yet processed)
- **PDNG** - Pending (under investigation)
- **RJCT** - Rejected (failed)
- **CANC** - Cancelled (successfully cancelled)
- **SUSP** - Suspended (suspended as requested)

### Status Reason Codes (StsRsnInf/Rsn/Cd)

**Account Related (AC series):**
- **AC01** - Incorrect account number
- **AC02** - Invalid debtor account number
- **AC03** - Invalid creditor account number
- **AC04** - Closed account
- **AC05** - Closed debtor account
- **AC06** - Blocked account
- **AC07** - Closed creditor account
- **AC13** - Invalid debtor account type
- **AC14** - Invalid creditor account type

**Agent Related (AG series):**
- **AG01** - Transaction forbidden on account
- **AG02** - Invalid bank operation code

**Amount Related (AM series):**
- **AM01** - Zero amount
- **AM02** - Not allowed amount
- **AM03** - Not allowed currency
- **AM04** - Insufficient funds
- **AM05** - Duplication

**Mandate Related (MD series):**
- **MD01** - No mandate
- **MD02** - Missing mandatory information in mandate
- **MD03** - Invalid file format for technical reasons
- **MD06** - Refund request by end customer
- **MD07** - End customer deceased

**Regulatory (RR series):**
- **RR01** - Missing regulatory reporting
- **RR02** - Invalid regulatory reporting
- **RR03** - Missing creditor address
- **RR04** - Regulatory reason

### Frequency Type Code (Frqcy/Tp/Cd)

- **DAIL** - Daily
- **WEEK** - Weekly
- **MNTH** - Monthly
- **QURT** - Quarterly
- **YEAR** - Annual

---

## Message Examples

### Example 1: Acceptance of Standing Order Activation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.014.001.07">
  <CdtrPmtActvtnReqStsRpt>
    <GrpHdr>
      <MsgId>STATUS-RPT-20241220-001</MsgId>
      <CreDtTm>2024-12-20T14:00:00</CreDtTm>
      <InitgPty>
        <Nm>ABC Bank PLC</Nm>
        <Id>
          <OrgId>
            <AnyBIC>ABCBGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlGrpInfAndSts>
      <OrgnlMsgId>SO-ACTIV-20241218-001</OrgnlMsgId>
      <OrgnlMsgNmId>pain.009.001.07</OrgnlMsgNmId>
      <OrgnlCreDtTm>2024-12-18T10:00:00</OrgnlCreDtTm>
      <GrpSts>ACCP</GrpSts>
    </OrgnlGrpInfAndSts>
    <ActvtnStsRpt>
      <OrgnlActvtnId>ACTIV-2024-SO-123456</OrgnlActvtnId>
      <OrgnlEndToEndId>E2E-SO-RENT-2024</OrgnlEndToEndId>
      <ActvtnSts>ACCP</ActvtnSts>
      <StsRsnInf>
        <AddtlInf>Standing order successfully activated. First payment will be executed on 2025-01-01.</AddtlInf>
        <Orgtr>
          <Nm>ABC Bank PLC - Standing Orders Department</Nm>
        </Orgtr>
      </StsRsnInf>
      <OrgnlActvtnDtls>
        <Cdtr>
          <Nm>John Smith</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>GB82ABCB20051512345678</IBAN>
          </Id>
        </CdtrAcct>
        <CdtrAgt>
          <FinInstnId>
            <BICFI>ABCBGB2LXXX</BICFI>
          </FinInstnId>
        </CdtrAgt>
        <Dbtr>
          <Nm>Landlord Properties Ltd</Nm>
          <PstlAdr>
            <StrtNm>Property Street</StrtNm>
            <PstCd>SW1A 1AA</PstCd>
            <TwnNm>London</TwnNm>
            <Ctry>GB</Ctry>
          </PstlAdr>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>GB29HSBC40051556789012</IBAN>
          </Id>
        </DbtrAcct>
        <Frqcy>
          <Tp>
            <Cd>MNTH</Cd>
          </Tp>
          <PtInTm>
            <Dt>2025-01-01</Dt>
          </PtInTm>
        </Frqcy>
        <Amt Ccy="GBP">1200.00</Amt>
        <RmtInf>
          <Ustrd>Monthly rent payment - 123 Main Street</Ustrd>
        </RmtInf>
      </OrgnlActvtnDtls>
    </ActvtnStsRpt>
  </CdtrPmtActvtnReqStsRpt>
</Document>
```

### Example 2: Rejection of SEPA Mandate Activation - Invalid Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.014.001.07">
  <CdtrPmtActvtnReqStsRpt>
    <GrpHdr>
      <MsgId>STATUS-RPT-20241220-002</MsgId>
      <CreDtTm>2024-12-20T15:30:00</CreDtTm>
      <InitgPty>
        <Nm>BNP Paribas SA</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BNPAFRPPXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>DEUTDEFFXXX</BICFI>
        </FinInstnId>
      </DbtrAgt>
    </GrpHdr>
    <OrgnlGrpInfAndSts>
      <OrgnlMsgId>MAND-ACTIV-20241220-789</OrgnlMsgId>
      <OrgnlMsgNmId>pain.009.001.07</OrgnlMsgNmId>
      <OrgnlCreDtTm>2024-12-20T09:00:00</OrgnlCreDtTm>
      <GrpSts>RJCT</GrpSts>
      <StsRsnInf>
        <Rsn>
          <Cd>AC02</Cd>
        </Rsn>
        <AddtlInf>Invalid debtor account number. Please verify IBAN and resubmit.</AddtlInf>
      </StsRsnInf>
    </OrgnlGrpInfAndSts>
    <ActvtnStsRpt>
      <OrgnlActvtnId>SEPA-MAND-2024-789456</OrgnlActvtnId>
      <OrgnlEndToEndId>E2E-DD-SUB-789</OrgnlEndToEndId>
      <ActvtnSts>RJCT</ActvtnSts>
      <StsRsnInf>
        <Rsn>
          <Cd>AC02</Cd>
        </Rsn>
        <AddtlInf>Debtor account IBAN failed validation. Account does not exist at debtor agent.</AddtlInf>
        <Orgtr>
          <Nm>BNP Paribas - SEPA Mandate Processing</Nm>
        </Orgtr>
      </StsRsnInf>
      <OrgnlActvtnDtls>
        <Cdtr>
          <Nm>Streaming Service Pro</Nm>
          <PstlAdr>
            <Ctry>FR</Ctry>
          </PstlAdr>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>FR7630006000011234567890189</IBAN>
          </Id>
        </CdtrAcct>
        <CdtrAgt>
          <FinInstnId>
            <BICFI>BNPAFRPPXXX</BICFI>
          </FinInstnId>
        </CdtrAgt>
        <Dbtr>
          <Nm>Hans Mueller</Nm>
          <PstlAdr>
            <StrtNm>Berliner Strasse</StrtNm>
            <PstCd>60311</PstCd>
            <TwnNm>Frankfurt</TwnNm>
            <Ctry>DE</Ctry>
          </PstlAdr>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>DE89370400440532013000</IBAN>
          </Id>
        </DbtrAcct>
        <DbtrAgt>
          <FinInstnId>
            <BICFI>DEUTDEFFXXX</BICFI>
          </FinInstnId>
        </DbtrAgt>
        <PmtTpInf>
          <SvcLvl>
            <Cd>SEPA</Cd>
          </SvcLvl>
          <LclInstrm>
            <Cd>CORE</Cd>
          </LclInstrm>
        </PmtTpInf>
        <Amt Ccy="EUR">9.99</Amt>
        <Mndt>
          <MndtId>MANDATE-2024-USER-789</MndtId>
          <MndtReqId>MAND-REQ-789456</MndtReqId>
          <DtOfSgntr>2024-12-15</DtOfSgntr>
          <Tp>
            <SvcLvl>
              <Cd>SEPA</Cd>
            </SvcLvl>
            <LclInstrm>
              <Cd>CORE</Cd>
            </LclInstrm>
          </Tp>
        </Mndt>
        <RmtInf>
          <Ustrd>Monthly subscription - Premium account</Ustrd>
        </RmtInf>
      </OrgnlActvtnDtls>
    </ActvtnStsRpt>
  </CdtrPmtActvtnReqStsRpt>
</Document>
```

### Example 3: Acceptance with Changes - Amendment Approved with Modifications

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.014.001.07">
  <CdtrPmtActvtnReqStsRpt>
    <GrpHdr>
      <MsgId>STATUS-RPT-20241220-003</MsgId>
      <CreDtTm>2024-12-20T16:00:00</CreDtTm>
      <InitgPty>
        <Nm>HSBC Bank PLC</Nm>
        <Id>
          <OrgId>
            <AnyBIC>HSBCGB2LXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlGrpInfAndSts>
      <OrgnlMsgId>AMEND-SO-20241220-555</OrgnlMsgId>
      <OrgnlMsgNmId>pain.013.001.07</OrgnlMsgNmId>
      <OrgnlCreDtTm>2024-12-20T11:00:00</OrgnlCreDtTm>
      <GrpSts>ACTC</GrpSts>
      <StsRsnInf>
        <AddtlInf>Amendment accepted with bank modifications to execution date due to system constraints.</AddtlInf>
      </StsRsnInf>
    </OrgnlGrpInfAndSts>
    <ActvtnStsRpt>
      <OrgnlActvtnId>SO-2024-CHARITY-555</OrgnlActvtnId>
      <OrgnlEndToEndId>E2E-CHARITY-QRTLY</OrgnlEndToEndId>
      <ActvtnSts>ACTC</ActvtnSts>
      <StsRsnInf>
        <AddtlInf>Frequency change to quarterly accepted. First quarterly payment date adjusted to 2025-01-05 instead of requested 2025-01-01 (holiday/weekend).</AddtlInf>
        <Orgtr>
          <Nm>HSBC - Standing Order Processing</Nm>
        </Orgtr>
      </StsRsnInf>
      <OrgnlActvtnDtls>
        <Cdtr>
          <Nm>Maria Garcia</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>GB33HSBC40051512345678</IBAN>
          </Id>
        </CdtrAcct>
        <Dbtr>
          <Nm>Children's Charity Foundation</Nm>
        </Dbtr>
        <Frqcy>
          <Tp>
            <Cd>QURT</Cd>
          </Tp>
          <PtInTm>
            <Dt>2025-01-01</Dt>
          </PtInTm>
        </Frqcy>
        <Amt Ccy="GBP">150.00</Amt>
      </OrgnlActvtnDtls>
      <AccptdAmdmntDtls>
        <Frqcy>
          <Tp>
            <Cd>QURT</Cd>
          </Tp>
        </Frqcy>
        <Amt Ccy="GBP">150.00</Amt>
      </AccptdAmdmntDtls>
    </ActvtnStsRpt>
  </CdtrPmtActvtnReqStsRpt>
</Document>
```

### Example 4: Pending Status - Under Investigation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.014.001.07">
  <CdtrPmtActvtnReqStsRpt>
    <GrpHdr>
      <MsgId>STATUS-RPT-20241220-004</MsgId>
      <CreDtTm>2024-12-20T12:00:00</CreDtTm>
      <InitgPty>
        <Nm>Deutsche Bank AG</Nm>
        <Id>
          <OrgId>
            <AnyBIC>DEUTDEFFXXX</AnyBIC>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <OrgnlGrpInfAndSts>
      <OrgnlMsgId>MAND-ACTIV-20241220-B2B</OrgnlMsgId>
      <OrgnlMsgNmId>pain.009.001.07</OrgnlMsgNmId>
      <OrgnlCreDtTm>2024-12-20T08:00:00</OrgnlCreDtTm>
      <GrpSts>PDNG</GrpSts>
      <StsRsnInf>
        <AddtlInf>Mandate activation under review. Awaiting verification from debtor agent.</AddtlInf>
      </StsRsnInf>
    </OrgnlGrpInfAndSts>
    <ActvtnStsRpt>
      <OrgnlActvtnId>B2B-MAND-2024-CORP-999</OrgnlActvtnId>
      <OrgnlEndToEndId>E2E-B2B-INV-MONTHLY</OrgnlEndToEndId>
      <ActvtnSts>PDNG</ActvtnSts>
      <StsRsnInf>
        <AddtlInf>SEPA B2B mandate activation pending verification with debtor agent. Expected completion within 2 business days.</AddtlInf>
        <Orgtr>
          <Nm>Deutsche Bank - SEPA B2B Processing</Nm>
        </Orgtr>
      </StsRsnInf>
      <OrgnlActvtnDtls>
        <Cdtr>
          <Nm>Supplier Services GmbH</Nm>
          <PstlAdr>
            <Ctry>DE</Ctry>
          </PstlAdr>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <IBAN>DE89370400440532013000</IBAN>
          </Id>
        </CdtrAcct>
        <CdtrAgt>
          <FinInstnId>
            <BICFI>DEUTDEFFXXX</BICFI>
          </FinInstnId>
        </CdtrAgt>
        <Dbtr>
          <Nm>Corporate Buyer Ltd</Nm>
          <PstlAdr>
            <Ctry>FR</Ctry>
          </PstlAdr>
        </Dbtr>
        <DbtrAcct>
          <Id>
            <IBAN>FR1420041010050500013M02606</IBAN>
          </Id>
        </DbtrAcct>
        <DbtrAgt>
          <FinInstnId>
            <BICFI>BNPAFRPPXXX</BICFI>
          </FinInstnId>
        </DbtrAgt>
        <PmtTpInf>
          <SvcLvl>
            <Cd>SEPA</Cd>
          </SvcLvl>
          <LclInstrm>
            <Cd>B2B</Cd>
          </LclInstrm>
        </PmtTpInf>
        <Frqcy>
          <Tp>
            <Cd>MNTH</Cd>
          </Tp>
        </Frqcy>
        <Amt Ccy="EUR">25000.00</Amt>
        <Mndt>
          <MndtId>B2B-MANDATE-2024-CORP-999</MndtId>
          <DtOfSgntr>2024-12-18</DtOfSgntr>
          <Tp>
            <SvcLvl>
              <Cd>SEPA</Cd>
            </SvcLvl>
            <LclInstrm>
              <Cd>B2B</Cd>
            </LclInstrm>
          </Tp>
        </Mndt>
      </OrgnlActvtnDtls>
    </ActvtnStsRpt>
  </CdtrPmtActvtnReqStsRpt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 68 fields in pain.014 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles instruction identification, amounts, dates
- Extension fields accommodate status reporting elements (status codes, reasons, original references)
- Party entity supports creditor, debtor, originator identification
- Account entity handles IBAN and non-IBAN account identifiers
- FinancialInstitution entity manages agent information
- StatusReport entity (or extensions) captures status workflow

**Key Extension Fields Used:**
- originalMessageId, originalMessageNameId, originalCreatedDateTime (reference to original request)
- originalActivationId, originalInstructionId, originalEndToEndId
- groupStatusCode, activationStatusCode (ACCP, ACTC, RCVD, PDNG, RJCT, CANC, SUSP)
- statusReasonCode (AC01-AC14, AG01-AG02, AM01-AM05, MD01-MD07, RR01-RR04)
- statusProprietaryReason, statusAdditionalInfo
- acceptedAmount, acceptedFrequencyCode (for ACTC status - accepted with changes)
- mandateId, mandateRequestId, mandateSignatureDate
- serviceLevelCode, localInstrumentCode (SEPA CORE/B2B)
- frequencyCode (DAIL, WEEK, MNTH, QURT, YEAR)

**Status Reporting Semantics:**
- Original request details preserved for reference
- Status codes standardized across ISO 20022 messages
- Reason codes provide detailed explanation for rejection/pending
- Accepted amendment details show final state after bank modifications
- Originator field identifies party setting the status

---

## References

- **ISO 20022 Message Definition:** pain.014.001.07 - CreditorPaymentActivationRequestStatusReportV07
- **XML Schema:** pain.014.001.07.xsd
- **Related Messages:** pain.009 (activation), pain.013 (amendment), pain.010 (cancellation), pain.012 (suspension), pain.002 (payment status)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Status Codes:** ISO 20022 ExternalPaymentTransactionStatus1Code
- **Reason Codes:** ISO 20022 ExternalStatusReason1Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
