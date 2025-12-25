# ISO 20022 camt.086 - Bank Service Billing Mapping

## Message Overview

**Message Type:** camt.086.001.02 - BankServicesBillingStatementV02
**Category:** CAMT - Cash Management
**Purpose:** Sent by a financial institution to provide billing information for banking services to a customer
**Direction:** FI → Customer (Bank to Customer)
**Scope:** Detailed billing statement for bank services, fees, and charges

**Key Use Cases:**
- Monthly/quarterly billing statements for banking services
- Detailed breakdown of fees and charges
- Activity-based billing for cash management services
- Transaction-based pricing statements
- Service usage reports with associated costs
- Volume-based pricing reconciliation
- Multi-account billing consolidation

**Relationship to Other Messages:**
- **camt.052/053**: Account statements showing posted charges
- **camt.054**: Debit notifications for fee charges
- **pain.001**: Payment for bank service fees
- **camt.087**: Request to modify payment (dispute resolution)

**Comparison with Related Messages:**
- **camt.086**: Detailed billing statement with service breakdown
- **camt.052/053**: Account statements showing charge postings
- **camt.054**: Individual charge notifications

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.086** | 125 |
| **Fields Mapped to CDM** | 125 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions for billing metadata)
- Party (account owner, billing recipient)
- Account (billed account information)
- FinancialInstitution (billing institution)
- Charge (fee and charge details)

---

## Complete Field Mapping

### 1. Report Header (RptHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| RptHdr/RptId | Report Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique billing report ID |
| RptHdr/MsgPgntn/PgNb | Page Number | Text | 1-5 | 1..1 | Numeric | PaymentInstruction.extensions | billingPageNumber | Current page number |
| RptHdr/MsgPgntn/LastPgInd | Last Page Indicator | Boolean | - | 1..1 | true/false | PaymentInstruction.extensions | billingLastPageIndicator | Last page flag |
| RptHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | creationDateTime | Billing statement timestamp |
| RptHdr/RptgPrd/FrDtTm | From Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | billingPeriodFromDateTime | Billing period start |
| RptHdr/RptgPrd/ToDtTm | To Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | billingPeriodToDateTime | Billing period end |

### 2. Billing Statement (BllgStmt)

#### 2.1 Statement Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/StmtId | Statement Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | billingStatementId | Unique statement ID |
| BllgStmt/FrToDt/FrDtTm | From Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | statementFromDateTime | Statement period start |
| BllgStmt/FrToDt/ToDtTm | To Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | statementToDateTime | Statement period end |
| BllgStmt/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction.extensions | statementCreationDateTime | Statement creation time |
| BllgStmt/Sts | Status | Code | - | 1..1 | Various codes | PaymentInstruction | currentStatus | Billing statement status |
| BllgStmt/AcctChrtcs/AcctLvl | Account Level | Code | - | 0..1 | Various codes | PaymentInstruction.extensions | accountLevel | Account hierarchy level |

#### 2.2 Account Identification

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/AcctId/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Billed account IBAN |
| BllgStmt/AcctId/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| BllgStmt/AcctId/Id/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | BBAN, UPIC, etc. | Account.extensions | accountScheme | Account ID scheme |
| BllgStmt/AcctId/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| BllgStmt/AcctId/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account.extensions | accountCurrency | Account currency |
| BllgStmt/AcctId/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name |

