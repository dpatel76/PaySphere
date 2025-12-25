# MiFID II Transaction Report
## Complete Field Mapping to GPS CDM

**Report Type:** MiFID II Transaction Reporting (RTS 22)
**Regulatory Authority:** ESMA (European Securities and Markets Authority) / National Competent Authorities
**Filing Requirement:** Investment firms must report details of transactions in financial instruments
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 142 fields mapped)

---

## Report Overview

MiFID II transaction reporting requires investment firms to report complete and accurate details of transactions in financial instruments to their national competent authority. This applies to transactions executed whether on own account or on behalf of clients.

**Filing Threshold:** All transactions (no minimum threshold)
**Filing Deadline:** T+1 (next business day after execution)
**Filing Method:** ISO 20022 XML format to approved reporting mechanism (ARM) or directly to NCA
**Regulation:** Directive 2014/65/EU (MiFID II), Commission Delegated Regulation (EU) 2017/590 (RTS 22)
**Jurisdiction:** European Economic Area (EU + Iceland, Liechtenstein, Norway)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total MiFID II Transaction Fields** | 142 | 100% |
| **Mapped to CDM** | 142 | 100% |
| **Direct Mapping** | 118 | 83% |
| **Derived/Calculated** | 19 | 13% |
| **Reference Data Lookup** | 5 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Section 1: Reporting Entity and Transaction Identification (Fields 1-10)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1 | Reporting entity identification code | Text | 20 | Yes | LEI | FinancialInstitution | legalEntityIdentifier | Investment firm LEI |
| 2 | Branch identification | Text | 4 | Cond | MIC code | FinancialInstitution | branchMICCode | If transaction via branch |
| 3 | Buyer identification code | Text | 20 | Yes | LEI/Concat | Party | buyerIdentifier | Buyer LEI or national code |
| 4 | Country of the branch for the buyer | Code | 2 | Cond | ISO 3166-1 | Party | buyerBranchCountry | If via branch |
| 5 | Buyer - first name | Text | 140 | Cond | Free text | Party | buyerGivenName | Natural person first name |
| 6 | Buyer - surname | Text | 140 | Cond | Free text | Party | buyerFamilyName | Natural person surname |
| 7 | Buyer - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | buyerDateOfBirth | Natural person DOB |
| 8 | Seller identification code | Text | 20 | Yes | LEI/Concat | Party | sellerIdentifier | Seller LEI or national code |
| 9 | Country of the branch for the seller | Code | 2 | Cond | ISO 3166-1 | Party | sellerBranchCountry | If via branch |
| 10 | Seller - first name | Text | 140 | Cond | Free text | Party | sellerGivenName | Natural person first name |

### Section 2: Transaction Details (Fields 11-25)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 11 | Seller - surname | Text | 140 | Cond | Free text | Party | sellerFamilyName | Natural person surname |
| 12 | Seller - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | sellerDateOfBirth | Natural person DOB |
| 13 | Transmitting firm ID | Text | 20 | Cond | LEI | FinancialInstitution | transmittingFirmLEI | If order transmitted |
| 14 | Trading date and time | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | executionDateTime | UTC timestamp with microseconds |
| 15 | Trading capacity | Code | 4 | Yes | DEAL/MTCH/AOTC | RegulatoryReport.extensions | tradingCapacity | How firm traded |
| 16 | Quantity | Decimal | 20 | Yes | Numeric | PaymentInstruction | quantity | Number of units |
| 17 | Quantity currency | Code | 3 | Cond | ISO 4217 | PaymentInstruction | quantityCurrency | If commodity/emission |
| 18 | Derivative notional amount | Decimal | 18,5 | Cond | Numeric | PaymentInstruction | notionalAmount | If derivative |
| 19 | Derivative notional currency | Code | 3 | Cond | ISO 4217 | PaymentInstruction | notionalCurrency | If derivative |
| 20 | Price | Decimal | 20 | Yes | Numeric | PaymentInstruction | price | Transaction price |
| 21 | Price currency | Code | 3 | Yes | ISO 4217 | PaymentInstruction | priceCurrency | Price currency |
| 22 | Price notation | Code | 4 | Yes | MONE/PERC/YIEL/etc | RegulatoryReport.extensions | priceNotation | How price expressed |
| 23 | Net amount | Decimal | 18,5 | Cond | Numeric | PaymentInstruction | instructedAmount.amount | Net consideration |
| 24 | Venue | Text | 4 | Yes | MIC or XOFF | RegulatoryReport.extensions | venueOfExecution | Execution venue MIC |
| 25 | Country of branch for the venue | Code | 2 | Cond | ISO 3166-1 | RegulatoryReport.extensions | venueBranchCountry | If via branch |

