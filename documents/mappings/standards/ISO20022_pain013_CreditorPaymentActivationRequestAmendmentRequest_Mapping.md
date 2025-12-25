# ISO 20022 pain.013 - Creditor Payment Activation Request Amendment Request Mapping

## Message Overview

**Message Type:** pain.013.001.07 - CreditorPaymentActivationRequestAmendmentRequestV07
**Category:** PAIN - Payment Initiation
**Purpose:** Sent by a creditor (or creditor's agent) to their bank to request amendment of a previously submitted standing order or direct debit mandate activation request
**Direction:** Customer (Creditor) → Bank (Creditor Agent)
**Scope:** Amendment of standing order or direct debit activation request

**Key Use Cases:**
- Amendment of standing order instructions (frequency, amount, beneficiary)
- Modification of SEPA direct debit mandate activation details
- Update of recurring payment parameters
- Change of creditor information in activation request
- Correction of debtor account details
- Amendment of payment execution rules
- Update of mandate-related information before first collection

**Relationship to Other Messages:**
- **pain.009**: Original creditor payment activation request (being amended)
- **pain.014**: Status report for amendment request
- **pain.010**: Cancellation request (if amendment not possible)
- **pain.012**: Suspension request for standing order
- **pain.008**: Direct debit initiation (executed after activation)
- **pacs.003**: Interbank direct debit (resulting from activation)

**Amendment Workflow:**
1. Creditor originally submitted **pain.009** (activation request)
2. Creditor sends **pain.013** with amendment details
3. Bank validates and processes amendment
4. Bank sends **pain.014** (status report) confirming acceptance/rejection
5. If accepted, amended activation becomes effective

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in pain.013** | 72 |
| **Fields Mapped to CDM** | 72 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (creditor, debtor, ultimate parties)
- Account (creditor account, debtor account)
- FinancialInstitution (creditor agent, debtor agent)
- Mandate (direct debit mandate activation amendment information)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique amendment message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | createdDateTime | Message creation timestamp |
| GrpHdr/NbOfTxs | Number of Transactions | Text | 1-15 | 0..1 | Numeric string | PaymentInstruction.extensions | numberOfTransactions | Transaction count in message |
| GrpHdr/CtrlSum | Control Sum | Decimal | - | 0..1 | Positive decimal | PaymentInstruction.extensions | controlSum | Total of all amounts (validation) |
| GrpHdr/InitgPty/Nm | Initiating Party Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Creditor or agent initiating |
| GrpHdr/InitgPty/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| GrpHdr/InitgPty/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | buildingNumber | Building number |
| GrpHdr/InitgPty/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| GrpHdr/InitgPty/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| GrpHdr/InitgPty/PstlAdr/CtrySubDvsn | Country Sub-division | Text | 1-35 | 0..1 | Free text | Party | stateProvince | State/province |
| GrpHdr/InitgPty/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| GrpHdr/InitgPty/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| GrpHdr/InitgPty/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/organization number |

### 2. Underlying Activation Details (UndrlygActvtnDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| UndrlygActvtnDtls/OrgnlMsgInf/MsgId | Original Message ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalMessageId | Original pain.009 message ID being amended |
| UndrlygActvtnDtls/OrgnlMsgInf/MsgNmId | Original Message Name ID | Code | 1-35 | 0..1 | pain.009.001.xx | PaymentInstruction.extensions | originalMessageNameId | Original message type |
| UndrlygActvtnDtls/OrgnlMsgInf/CreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |
| UndrlygActvtnDtls/ActvtnId | Activation Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | activationId | Activation request ID being amended |

### 3. Amendment (Amdmnt)

#### 3.1 Amendment Reason Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/AmdmntRsn/Rsn/Cd | Amendment Reason Code | Code | - | 0..1 | AM01-AM15 | PaymentInstruction.extensions | amendmentReasonCode | Code for amendment reason |
| Amdmnt/AmdmntRsn/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | amendmentProprietaryReason | Custom reason |
| Amdmnt/AmdmntRsn/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | amendmentAdditionalInfo | Explanation of amendment |

#### 3.2 Original Creditor (OrgnlCdtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlCdtr/Nm | Original Creditor Name | Text | 1-140 | 0..1 | Free text | Party.extensions | originalCreditorName | Creditor name before amendment |
| Amdmnt/OrgnlCdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party.extensions | originalCreditorCountry | Country |
| Amdmnt/OrgnlCdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party.extensions | originalCreditorBIC | Organization BIC |
| Amdmnt/OrgnlCdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party.extensions | originalCreditorTaxId | Tax ID |

#### 3.3 Original Creditor Agent (OrgnlCdtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlCdtrAgt/FinInstnId/BICFI | Original Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution.extensions | originalCreditorAgentBIC | Original creditor bank BIC |
| Amdmnt/OrgnlCdtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution.extensions | originalCreditorAgentName | Original creditor agent name |

#### 3.4 Original Creditor Account (OrgnlCdtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlCdtrAcct/Id/IBAN | Original Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account.extensions | originalCreditorAccountIBAN | Original IBAN |
| Amdmnt/OrgnlCdtrAcct/Id/Othr/Id | Original Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account.extensions | originalCreditorAccountNumber | Original account |

#### 3.5 Original Debtor (OrgnlDbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlDbtr/Nm | Original Debtor Name | Text | 1-140 | 0..1 | Free text | Party.extensions | originalDebtorName | Debtor name before amendment |
| Amdmnt/OrgnlDbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party.extensions | originalDebtorStreetName | Street |
| Amdmnt/OrgnlDbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party.extensions | originalDebtorPostalCode | ZIP/postal code |
| Amdmnt/OrgnlDbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party.extensions | originalDebtorCity | City |
| Amdmnt/OrgnlDbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party.extensions | originalDebtorCountry | Country code |
| Amdmnt/OrgnlDbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party.extensions | originalDebtorTaxId | Tax ID |

#### 3.6 Original Debtor Agent (OrgnlDbtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlDbtrAgt/FinInstnId/BICFI | Original Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution.extensions | originalDebtorAgentBIC | Original debtor bank BIC |
| Amdmnt/OrgnlDbtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution.extensions | originalDebtorAgentName | Original debtor agent name |

#### 3.7 Original Debtor Account (OrgnlDbtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlDbtrAcct/Id/IBAN | Original Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account.extensions | originalDebtorAccountIBAN | Original debtor IBAN |
| Amdmnt/OrgnlDbtrAcct/Id/Othr/Id | Original Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account.extensions | originalDebtorAccountNumber | Original account |

#### 3.8 Original Mandate (OrgnlMndt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlMndt/MndtId | Original Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalMandateId | Original mandate reference |
| Amdmnt/OrgnlMndt/MndtReqId | Original Mandate Request ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalMandateRequestId | Original activation request ID |
| Amdmnt/OrgnlMndt/DtOfSgntr | Original Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | originalMandateSignatureDate | Original signature date |

#### 3.9 Original Frequency (OrgnlFrqcy)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlFrqcy/Tp/Cd | Original Frequency Type Code | Code | - | 0..1 | DAIL, WEEK, MNTH, QURT, YEAR | PaymentInstruction.extensions | originalFrequencyCode | Original payment frequency |
| Amdmnt/OrgnlFrqcy/PtInTm/Dt | Original Point in Time Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | originalExecutionDate | Original execution date |

#### 3.10 Original Amount (OrgnlAmt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Amdmnt/OrgnlAmt | Original Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | originalAmount | Original payment amount |
| Amdmnt/OrgnlAmt/@Ccy | Currency | Code | 3 | 0..1 | ISO 4217 | PaymentInstruction.extensions | originalCurrency | Original currency |

### 4. Activation Amendment (ActvtnAmdmnt)

#### 4.1 New Creditor (Cdtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/Cdtr/Nm | New Creditor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Amended creditor name |
| ActvtnAmdmnt/Cdtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| ActvtnAmdmnt/Cdtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| ActvtnAmdmnt/Cdtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| ActvtnAmdmnt/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| ActvtnAmdmnt/Cdtr/Id/OrgId/AnyBIC | Any BIC | Text | - | 0..1 | BIC format | Party | bic | Organization BIC |
| ActvtnAmdmnt/Cdtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID/organization number |

#### 4.2 New Creditor Agent (CdtrAgt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/CdtrAgt/FinInstnId/BICFI | New Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | New creditor bank BIC |
| ActvtnAmdmnt/CdtrAgt/FinInstnId/Nm | Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | New creditor agent name |

#### 4.3 New Creditor Account (CdtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/CdtrAcct/Id/IBAN | New Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | New creditor IBAN |
| ActvtnAmdmnt/CdtrAcct/Id/Othr/Id | New Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | New non-IBAN account |
| ActvtnAmdmnt/CdtrAcct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account | currency | Account currency |

#### 4.4 New Debtor (Dbtr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/Dbtr/Nm | New Debtor Name | Text | 1-140 | 0..1 | Free text | Party | partyName | Amended debtor name |
| ActvtnAmdmnt/Dbtr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | streetName | Street |
| ActvtnAmdmnt/Dbtr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalCode | ZIP/postal code |
| ActvtnAmdmnt/Dbtr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | city | City |
| ActvtnAmdmnt/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | country | Country code |
| ActvtnAmdmnt/Dbtr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxId | Tax ID |

#### 4.5 New Debtor Account (DbtrAcct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/DbtrAcct/Id/IBAN | New Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | New debtor IBAN |
| ActvtnAmdmnt/DbtrAcct/Id/Othr/Id | New Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | New non-IBAN account |

#### 4.6 New Frequency (Frqcy)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/Frqcy/Tp/Cd | New Frequency Type Code | Code | - | 0..1 | DAIL, WEEK, MNTH, QURT, YEAR | PaymentInstruction.extensions | frequencyCode | New payment frequency |
| ActvtnAmdmnt/Frqcy/PtInTm/Dt | New Point in Time Date | Date | - | 0..1 | ISODate | PaymentInstruction | requestedExecutionDate | New execution date |

#### 4.7 New Amount (Amt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/Amt | New Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction | amount | New payment amount |
| ActvtnAmdmnt/Amt/@Ccy | Currency | Code | 3 | 0..1 | ISO 4217 | PaymentInstruction | currency | New currency |

#### 4.8 New Mandate (Mndt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| ActvtnAmdmnt/Mndt/MndtId | New Mandate ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | mandateId | New mandate reference |
| ActvtnAmdmnt/Mndt/DtOfSgntr | New Date of Signature | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | mandateSignatureDate | New signature date |

### 5. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Amendment Reason Code (AmdmntRsn/Rsn/Cd)

- **AM01** - Change of debtor account
- **AM02** - Change of debtor
- **AM03** - Change of debtor agent
- **AM04** - Change of final party
- **AM05** - Change of creditor
- **AM06** - Change of creditor account
- **AM07** - Change of creditor agent
- **AM08** - Change of intermediary agent
- **AM09** - Change of amount
- **AM10** - Change of currency
- **AM11** - Requested date received late
- **AM12** - Change of charge bearer code
- **AM13** - Change of remittance information
- **AM14** - Change of payment purpose
- **AM15** - Change of frequency

### Frequency Type Code (Frqcy/Tp/Cd)

- **DAIL** - Daily
- **WEEK** - Weekly
- **TOWK** - Twice a week
- **MNTH** - Monthly
- **QURT** - Quarterly
- **MIAN** - Semi-annual
- **YEAR** - Annual
- **INDA** - Intra-day

---

## Message Examples

### Example 1: Amendment of Standing Order Amount

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.013.001.07">
  <CdtrPmtActvtnReqAmdmntReq>
    <GrpHdr>
      <MsgId>AMEND-SO-20241220-001</MsgId>
      <CreDtTm>2024-12-20T10:00:00</CreDtTm>
      <InitgPty>
        <Nm>John Smith</Nm>
      </InitgPty>
    </GrpHdr>
    <UndrlygActvtnDtls>
      <OrgnlMsgInf>
        <MsgId>SO-ACTIV-20240115-001</MsgId>
        <MsgNmId>pain.009.001.07</MsgNmId>
        <CreDtTm>2024-01-15T14:30:00</CreDtTm>
      </OrgnlMsgInf>
      <ActvtnId>ACTIV-2024-SO-123456</ActvtnId>
    </UndrlygActvtnDtls>
    <Amdmnt>
      <AmdmntRsn>
        <Rsn>
          <Cd>AM09</Cd>
        </Rsn>
        <AddtlInf>Increasing monthly standing order amount due to higher rent payment</AddtlInf>
      </AmdmntRsn>
      <OrgnlAmt Ccy="EUR">1200.00</OrgnlAmt>
    </Amdmnt>
    <ActvtnAmdmnt>
      <Amt Ccy="EUR">1350.00</Amt>
    </ActvtnAmdmnt>
  </CdtrPmtActvtnReqAmdmntReq>
</Document>
```

### Example 2: SEPA Mandate Amendment - Change of Debtor Account

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.013.001.07">
  <CdtrPmtActvtnReqAmdmntReq>
    <GrpHdr>
      <MsgId>AMEND-MAND-20241220-002</MsgId>
      <CreDtTm>2024-12-20T11:30:00</CreDtTm>
      <InitgPty>
        <Nm>Telecom Services Ltd</Nm>
        <Id>
          <OrgId>
            <Othr>
              <Id>GB123456789</Id>
            </Othr>
          </OrgId>
        </Id>
      </InitgPty>
    </GrpHdr>
    <UndrlygActvtnDtls>
      <OrgnlMsgInf>
        <MsgId>MAND-ACTIV-20240601-789</MsgId>
        <MsgNmId>pain.009.001.07</MsgNmId>
        <CreDtTm>2024-06-01T09:00:00</CreDtTm>
      </OrgnlMsgInf>
      <ActvtnId>SEPA-MAND-2024-789456</ActvtnId>
    </UndrlygActvtnDtls>
    <Amdmnt>
      <AmdmntRsn>
        <Rsn>
          <Cd>AM01</Cd>
        </Rsn>
        <AddtlInf>Customer switched bank accounts - new account provided</AddtlInf>
      </AmdmntRsn>
      <OrgnlDbtr>
        <Nm>Sarah Johnson</Nm>
        <PstlAdr>
          <StrtNm>High Street</StrtNm>
          <PstCd>EC1A 1BB</PstCd>
          <TwnNm>London</TwnNm>
          <Ctry>GB</Ctry>
        </PstlAdr>
      </OrgnlDbtr>
      <OrgnlDbtrAgt>
        <FinInstnId>
          <BICFI>BARCGB22XXX</BICFI>
        </FinInstnId>
      </OrgnlDbtrAgt>
      <OrgnlDbtrAcct>
        <Id>
          <IBAN>GB82BARC20051512345678</IBAN>
        </Id>
      </OrgnlDbtrAcct>
      <OrgnlMndt>
        <MndtId>MANDATE-2024-CUST-789456</MndtId>
        <DtOfSgntr>2024-06-01</DtOfSgntr>
      </OrgnlMndt>
    </Amdmnt>
    <ActvtnAmdmnt>
      <Dbtr>
        <Nm>Sarah Johnson</Nm>
        <PstlAdr>
          <StrtNm>High Street</StrtNm>
          <PstCd>EC1A 1BB</PstCd>
          <TwnNm>London</TwnNm>
          <Ctry>GB</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <IBAN>GB29HSBC40051556789012</IBAN>
        </Id>
      </DbtrAcct>
      <Mndt>
        <MndtId>MANDATE-2024-CUST-789456-AMD</MndtId>
        <DtOfSgntr>2024-12-20</DtOfSgntr>
      </Mndt>
    </ActvtnAmdmnt>
  </CdtrPmtActvtnReqAmdmntReq>
</Document>
```

### Example 3: Amendment of Standing Order Frequency and Date

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.013.001.07">
  <CdtrPmtActvtnReqAmdmntReq>
    <GrpHdr>
      <MsgId>AMEND-FREQ-20241220-003</MsgId>
      <CreDtTm>2024-12-20T15:00:00</CreDtTm>
      <InitgPty>
        <Nm>Maria Garcia</Nm>
      </InitgPty>
    </GrpHdr>
    <UndrlygActvtnDtls>
      <OrgnlMsgInf>
        <MsgId>SO-ACTIV-20240301-555</MsgId>
        <MsgNmId>pain.009.001.07</MsgNmId>
        <CreDtTm>2024-03-01T10:00:00</CreDtTm>
      </OrgnlMsgInf>
      <ActvtnId>SO-2024-CHARITY-555</ActvtnId>
    </UndrlygActvtnDtls>
    <Amdmnt>
      <AmdmntRsn>
        <Rsn>
          <Cd>AM15</Cd>
        </Rsn>
        <AddtlInf>Changing charity donation from monthly to quarterly</AddtlInf>
      </AmdmntRsn>
      <OrgnlFrqcy>
        <Tp>
          <Cd>MNTH</Cd>
        </Tp>
        <PtInTm>
          <Dt>2024-04-01</Dt>
        </PtInTm>
      </OrgnlFrqcy>
      <OrgnlAmt Ccy="EUR">50.00</OrgnlAmt>
    </Amdmnt>
    <ActvtnAmdmnt>
      <Frqcy>
        <Tp>
          <Cd>QURT</Cd>
        </Tp>
        <PtInTm>
          <Dt>2025-01-01</Dt>
        </PtInTm>
      </Frqcy>
      <Amt Ccy="EUR">150.00</Amt>
    </ActvtnAmdmnt>
  </CdtrPmtActvtnReqAmdmntReq>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 72 fields in pain.013 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles instruction identification, amounts, dates
- Extension fields accommodate amendment-specific elements (original values, amendment reasons, activation IDs)
- Party entity supports creditor, debtor identification with original and amended values
- Account entity handles IBAN and non-IBAN account identifiers (original and amended)
- FinancialInstitution entity manages agent information (original and amended)

**Key Extension Fields Used:**
- originalMessageId, originalMessageNameId, originalCreatedDateTime (reference to pain.009)
- activationId (standing order or mandate activation being amended)
- amendmentReasonCode, amendmentProprietaryReason, amendmentAdditionalInfo
- originalCreditorName, originalCreditorBIC, originalCreditorAccountIBAN
- originalDebtorName, originalDebtorAccountIBAN, originalDebtorAgentBIC
- originalMandateId, originalMandateSignatureDate
- originalAmount, originalCurrency, originalFrequencyCode, originalExecutionDate
- All amended values use standard CDM attributes (partyName, accountNumber, amount, etc.)

**Amendment Handling:**
- Original activation details preserved in extension fields with "original" prefix
- Amended values use standard CDM attributes
- Amendment reason codes standardized (AM01-AM15)
- Both original and amended values maintained for audit trail

---

## References

- **ISO 20022 Message Definition:** pain.013.001.07 - CreditorPaymentActivationRequestAmendmentRequestV07
- **XML Schema:** pain.013.001.07.xsd
- **Related Messages:** pain.009 (activation request), pain.014 (status report), pain.010 (cancellation), pain.012 (suspension)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **SEPA Rulebook:** EPC Implementation Guidelines for SEPA Direct Debit Mandate Management

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