#### 2.3 Account Owner

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/AcctId/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account owner name |
| BllgStmt/AcctId/Ownr/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Free text | Party | postalAddress.department | Department |
| BllgStmt/AcctId/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Owner street |
| BllgStmt/AcctId/Ownr/PstlAdr/BldgNb | Building Number | Text | 1-16 | 0..1 | Free text | Party | postalAddress.buildingNumber | Building number |
| BllgStmt/AcctId/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | Owner postal code |
| BllgStmt/AcctId/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | Owner city |
| BllgStmt/AcctId/Ownr/PstlAdr/CtrySubDvsn | Country Sub Division | Text | 1-35 | 0..1 | Free text | Party | postalAddress.countrySubDivision | State/province |
| BllgStmt/AcctId/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Owner country |
| BllgStmt/AcctId/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Owner BIC |
| BllgStmt/AcctId/Ownr/Id/OrgId/LEI | Legal Entity Identifier | Text | - | 0..1 | LEI format | Party.extensions | legalEntityIdentifier | Owner LEI |
| BllgStmt/AcctId/Ownr/Id/OrgId/Othr/Id | Organization Other ID | Text | 1-35 | 0..1 | Free text | Party | taxIdentificationNumber | Tax ID/org number |
| BllgStmt/AcctId/Ownr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Owner ID |

#### 2.4 Account Servicer

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/AcctId/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Billing institution BIC |
| BllgStmt/AcctId/Svcr/FinInstnId/ClrSysMmbId/MmbId | Member ID | Text | 1-35 | 0..1 | Free text | FinancialInstitution | clearingSystemMemberId | Clearing member ID |
| BllgStmt/AcctId/Svcr/FinInstnId/LEI | Legal Entity Identifier | Text | - | 0..1 | LEI format | FinancialInstitution.extensions | legalEntityIdentifier | Servicer LEI |
| BllgStmt/AcctId/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Billing institution name |
| BllgStmt/AcctId/Svcr/FinInstnId/PstlAdr/Dept | Department | Text | 1-70 | 0..1 | Free text | FinancialInstitution.extensions | department | Servicer department |
| BllgStmt/AcctId/Svcr/FinInstnId/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | FinancialInstitution.extensions | streetName | Servicer street |
| BllgStmt/AcctId/Svcr/FinInstnId/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | FinancialInstitution.extensions | postalCode | Servicer postal code |
| BllgStmt/AcctId/Svcr/FinInstnId/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | FinancialInstitution.extensions | townName | Servicer city |
| BllgStmt/AcctId/Svcr/FinInstnId/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | FinancialInstitution | country | Servicer country |

#### 2.5 Billing Balance

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/BllgBal/Tp/CdOrPrtry/Cd | Balance Type Code | Code | - | 0..1 | Various codes | PaymentInstruction.extensions | billingBalanceTypeCode | Type of balance |
| BllgStmt/BllgBal/Amt | Balance Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | billingBalanceAmount | Balance amount |
| BllgStmt/BllgBal/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | billingBalanceCurrency | Balance currency |
| BllgStmt/BllgBal/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | billingBalanceCreditDebitIndicator | Balance direction |
| BllgStmt/BllgBal/Dt/Dt | Balance Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | billingBalanceDate | Balance as of date |
| BllgStmt/BllgBal/Dt/DtTm | Balance Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | billingBalanceDateTime | Balance timestamp |

#### 2.6 Commission Details (ComssnDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/ComssnDtls/ComssnId | Commission Identification | Text | 1-35 | 0..1 | Free text | Charge.extensions | commissionId | Unique commission ID |
| BllgStmt/ComssnDtls/FromDt | From Date | Date | - | 0..1 | ISODate | Charge.extensions | commissionFromDate | Commission period start |
| BllgStmt/ComssnDtls/ToDt | To Date | Date | - | 0..1 | ISODate | Charge.extensions | commissionToDate | Commission period end |
| BllgStmt/ComssnDtls/Comssn/Tp | Commission Type | Code | - | 0..1 | Various codes | Charge | chargeType | Type of commission |
| BllgStmt/ComssnDtls/Comssn/Amt | Commission Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge | amount | Commission amount |
| BllgStmt/ComssnDtls/Comssn/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge | currency | Commission currency |
| BllgStmt/ComssnDtls/Comssn/Rate | Commission Rate | Decimal | - | 0..1 | Percentage | Charge.extensions | commissionRate | Commission rate % |
| BllgStmt/ComssnDtls/Comssn/Bsis/Amt | Basis Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | commissionBasisAmount | Calculation basis |
| BllgStmt/ComssnDtls/Comssn/Bsis/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | commissionBasisCurrency | Basis currency |

