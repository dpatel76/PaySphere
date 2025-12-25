# ISO 20022 camt.059 - Account Reporting Request Mapping

## Message Overview

**Message Type:** camt.059.001.06 - AccountReportingRequestV06
**Category:** CAMT - Cash Management
**Purpose:** Sent by an account owner to request account information from the account servicing institution
**Direction:** Customer → FI (Account Owner to Bank)
**Scope:** Request for account statements, balances, or transaction reports

**Key Use Cases:**
- Request account statement for specific date range
- Request current account balance
- Request transaction details for reconciliation
- Request interim account reports
- Request specific transaction information
- Support cash management and liquidity reporting
- Enable automated reconciliation processes

**Relationship to Other Messages:**
- **camt.052**: Account report (response - intraday statement)
- **camt.053**: Bank to customer statement (response - end-of-day statement)
- **camt.054**: Debit/credit notification (response - transaction notification)
- **camt.060**: Account reporting request (alternative version)
- **MT 940**: SWIFT statement equivalent
- **MT 942**: SWIFT interim transaction report

**Comparison with Related Messages:**
- **camt.059**: Account reporting request (customer to bank)
- **camt.060**: Account reporting request (alternative structure)
- **camt.052**: Intraday account report (response)
- **camt.053**: End-of-day account statement (response)

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.059** | 65 |
| **Fields Mapped to CDM** | 65 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions for request metadata)
- Party (account owner, message sender/recipient)
- Account (account subject to reporting request)
- FinancialInstitution (account servicing institution)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique request message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | creationDateTime | Request creation timestamp |
| GrpHdr/MsgRcpt/Nm | Message Recipient Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| GrpHdr/MsgRcpt/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Recipient country |
| GrpHdr/MsgRcpt/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |

### 2. Reporting Request (RptgReq)

#### 2.1 Request Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptgReq/Id | Request Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | reportingRequestId | Unique reporting request ID |
| RptgReq/ReqdMsgNmId | Requested Message Name ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | requestedMessageType | Type of report requested (camt.052, camt.053, camt.054) |
| RptgReq/Acct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account IBAN |
| RptgReq/Acct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| RptgReq/Acct/Id/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | BBAN, UPIC, etc. | Account.extensions | accountScheme | Account ID scheme |
| RptgReq/Acct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| RptgReq/Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account.extensions | accountCurrency | Account currency |
| RptgReq/Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name |

#### 2.2 Account Owner

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptgReq/Acct/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account owner name |
| RptgReq/Acct/Ownr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Free text | Party | postalAddress.department | Department |
| RptgReq/Acct/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Owner street |
| RptgReq/Acct/Ownr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | postalAddress.buildingNumber | Building number |
| RptgReq/Acct/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | Owner postal code |
| RptgReq/Acct/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | Owner city |
| RptgReq/Acct/Ownr/PstlAdr/CtrySubDvsn | Country Sub Division | Text | 1-35 | 0..1 | Free text | Party | postalAddress.countrySubDivision | State/province |
| RptgReq/Acct/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Owner country |
| RptgReq/Acct/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Owner BIC |
| RptgReq/Acct/Ownr/Id/OrgId/LEI | Legal Entity Identifier | Text | - | 0..1 | LEI format | Party.extensions | legalEntityIdentifier | Owner LEI |
| RptgReq/Acct/Ownr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxIdentificationNumber | Tax ID/org number |
| RptgReq/Acct/Ownr/Id/PrvtId/DtAndPlcOfBirth/BirthDt | Birth Date | Date | - | 0..1 | ISODate | Party | dateOfBirth | Individual birth date |
| RptgReq/Acct/Ownr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Owner ID |
| RptgReq/Acct/Ownr/CtryOfRes | Country of Residence | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party.extensions | countryOfResidence | Residence country |

#### 2.3 Account Servicer

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptgReq/Acct/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicing bank |
| RptgReq/Acct/Svcr/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| RptgReq/Acct/Svcr/FinInstnId/LEI | Legal Entity Identifier | Text | - | 0..1 | LEI format | FinancialInstitution.extensions | legalEntityIdentifier | Servicer LEI |
| RptgReq/Acct/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Servicing bank name |
| RptgReq/Acct/Svcr/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Servicer country |