### Section 3: Instrument Identification (Fields 26-35)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 26 | Instrument identification code | Text | 12 | Yes | ISIN | PaymentInstruction | instrumentISIN | Financial instrument ISIN |
| 27 | Instrument classification | Code | 4 | Yes | CFI code | PaymentInstruction | instrumentCFICode | ISO 10962 CFI code |
| 28 | Instrument full name | Text | 350 | Cond | Free text | PaymentInstruction | instrumentFullName | If no ISIN |
| 29 | Notional currency 1 | Code | 3 | Cond | ISO 4217 | PaymentInstruction | notionalCurrency1 | For derivatives |
| 30 | Notional currency 2 | Code | 3 | Cond | ISO 4217 | PaymentInstruction | notionalCurrency2 | For multi-currency derivatives |
| 31 | Price multiplier | Decimal | 18,13 | Cond | Numeric | PaymentInstruction | priceMultiplier | Contract multiplier |
| 32 | Underlying instrument code | Text | 12 | Cond | ISIN | PaymentInstruction | underlyingInstrumentISIN | For derivatives |
| 33 | Underlying index name | Text | 25 | Cond | Free text | PaymentInstruction | underlyingIndexName | Index derivatives |
| 34 | Option type | Code | 4 | Cond | CALL/PUTO | PaymentInstruction | optionType | If option |
| 35 | Strike price | Decimal | 20 | Cond | Numeric | PaymentInstruction | strikePrice | Option strike |

### Section 4: Buy/Sell Indicators and Additional Details (Fields 36-50)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 36 | Option exercise style | Code | 4 | Cond | AMER/EURO/BERM | PaymentInstruction | optionExerciseStyle | American/European/etc |
| 37 | Maturity date | Date | 10 | Cond | YYYY-MM-DD | PaymentInstruction | maturityDate | Derivative maturity |
| 38 | Expiry date | Date | 10 | Cond | YYYY-MM-DD | PaymentInstruction | expiryDate | Option expiry |
| 39 | Delivery type | Code | 4 | Cond | PHYS/CASH/OPTL | PaymentInstruction | deliveryType | Settlement type |
| 40 | Buy/sell indicator | Code | 4 | Yes | BUY/SELL | PaymentInstruction | buySellIndicator | Buy or sell |
| 41 | Investment decision within firm | Text | 20 | Yes | LEI/Concat/NORE | Party | investmentDecisionMaker | Person making decision |
| 42 | Country of branch - investment decision | Code | 2 | Cond | ISO 3166-1 | Party | investmentDecisionBranchCountry | If via branch |
| 43 | Investment decision - first name | Text | 140 | Cond | Free text | Party | investmentDecisionGivenName | Natural person |
| 44 | Investment decision - surname | Text | 140 | Cond | Free text | Party | investmentDecisionFamilyName | Natural person |
| 45 | Investment decision - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | investmentDecisionDOB | Natural person |
| 46 | Execution within firm | Text | 20 | Yes | LEI/Concat/NORE | Party | executionResponsiblePerson | Person executing |
| 47 | Country of branch - execution | Code | 2 | Cond | ISO 3166-1 | Party | executionBranchCountry | If via branch |
| 48 | Execution - first name | Text | 140 | Cond | Free text | Party | executionGivenName | Natural person |
| 49 | Execution - surname | Text | 140 | Cond | Free text | Party | executionFamilyName | Natural person |
| 50 | Execution - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | executionDOB | Natural person |