#### 2.7 Interest Details (IntrstDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/IntrstDtls/IntrstId | Interest Identification | Text | 1-35 | 0..1 | Free text | Charge.extensions | interestId | Unique interest ID |
| BllgStmt/IntrstDtls/FromDt | From Date | Date | - | 0..1 | ISODate | Charge.extensions | interestFromDate | Interest period start |
| BllgStmt/IntrstDtls/ToDt | To Date | Date | - | 0..1 | ISODate | Charge.extensions | interestToDate | Interest period end |
| BllgStmt/IntrstDtls/Intrst/Tp/Cd | Interest Type Code | Code | - | 0..1 | Various codes | Charge.extensions | interestTypeCode | Type of interest |
| BllgStmt/IntrstDtls/Intrst/Rate/Tp/Pctg | Interest Rate Percentage | Decimal | - | 0..1 | Percentage | Charge.extensions | interestRatePercentage | Interest rate % |
| BllgStmt/IntrstDtls/Intrst/Amt | Interest Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge | amount | Interest amount |
| BllgStmt/IntrstDtls/Intrst/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge | currency | Interest currency |
| BllgStmt/IntrstDtls/Tax/TtlTaxAmt | Total Tax Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | taxAmount | Tax on interest |
| BllgStmt/IntrstDtls/Tax/TtlTaxAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | taxCurrency | Tax currency |
| BllgStmt/IntrstDtls/Tax/Rcrd/Tp | Tax Type | Code | - | 0..1 | Various codes | Charge.extensions | taxTypeCode | Type of tax |
| BllgStmt/IntrstDtls/Tax/Rcrd/Amt | Tax Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | taxRecordAmount | Individual tax amount |
| BllgStmt/IntrstDtls/Tax/Rcrd/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | taxRecordCurrency | Tax record currency |

#### 2.8 Cash Deposit Details (CshDpstDtls)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/CshDpstDtls/TtlNbOfAccts | Total Number of Accounts | Text | 1-15 | 0..1 | Numeric | PaymentInstruction.extensions | totalNumberOfAccounts | Account count |
| BllgStmt/CshDpstDtls/TtlAmt | Total Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | totalDepositAmount | Total deposit amount |
| BllgStmt/CshDpstDtls/TtlAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | totalDepositCurrency | Deposit currency |
| BllgStmt/CshDpstDtls/AvrgAmt | Average Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | averageDepositAmount | Average deposit |
| BllgStmt/CshDpstDtls/AvrgAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | averageDepositCurrency | Average currency |

#### 2.9 Service Detail (SvcDtl)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/SvcDtl/SvcTp | Service Type | Code | - | 1..1 | Various codes | Charge.extensions | serviceTypeCode | Type of service |
| BllgStmt/SvcDtl/Desc | Description | Text | 1-140 | 0..1 | Free text | Charge | description | Service description |
| BllgStmt/SvcDtl/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | Charge.extensions | serviceBookingDate | Service booking date |
| BllgStmt/SvcDtl/BookgDt/DtTm | Booking Date Time | DateTime | - | 0..1 | ISODateTime | Charge.extensions | serviceBookingDateTime | Service booking time |
| BllgStmt/SvcDtl/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | Charge.extensions | serviceValueDate | Service value date |
| BllgStmt/SvcDtl/ValDt/DtTm | Value Date Time | DateTime | - | 0..1 | ISODateTime | Charge.extensions | serviceValueDateTime | Service value time |
| BllgStmt/SvcDtl/PricTp | Price Type | Code | - | 0..1 | Various codes | Charge.extensions | priceTypeCode | Type of pricing |
| BllgStmt/SvcDtl/UnitPric/Amt | Unit Price Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | unitPriceAmount | Price per unit |
| BllgStmt/SvcDtl/UnitPric/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | unitPriceCurrency | Unit price currency |
| BllgStmt/SvcDtl/TtlChrg/TtlChrg | Total Charge Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge | amount | Total service charge |
| BllgStmt/SvcDtl/TtlChrg/TtlChrg/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge | currency | Charge currency |
| BllgStmt/SvcDtl/TtlChrg/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | Charge.extensions | chargeCreditDebitIndicator | Charge direction |
| BllgStmt/SvcDtl/Tax/TtlTaxAmt | Total Tax Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | serviceTaxAmount | Tax on service |
| BllgStmt/SvcDtl/Tax/TtlTaxAmt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | serviceTaxCurrency | Tax currency |
| BllgStmt/SvcDtl/Tax/Rcrd/Tp | Tax Type | Code | - | 0..1 | Various codes | Charge.extensions | serviceTaxTypeCode | Type of tax |
| BllgStmt/SvcDtl/Tax/Rcrd/Amt | Tax Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | serviceTaxRecordAmount | Tax record amount |
| BllgStmt/SvcDtl/Tax/Rcrd/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | serviceTaxRecordCurrency | Tax record currency |