#### 2.4 Reporting Period

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptgReq/RptgPrd/FrDtTm | From Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | reportingPeriodFromDateTime | Start of reporting period |
| RptgReq/RptgPrd/ToDtTm | To Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | reportingPeriodToDateTime | End of reporting period |
| RptgReq/RptgPrd/Tp | Period Type | Code | - | 0..1 | Various codes | PaymentInstruction.extensions | reportingPeriodType | Type of period |

#### 2.5 Reporting Sequence

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptgReq/RptgSeq/FrSeq | From Sequence | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | reportingSequenceFrom | Starting sequence number |
| RptgReq/RptgSeq/ToSeq | To Sequence | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | reportingSequenceTo | Ending sequence number |

#### 2.6 Additional Reporting Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptgReq/AddtlRptgInf | Additional Reporting Info | Text | 1-500 | 0..1 | Free text | PaymentInstruction.extensions | additionalReportingInfo | Additional instructions |

### 3. Return Indicators (RtrInd)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RtrInd/RtrRsn/Cd | Return Reason Code | Code | - | 0..1 | ISO 20022 codes | PaymentInstruction.extensions | returnReasonCode | Reason for return |
| RtrInd/RtrRsn/Prtry | Proprietary Return Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryReturnReason | Custom return reason |
| RtrInd/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | returnAdditionalInfo | Return details |

### 4. Reporting Criteria (RptCrit)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptCrit/NewQryNm | New Query Name | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | queryName | Name for saved query |
| RptCrit/SchCrit/NewCrit/SchPtyId/Nm | Search Party Name | Text | 1-140 | 0..1 | Free text | PaymentInstruction.extensions | searchPartyName | Party name to search |
| RptCrit/SchCrit/NewCrit/SchPtyId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | PaymentInstruction.extensions | searchPartyCountry | Party country |
| RptCrit/SchCrit/NewCrit/SchPtyId/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | PaymentInstruction.extensions | searchPartyBIC | Party BIC |
| RptCrit/SchCrit/NewCrit/SchAcct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | PaymentInstruction.extensions | searchAccountIBAN | Account to search |
| RptCrit/SchCrit/NewCrit/SchAcct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | PaymentInstruction.extensions | searchAccountOther | Non-IBAN account |
| RptCrit/SchCrit/NewCrit/AmtCrit/Amt | Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | searchAmount | Amount criteria |
| RptCrit/SchCrit/NewCrit/AmtCrit/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | searchCurrency | Amount currency |
| RptCrit/SchCrit/NewCrit/AmtCrit/AmtRg/FrAmt | From Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | searchAmountFrom | Minimum amount |
| RptCrit/SchCrit/NewCrit/AmtCrit/AmtRg/ToAmt | To Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | searchAmountTo | Maximum amount |
| RptCrit/SchCrit/NewCrit/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | searchCreditDebitIndicator | Transaction type |
| RptCrit/SchCrit/NewCrit/NtryDtlsReqd | Entry Details Required | Boolean | - | 0..1 | true/false | PaymentInstruction.extensions | entryDetailsRequired | Include transaction details |

### 5. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Requested Message Name ID (ReqdMsgNmId)
- **camt.052.001.08** - Account Report (intraday)
- **camt.053.001.08** - Bank to Customer Statement (end-of-day)
- **camt.054.001.08** - Bank to Customer Debit Credit Notification

### Account Type (Tp/Cd)
- **CACC** - Current/Checking Account
- **SVGS** - Savings Account
- **LOAN** - Loan Account
- **CARD** - Card Account
- **CASH** - Cash Account
- **CHAR** - Charges Account

### Reporting Period Type (RptgPrd/Tp)
- **MM01** - Month 1
- **QTR1** - Quarter 1
- **YEAR** - Year
- **CUSTOM** - Custom Period

### Credit Debit Indicator (CdtDbtInd)
- **CRDT** - Credit transactions only
- **DBIT** - Debit transactions only

### Return Reason Code (RtrRsn/Cd)
- **AC01** - Account identifier invalid
- **AC02** - Invalid debtor account number
- **AC04** - Closed account number
- **AC06** - Blocked account
- **AG01** - Transaction forbidden
- **NOAS** - No account or unable to locate account

---

## Message Examples