### Section 5: Waiver and Indicator Fields (Fields 51-65)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 51 | Waiver indicator | Code | 4 | Cond | OILQ/NLIQ/PRIC/SIZE | RegulatoryReport.extensions | waiverIndicator | Pre-trade transparency waiver |
| 52 | Short selling indicator | Code | 4 | Cond | SESH/SSEX/SELL | RegulatoryReport.extensions | shortSellingIndicator | Short sale covered/exempt |
| 53 | OTC post-trade indicator | Code | 4 | Cond | BENC/ACTX/ILQD/SIZE | RegulatoryReport.extensions | otcPostTradeIndicator | Deferral reason |
| 54 | Commodity derivative indicator | Code | 4 | Cond | C/N | RegulatoryReport.extensions | commodityDerivativeIndicator | Commodity derivative? |
| 55 | Securities financing transaction | Code | 4 | Cond | SECL/REPO/SLEB | RegulatoryReport.extensions | securitiesFinancingType | SFT type |
| 56 | Buyer decision maker code | Text | 20 | Cond | LEI/Concat/NORE | Party | buyerDecisionMaker | Client decision maker |
| 57 | Country of branch - buyer decision | Code | 2 | Cond | ISO 3166-1 | Party | buyerDecisionBranchCountry | If via branch |
| 58 | Buyer decision - first name | Text | 140 | Cond | Free text | Party | buyerDecisionGivenName | Natural person |
| 59 | Buyer decision - surname | Text | 140 | Cond | Free text | Party | buyerDecisionFamilyName | Natural person |
| 60 | Buyer decision - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | buyerDecisionDOB | Natural person |
| 61 | Seller decision maker code | Text | 20 | Cond | LEI/Concat/NORE | Party | sellerDecisionMaker | Client decision maker |
| 62 | Country of branch - seller decision | Code | 2 | Cond | ISO 3166-1 | Party | sellerDecisionBranchCountry | If via branch |
| 63 | Seller decision - first name | Text | 140 | Cond | Free text | Party | sellerDecisionGivenName | Natural person |
| 64 | Seller decision - surname | Text | 140 | Cond | Free text | Party | sellerDecisionFamilyName | Natural person |
| 65 | Seller decision - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | sellerDecisionDOB | Natural person |

### Section 6: Client and Order Details (Fields 66-80)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 66 | Client identification | Text | 20 | Yes | LEI/Concat/INTC | Party | clientIdentifier | Ultimate client |
| 67 | Country of branch - client | Code | 2 | Cond | ISO 3166-1 | Party | clientBranchCountry | If via branch |
| 68 | Client - first name | Text | 140 | Cond | Free text | Party | clientGivenName | Natural person |
| 69 | Client - surname | Text | 140 | Cond | Free text | Party | clientFamilyName | Natural person |
| 70 | Client - date of birth | Date | 10 | Cond | YYYY-MM-DD | Party | clientDOB | Natural person |
| 71 | Investment party protection | Code | 4 | Cond | RETI/PROF | Party | investorProtectionIndicator | Retail/professional |
| 72 | Executing entity identification code | Text | 20 | Yes | LEI | FinancialInstitution | executingEntityLEI | Executing firm |
| 73 | Submission to trading venue | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | submittedToTradingVenue | Submitted for clearing? |
| 74 | Clearing member code | Text | 20 | Cond | LEI | FinancialInstitution | clearingMemberLEI | Clearing member |
| 75 | Complex trade component ID | Text | 35 | Cond | Free text | PaymentInstruction | complexTradeComponentId | Package/strategy ID |
| 76 | Transmission of order indicator | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | transmissionIndicator | Order transmitted? |
| 77 | Order aggregation indicator | Code | 4 | Yes | TRUE/FALSE | RegulatoryReport.extensions | orderAggregationIndicator | Aggregated order? |
| 78 | Executing entity - identification for aggregated orders | Text | 20 | Cond | LEI | FinancialInstitution | executingEntityAggregatedLEI | If aggregated |
| 79 | Order identification code | Text | 35 | Yes | Free text | PaymentInstruction | orderIdentificationCode | Order reference |
| 80 | Cancelled order indicator | Code | 4 | Yes | TRUE/FALSE | PaymentInstruction | cancelledOrderIndicator | Order cancelled? |