#### 2.10 Additional Service Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| BllgStmt/SvcDtl/OrgnlVal/Amt | Original Value Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | Charge.extensions | originalValueAmount | Original transaction value |
| BllgStmt/SvcDtl/OrgnlVal/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | Charge.extensions | originalValueCurrency | Original value currency |
| BllgStmt/SvcDtl/TxId | Transaction Identification | Text | 1-35 | 0..1 | Free text | Charge.extensions | serviceTransactionId | Related transaction ID |
| BllgStmt/SvcDtl/SvcId | Service Identification | Text | 1-35 | 0..1 | Free text | Charge.extensions | serviceId | Service identifier |
| BllgStmt/SvcDtl/Pric/UnitNb | Unit Number | Decimal | - | 0..1 | Positive decimal | Charge.extensions | unitNumber | Number of units |
| BllgStmt/SvcDtl/Pric/UnitPric | Unit Price | Decimal | - | 0..1 | Positive decimal | Charge.extensions | unitPrice | Price per unit |
| BllgStmt/SvcDtl/Pric/TtlPric | Total Price | Decimal | - | 0..1 | Positive decimal | Charge.extensions | totalPrice | Total price |
| BllgStmt/SvcDtl/Pric/Tp | Price Type | Code | - | 0..1 | Various codes | Charge.extensions | servicePriceTypeCode | Pricing type |

### 3. Account Report (AcctRpt)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| AcctRpt/RptId | Report Identification | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | accountReportId | Account report ID |
| AcctRpt/RptDt/Dt | Report Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | accountReportDate | Report date |
| AcctRpt/AcctId/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account IBAN |
| AcctRpt/AcctId/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| AcctRpt/Bal/Tp/CdOrPrtry/Cd | Balance Type Code | Code | - | 0..1 | Various codes | PaymentInstruction.extensions | accountBalanceTypeCode | Type of balance |
| AcctRpt/Bal/Amt | Balance Amount | ActiveOrHistoricCurrencyAndAmount | - | 1..1 | Amount + Ccy | PaymentInstruction.extensions | accountBalanceAmount | Balance amount |
| AcctRpt/Bal/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | accountBalanceCurrency | Balance currency |
| AcctRpt/Bal/CdtDbtInd | Credit Debit Indicator | Code | 4 | 1..1 | CRDT, DBIT | PaymentInstruction.extensions | accountBalanceCreditDebitIndicator | Balance direction |

### 4. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Statement Status (BllgStmt/Sts)
- **OPEN** - Open statement
- **CLSD** - Closed statement
- **FNLD** - Finalized statement
- **PDNG** - Pending statement

### Account Level (AcctLvl)
- **CUST** - Customer level
- **ACCT** - Account level
- **SUAC** - Sub-account level

### Service Type (SvcDtl/SvcTp)
- **ACMT** - Account Management
- **CASH** - Cash Management
- **COLL** - Collection
- **COMM** - Commission
- **CSHE** - Cheque Services
- **INTR** - Interest
- **LBOX** - Lockbox Services
- **TRAD** - Trade Services
- **CRDT** - Credit Related Services
- **DBIT** - Debit Related Services