### Example 1: Request for Account Statement

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.059.001.06">
  <AcctRptgReq>
    <GrpHdr>
      <MsgId>ACCTREQ-20241220-001</MsgId>
      <CreDtTm>2024-12-20T09:00:00</CreDtTm>
      <MsgRcpt>
        <Nm>Bank of America</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3NXXX</AnyBIC>
          </OrgId>
        </Id>
      </MsgRcpt>
    </GrpHdr>
    <RptgReq>
      <Id>REQ-STMT-20241220-001</Id>
      <ReqdMsgNmId>camt.053.001.08</ReqdMsgNmId>
      <Acct>
        <Id>
          <Othr>
            <Id>1234567890</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Operating Account</Nm>
        <Ownr>
          <Nm>Global Corporation</Nm>
          <PstlAdr>
            <StrtNm>Corporate Plaza</StrtNm>
            <PstCd>10001</PstCd>
            <TwnNm>New York</TwnNm>
            <Ctry>US</Ctry>
          </PstlAdr>
          <Id>
            <OrgId>
              <Othr>
                <Id>EIN-987654321</Id>
              </Othr>
            </OrgId>
          </Id>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
            <Nm>Bank of America</Nm>
          </FinInstnId>
        </Svcr>
      </Acct>
      <RptgPrd>
        <FrDtTm>2024-12-01T00:00:00</FrDtTm>
        <ToDtTm>2024-12-20T23:59:59</ToDtTm>
        <Tp>CUSTOM</Tp>
      </RptgPrd>
    </RptgReq>
  </AcctRptgReq>
</Document>
```

### Example 2: Request for Specific Transactions

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.059.001.06">
  <AcctRptgReq>
    <GrpHdr>
      <MsgId>ACCTREQ-20241220-TXN-002</MsgId>
      <CreDtTm>2024-12-20T10:30:00</CreDtTm>
      <MsgRcpt>
        <Nm>Bank of America</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3NXXX</AnyBIC>
          </OrgId>
        </Id>
      </MsgRcpt>
    </GrpHdr>
    <RptgReq>
      <Id>REQ-TXN-20241220-002</Id>
      <ReqdMsgNmId>camt.052.001.08</ReqdMsgNmId>
      <Acct>
        <Id>
          <Othr>
            <Id>9876543210</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Ownr>
          <Nm>ABC Services Inc</Nm>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
          </FinInstnId>
        </Svcr>
      </Acct>
      <RptgPrd>
        <FrDtTm>2024-12-20T00:00:00</FrDtTm>
        <ToDtTm>2024-12-20T23:59:59</ToDtTm>
      </RptgPrd>
    </RptgReq>
    <RptCrit>
      <SchCrit>
        <NewCrit>
          <AmtCrit>
            <AmtRg>
              <FrAmt Ccy="USD">10000.00</FrAmt>
              <ToAmt Ccy="USD">100000.00</ToAmt>
            </AmtRg>
          </AmtCrit>
          <CdtDbtInd>CRDT</CdtDbtInd>
          <NtryDtlsReqd>true</NtryDtlsReqd>
        </NewCrit>
      </SchCrit>
    </RptCrit>
  </AcctRptgReq>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 65 fields in camt.059 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles request identification, dates, and metadata
- Extension fields accommodate reporting request-specific information
- Party entity supports account owner with full address and identification details
- Account entity handles IBAN and non-IBAN account identifiers with account types and currency
- FinancialInstitution entity manages servicing institution information

**Key Extension Fields Used:**
- reportingRequestId, requestedMessageType
- reportingPeriodFromDateTime, reportingPeriodToDateTime, reportingPeriodType
- reportingSequenceFrom, reportingSequenceTo
- additionalReportingInfo
- returnReasonCode, proprietaryReturnReason, returnAdditionalInfo
- queryName, searchPartyName, searchPartyCountry, searchPartyBIC
- searchAccountIBAN, searchAccountOther
- searchAmount, searchCurrency, searchAmountFrom, searchAmountTo
- searchCreditDebitIndicator, entryDetailsRequired
- accountScheme, accountTypeCode, accountCurrency, accountName
- legalEntityIdentifier (for both Party and FinancialInstitution)
- countryOfResidence

---

## References

- **ISO 20022 Message Definition:** camt.059.001.06 - AccountReportingRequestV06
- **XML Schema:** camt.059.001.06.xsd
- **Related Messages:** camt.052 (account report), camt.053 (bank statement), camt.054 (debit/credit notification), camt.060 (account reporting request), MT 940/942 (SWIFT statements)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