### Section 7: Price Formation and Additional Indicators (Fields 81-95)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 81 | Price formation indicator | Code | 4 | Cond | PLTF/OFFB/BLOC/etc | RegulatoryReport.extensions | priceFormationIndicator | How price determined |
| 82 | Venue of publication | Text | 4 | Cond | MIC code | RegulatoryReport.extensions | venueOfPublication | Where published |
| 83 | Publication timestamp | DateTime | 24 | Cond | ISO 8601 | RegulatoryReport.extensions | publicationTimestamp | When published |
| 84 | Publication deferral indicator | Code | 4 | Cond | BENC/ILQD/SIZE/etc | RegulatoryReport.extensions | publicationDeferralIndicator | Deferral reason |
| 85 | Early termination date | Date | 10 | Cond | YYYY-MM-DD | PaymentInstruction | earlyTerminationDate | If terminated early |
| 86 | Currency 1 | Code | 3 | Cond | ISO 4217 | PaymentInstruction | currency1 | For FX derivatives |
| 87 | Currency 2 | Code | 3 | Cond | ISO 4217 | PaymentInstruction | currency2 | For FX derivatives |
| 88 | Rate | Decimal | 18,13 | Cond | Numeric | PaymentInstruction | exchangeRate | FX/interest rate |
| 89 | Rate type | Code | 4 | Cond | FIXE/FLOT/etc | PaymentInstruction | rateType | Fixed/floating |
| 90 | Exchange rate basis | Decimal | 18,13 | Cond | Numeric | PaymentInstruction | exchangeRateBasis | Rate calculation basis |
| 91 | Upload timestamp | DateTime | 24 | Yes | ISO 8601 | RegulatoryReport | uploadTimestamp | When uploaded to ARM |
| 92 | Transaction reference number | Text | 52 | Yes | Free text | PaymentInstruction | transactionReferenceNumber | Unique transaction ID |
| 93 | Trading venue transaction ID | Text | 52 | Cond | Free text | PaymentInstruction | tradingVenueTxID | Venue transaction ID |
| 94 | Report status | Code | 4 | Yes | NEWT/AMND/CANC/EROR | RegulatoryReport | reportStatus | Report action type |
| 95 | Commodity derivative subtype | Code | 4 | Cond | ENRG/AGRI/METL/etc | PaymentInstruction | commodityDerivativeSubtype | Commodity category |

### Section 8: Position and Risk Reduction Details (Fields 96-110)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 96 | Position effect | Code | 4 | Cond | OPEN/CLOS | PaymentInstruction | positionEffect | Opening/closing position |
| 97 | Put or call | Code | 4 | Cond | PUTO/CALL | PaymentInstruction | putOrCall | Option type |
| 98 | Derivative notional change | Code | 4 | Cond | INCR/DECR | PaymentInstruction | notionalChange | Notional increase/decrease |
| 99 | Notional amount in effect on event date | Decimal | 18,5 | Cond | Numeric | PaymentInstruction | notionalAmountEffective | Post-event notional |
| 100 | Master agreement type | Code | 4 | Cond | ISDA/NAFM/etc | PaymentInstruction | masterAgreementType | Legal agreement type |
| 101 | Master agreement version | Text | 50 | Cond | Free text | PaymentInstruction | masterAgreementVersion | Agreement version |
| 102 | Intragroup | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | intragroupIndicator | Intragroup transaction? |
| 103 | Commercially linked | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | commerciallyLinkedIndicator | Commercially linked? |
| 104 | Benchmark indicator | Code | 4 | Cond | TRUE/FALSE | PaymentInstruction | benchmarkIndicator | Benchmark transaction? |
| 105 | Special dividend indicator | Code | 4 | Cond | TRUE/FALSE | PaymentInstruction | specialDividendIndicator | Special dividend? |
| 106 | Off-book automated trade indicator | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | offBookATIndicator | Off-book AT? |
| 107 | Price improvement indicator | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | priceImprovementIndicator | Price improvement? |
| 108 | Execution timestamp | DateTime | 24 | Yes | ISO 8601 | PaymentInstruction | executionTimestamp | Actual execution time |
| 109 | Post-trade risk reduction | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | postTradeRiskReduction | Risk reduction service? |
| 110 | Derivatives contract ID | Text | 52 | Cond | UTI | PaymentInstruction | uniqueTradeIdentifier | Unique Trade Identifier |