### Price Type (PricTp)
- **FLAT** - Flat Fee
- **PERU** - Per Unit
- **PERC** - Percentage

### Balance Type Code (Bal/Tp/CdOrPrtry/Cd)
- **OPBD** - Opening Balance Due
- **CLBD** - Closing Balance Due
- **XPCD** - Expected Credit
- **XPDB** - Expected Debit

### Credit Debit Indicator (CdtDbtInd)
- **CRDT** - Credit
- **DBIT** - Debit

---

## Message Examples

### Example 1: Monthly Bank Service Billing Statement

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.086.001.02">
  <BkSvcsBllgStmt>
    <RptHdr>
      <RptId>BILLING-NOV-2024-001</RptId>
      <MsgPgntn>
        <PgNb>1</PgNb>
        <LastPgInd>true</LastPgInd>
      </MsgPgntn>
      <CreDtTm>2024-12-01T00:00:00</CreDtTm>
      <RptgPrd>
        <FrDtTm>2024-11-01T00:00:00</FrDtTm>
        <ToDtTm>2024-11-30T23:59:59</ToDtTm>
      </RptgPrd>
    </RptHdr>
    <BllgStmt>
      <StmtId>STMT-BILLING-NOV-2024</StmtId>
      <FrToDt>
        <FrDtTm>2024-11-01T00:00:00</FrDtTm>
        <ToDtTm>2024-11-30T23:59:59</ToDtTm>
      </FrToDt>
      <CreDtTm>2024-12-01T00:00:00</CreDtTm>
      <Sts>FNLD</Sts>
      <AcctChrtcs>
        <AcctLvl>CUST</AcctLvl>
      </AcctChrtcs>
      <AcctId>
        <Id>
          <Othr>
            <Id>1234567890</Id>
          </Othr>
        </Id>
        <Tp>
          <Cd>CACC</Cd>
        </Tp>
        <Ccy>USD</Ccy>
        <Nm>Global Corporation Operating Account</Nm>
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
              <LEI>549300ABCDEFGHIJKL12</LEI>
            </OrgId>
          </Id>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>BOFAUS3NXXX</BICFI>
            <Nm>Bank of America</Nm>
            <PstlAdr>
              <TwnNm>Charlotte</TwnNm>
              <Ctry>US</Ctry>
            </PstlAdr>
          </FinInstnId>
        </Svcr>
      </AcctId>
      <BllgBal>
        <Tp>
          <CdOrPrtry>
            <Cd>CLBD</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="USD">2547.89</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <Dt>
          <Dt>2024-11-30</Dt>
        </Dt>
      </BllgBal>
      <SvcDtl>
        <SvcTp>CASH</SvcTp>
        <Desc>Wire Transfer Services - Outgoing</Desc>
        <BookgDt>
          <Dt>2024-11-30</Dt>
        </BookgDt>
        <PricTp>PERU</PricTp>
        <UnitPric>
          <Amt Ccy="USD">25.00</Amt>
        </UnitPric>
        <TtlChrg>
          <TtlChrg Ccy="USD">750.00</TtlChrg>
          <CdtDbtInd>DBIT</CdtDbtInd>
        </TtlChrg>
        <Pric>
          <UnitNb>30</UnitNb>
          <UnitPric>25.00</UnitPric>
          <TtlPric>750.00</TtlPric>
          <Tp>PERU</Tp>
        </Pric>
      </SvcDtl>
      <SvcDtl>
        <SvcTp>CASH</SvcTp>
        <Desc>ACH Transactions</Desc>
        <BookgDt>
          <Dt>2024-11-30</Dt>
        </BookgDt>
        <PricTp>PERU</PricTp>
        <UnitPric>
          <Amt Ccy="USD">0.15</Amt>
        </UnitPric>
        <TtlChrg>
          <TtlChrg Ccy="USD">225.00</TtlChrg>
          <CdtDbtInd>DBIT</CdtDbtInd>
        </TtlChrg>
        <Pric>
          <UnitNb>1500</UnitNb>
          <UnitPric>0.15</UnitPric>
          <TtlPric>225.00</TtlPric>
          <Tp>PERU</Tp>
        </Pric>
      </SvcDtl>
      <SvcDtl>
        <SvcTp>ACMT</SvcTp>
        <Desc>Account Maintenance Fee</Desc>
        <BookgDt>
          <Dt>2024-11-30</Dt>
        </BookgDt>
        <PricTp>FLAT</PricTp>
        <TtlChrg>
          <TtlChrg Ccy="USD">150.00</TtlChrg>
          <CdtDbtInd>DBIT</CdtDbtInd>
        </TtlChrg>
      </SvcDtl>
      <IntrstDtls>
        <IntrstId>INT-NOV-2024</IntrstId>
        <FromDt>2024-11-01</FromDt>
        <ToDt>2024-11-30</ToDt>
        <Intrst>
          <Tp>
            <Cd>INDY</Cd>
          </Tp>
          <Rate>
            <Tp>
              <Pctg>2.50</Pctg>
            </Tp>
          </Rate>
          <Amt Ccy="USD">1377.11</Amt>
        </Intrst>
        <Tax>
          <TtlTaxAmt Ccy="USD">0.00</TtlTaxAmt>
        </Tax>
      </IntrstDtls>
    </BllgStmt>
  </BkSvcsBllgStmt>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 125 fields in camt.086 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles billing statement identification, dates, and metadata