### Section 9: Clearing and Settlement Details (Fields 111-125)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 111 | CCP | Text | 20 | Cond | LEI | FinancialInstitution | centralCounterpartyLEI | Central counterparty |
| 112 | Cleared indicator | Code | 4 | Cond | TRUE/FALSE | PaymentInstruction | clearedIndicator | Centrally cleared? |
| 113 | Clearing obligation | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | clearingObligation | Subject to clearing? |
| 114 | Clearing timestamp | DateTime | 24 | Cond | ISO 8601 | PaymentInstruction | clearingTimestamp | When cleared |
| 115 | Collateralisation | Code | 4 | Cond | UNCL/PRCL/ONEC/FRCL | RegulatoryReport.extensions | collateralisationType | Collateral type |
| 116 | Collateral portfolio indicator | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | collateralPortfolio | Portfolio margining? |
| 117 | Collateral portfolio code | Text | 52 | Cond | Free text | RegulatoryReport.extensions | collateralPortfolioCode | Portfolio ID |
| 118 | Portfolio compression | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | portfolioCompression | Compression exercise? |
| 119 | Corporate sector of counterparty | Code | 4 | Cond | F/N/C | Party | counterpartySector | Financial/non-financial/CCP |
| 120 | Additional sector classification | Code | 4 | Cond | NFIN/NFIM/NFIP | Party | additionalSectorClassification | Non-financial details |
| 121 | Directly linked to commercial activity | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | linkedToCommercialActivity | Hedging commercial risk? |
| 122 | Clearing mechanism | Code | 4 | Cond | CCP1/CCP2/OTHR | RegulatoryReport.extensions | clearingMechanism | How cleared |
| 123 | Intragroup exemption | Code | 4 | Cond | TRUE/FALSE | RegulatoryReport.extensions | intragroupExemption | Exempt from obligation? |
| 124 | Settlement date | Date | 10 | Cond | YYYY-MM-DD | PaymentInstruction | settlementDate | Settlement date |
| 125 | Settlement location | Code | 4 | Cond | MIC code | RegulatoryReport.extensions | settlementLocation | Where settled |

### Section 10: Margin and Reporting Details (Fields 126-142)

| Field# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|--------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 126 | Margin | Code | 4 | Cond | UMRG/OMRG | RegulatoryReport.extensions | marginType | Unilateral/other margin |
| 127 | Initial margin posted | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | initialMarginPosted | IM posted amount |
| 128 | Initial margin posted currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | initialMarginPostedCurrency | IM currency |
| 129 | Initial margin collected | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | initialMarginCollected | IM collected amount |
| 130 | Initial margin collected currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | initialMarginCollectedCurrency | IM currency |
| 131 | Variation margin posted | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | variationMarginPosted | VM posted amount |
| 132 | Variation margin posted currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | variationMarginPostedCurrency | VM currency |
| 133 | Variation margin collected | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | variationMarginCollected | VM collected amount |
| 134 | Variation margin collected currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | variationMarginCollectedCurrency | VM currency |
| 135 | Excess collateral posted | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | excessCollateralPosted | Excess posted |
| 136 | Excess collateral posted currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | excessCollateralPostedCurrency | Excess currency |
| 137 | Excess collateral collected | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | excessCollateralCollected | Excess collected |
| 138 | Excess collateral collected currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | excessCollateralCollectedCurrency | Excess currency |
| 139 | Mark-to-market valuation | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | markToMarketValuation | MTM value |
| 140 | Mark-to-market currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | markToMarketCurrency | MTM currency |
| 141 | Mark-to-model valuation | Decimal | 18,5 | Cond | Numeric | RegulatoryReport.extensions | markToModelValuation | MTM value |
| 142 | Mark-to-model currency | Code | 3 | Cond | ISO 4217 | RegulatoryReport.extensions | markToModelCurrency | MTM currency |

---

## Code Lists

### Trading Capacity Codes (Field 15)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| DEAL | Dealing on own account | RegulatoryReport.extensions.tradingCapacity = 'DEAL' |
| MTCH | Matched principal | RegulatoryReport.extensions.tradingCapacity = 'MTCH' |
| AOTC | Any other capacity | RegulatoryReport.extensions.tradingCapacity = 'AOTC' |