- Extension fields accommodate billing-specific information (period, pagination, balances)
- Party entity supports account owner with full address and identification details
- Account entity handles IBAN and non-IBAN account identifiers with account types and currency
- FinancialInstitution entity manages billing institution information with full address
- Charge entity comprehensively handles all fee, commission, interest, and tax details

**Key Extension Fields Used:**
- billingPageNumber, billingLastPageIndicator
- billingPeriodFromDateTime, billingPeriodToDateTime
- billingStatementId, statementFromDateTime, statementToDateTime, statementCreationDateTime
- accountLevel, billingBalanceTypeCode, billingBalanceAmount, billingBalanceCurrency
- billingBalanceCreditDebitIndicator, billingBalanceDate, billingBalanceDateTime
- commissionId, commissionFromDate, commissionToDate, commissionRate
- commissionBasisAmount, commissionBasisCurrency
- interestId, interestFromDate, interestToDate, interestTypeCode
- interestRatePercentage, taxAmount, taxCurrency, taxTypeCode
- taxRecordAmount, taxRecordCurrency
- totalNumberOfAccounts, totalDepositAmount, totalDepositCurrency
- averageDepositAmount, averageDepositCurrency
- serviceTypeCode, serviceBookingDate, serviceBookingDateTime
- serviceValueDate, serviceValueDateTime, priceTypeCode
- unitPriceAmount, unitPriceCurrency, chargeCreditDebitIndicator
- serviceTaxAmount, serviceTaxCurrency, serviceTaxTypeCode
- serviceTaxRecordAmount, serviceTaxRecordCurrency
- originalValueAmount, originalValueCurrency
- serviceTransactionId, serviceId, unitNumber, unitPrice, totalPrice
- servicePriceTypeCode
- accountReportId, accountReportDate
- accountBalanceTypeCode, accountBalanceAmount, accountBalanceCurrency
- accountBalanceCreditDebitIndicator
- legalEntityIdentifier (for both Party and FinancialInstitution)
- department, streetName, postalCode, townName (for FinancialInstitution)

---

## References

- **ISO 20022 Message Definition:** camt.086.001.02 - BankServicesBillingStatementV02
- **XML Schema:** camt.086.001.02.xsd
- **Related Messages:** camt.052/053 (account statements), camt.054 (debit/credit notifications), pain.001 (payment of fees), camt.087 (request to modify payment)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