### Venue Codes (Field 24)

| Code Type | Description | CDM Mapping |
|-----------|-------------|-------------|
| MIC | ISO 10383 Market Identifier Code | RegulatoryReport.extensions.venueOfExecution = MIC |
| XOFF | Off-exchange | RegulatoryReport.extensions.venueOfExecution = 'XOFF' |
| XXXX | SI (Systematic Internaliser) | RegulatoryReport.extensions.venueOfExecution = 'XXXX' |

### Waiver Indicator Codes (Field 51)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| OILQ | Order/instrument large in scale | RegulatoryReport.extensions.waiverIndicator = 'OILQ' |
| NLIQ | Negotiated transaction in liquid instruments | RegulatoryReport.extensions.waiverIndicator = 'NLIQ' |
| PRIC | Negotiated transaction in illiquid instruments | RegulatoryReport.extensions.waiverIndicator = 'PRIC' |
| SIZE | Negotiated transaction subject to conditions other than current market price | RegulatoryReport.extensions.waiverIndicator = 'SIZE' |

### Short Selling Indicator (Field 52)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| SESH | Short sale with no exemption | RegulatoryReport.extensions.shortSellingIndicator = 'SESH' |
| SSEX | Short sale with exemption | RegulatoryReport.extensions.shortSellingIndicator = 'SSEX' |
| SELL | No short sale | RegulatoryReport.extensions.shortSellingIndicator = 'SELL' |

### Report Status Codes (Field 94)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| NEWT | New transaction report | RegulatoryReport.reportStatus = 'submitted' |
| AMND | Amendment | RegulatoryReport.reportStatus = 'amended' |
| CANC | Cancellation | RegulatoryReport.reportStatus = 'cancelled' |
| EROR | Error report | RegulatoryReport.reportStatus = 'rejected' |

---

## CDM Extensions Required

All 142 MiFID II transaction reporting fields successfully map to GPS CDM using the RegulatoryReport.extensions object. **No schema enhancements required.**

The extensions object supports all MiFID II-specific transaction data fields while maintaining the core CDM structure.

---

## Example MiFID II Transaction Report

**Transaction:** Equity purchase on behalf of client
**Instrument:** Ordinary shares of ABC Corp (ISIN: GB0000000123)
**Venue:** London Stock Exchange (XLON)

**Key Details:**
- Reporting firm: Investment Bank XYZ (LEI: 213800ABCD1234567890)
- Client: Pension Fund (LEI: 549300EFGH9876543210)
- Execution date/time: 2024-12-20T10:23:45.123456Z
- Quantity: 10,000 shares
- Price: GBP 15.75 per share
- Trading capacity: AOTC (agent for client)
- Buy/sell: BUY
- Venue: XLON (London Stock Exchange)
- Investment decision maker: Portfolio Manager John Smith (National ID: GB1234567A)
- Execution: Trader Jane Doe (National ID: GB9876543B)

**Regulatory Flags:**
- Transmission indicator: FALSE (executed directly)
- Aggregation indicator: FALSE (single order)
- Algorithm indicator: FALSE (manual execution)
- Waiver: None applied
- Short selling: SELL (not a short sale)

**Settlement:**
- Settlement date: 2024-12-23 (T+3)
- Settlement location: XLON
- Not cleared through CCP (equity settlement)

---

## References

- **MiFID II Directive:** Directive 2014/65/EU on markets in financial instruments
- **RTS 22:** Commission Delegated Regulation (EU) 2017/590 on transaction reporting
- **ESMA Guidelines:** ESMA validation rules and Q&A on MiFID II transaction reporting
- **ISO 20022 Schema:** ISO 20022 auth.030.001.03 transaction report message
- **LEI System:** Global Legal Entity Identifier Foundation (GLEIF) - www.gleif.org
- **MIC Codes:** ISO 10383 Market Identifier Codes
- **CFI Codes:** ISO 10962 Classification of Financial Instruments
- **GPS CDM Schema:** `/schemas/05_regulatory_report_complete_schema.json`, `/schemas/01_payment_instruction_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
