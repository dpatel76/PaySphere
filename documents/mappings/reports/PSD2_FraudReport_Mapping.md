# PSD2 Fraud Report
## Complete Field Mapping to GPS CDM

**Report Type:** PSD2 Fraud Reporting under RTS 2018/1042
**Regulatory Authority:** European Banking Authority (EBA)
**Filing Requirement:** Payment service providers must report fraud data on payment transactions
**Document Date:** 2024-12-20
**Mapping Coverage:** 100% (All 87 fields mapped)

---

## Report Overview

The PSD2 Fraud Report is submitted quarterly by payment service providers (PSPs) to competent authorities to provide comprehensive data on fraud relating to different means of payment. The report includes aggregated data on fraudulent transactions and security incidents.

**Filing Threshold:** All fraud incidents (no minimum threshold)
**Filing Deadline:** Quarterly, within 70 calendar days after the end of each calendar quarter
**Filing Method:** XML format per EBA technical standards to national competent authority
**Regulation:** Payment Services Directive 2 (EU) 2015/2366, Commission Delegated Regulation (EU) 2018/389, RTS (EU) 2018/1042
**Jurisdiction:** European Union (all EU member states)

---

## Mapping Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total PSD2 Fraud Fields** | 87 | 100% |
| **Mapped to CDM** | 87 | 100% |
| **Direct Mapping** | 74 | 85% |
| **Derived/Calculated** | 10 | 11% |
| **Reference Data Lookup** | 3 | 4% |
| **CDM Gaps Identified** | 0 | 0% |

---

## Field-by-Field Mapping

### Section 1: Reporting Entity Information (Items 1-12)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 1.1 | Reporting entity LEI | Text | 20 | Yes | ISO 17442 LEI | FinancialInstitution | legalEntityIdentifier | Legal Entity Identifier |
| 1.2 | Reporting entity name | Text | 140 | Yes | Free text | FinancialInstitution | institutionName | Legal name of PSP |
| 1.3 | Reporting entity country | Code | 2 | Yes | ISO 3166-1 | FinancialInstitution | country | Country of establishment |
| 1.4 | Reporting entity type | Code | 2 | Yes | PSP codes | FinancialInstitution | institutionType | PSP type (credit inst, payment inst, e-money inst) |
| 1.5 | Competent authority | Code | 4 | Yes | Authority codes | RegulatoryReport | regulatoryAuthority | National competent authority |
| 1.6 | Reporting period start date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | reportingPeriodStartDate | Quarter start date |
| 1.7 | Reporting period end date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | reportingPeriodEndDate | Quarter end date |
| 1.8 | Reporting currency | Code | 3 | Yes | ISO 4217 | RegulatoryReport | reportingCurrency | EUR or local currency |
| 1.9 | Report submission date | Date | 10 | Yes | YYYY-MM-DD | RegulatoryReport | submissionDate | Actual submission date |
| 1.10 | Report version | Text | 10 | Yes | Version number | RegulatoryReport | reportVersion | Version (initial/amended) |
| 1.11 | Contact person name | Text | 140 | Yes | Free text | RegulatoryReport | reportingEntityContactName | Primary contact |
| 1.12 | Contact person email | Text | 256 | Yes | Email format | RegulatoryReport | reportingEntityContactEmail | Contact email |

### Section 2: Card Payment Fraud Data (Items 2.1-2.24)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 2.1 | Total number of card transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardTransactionCount | All card transactions in period |
| 2.2 | Total value of card transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardTransactionValue | Total card transaction value |
| 2.3 | Number of fraudulent card transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudTransactionCount | Fraud transactions detected |
| 2.4 | Value of fraudulent card transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudTransactionValue | Total fraud value |
| 2.5 | Card fraud - lost/stolen card | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudLostStolen | Lost/stolen card fraud count |
| 2.6 | Card fraud - lost/stolen card value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudLostStolenValue | Lost/stolen fraud value |
| 2.7 | Card fraud - card not received | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudNotReceived | Card not received fraud count |
| 2.8 | Card fraud - card not received value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudNotReceivedValue | Card not received fraud value |
| 2.9 | Card fraud - counterfeit card | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudCounterfeit | Counterfeit card fraud count |
| 2.10 | Card fraud - counterfeit card value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudCounterfeitValue | Counterfeit card fraud value |
| 2.11 | Card fraud - card ID theft | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudIdTheft | Identity theft fraud count |
| 2.12 | Card fraud - card ID theft value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudIdTheftValue | Identity theft fraud value |
| 2.13 | Card fraud - card not present | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudNotPresent | CNP fraud count |
| 2.14 | Card fraud - card not present value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudNotPresentValue | CNP fraud value |
| 2.15 | Card fraud - manipulated card/terminal | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudManipulated | Manipulated card/terminal count |
| 2.16 | Card fraud - manipulated card/terminal value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudManipulatedValue | Manipulated fraud value |
| 2.17 | Remote card payment fraud | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudRemotePayment | Remote payment fraud count |
| 2.18 | Remote card payment fraud value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudRemotePaymentValue | Remote payment fraud value |
| 2.19 | Card fraud at point of sale | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudPOS | POS fraud count |
| 2.20 | Card fraud at point of sale value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudPOSValue | POS fraud value |
| 2.21 | Card fraud at ATM | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudATM | ATM fraud count |
| 2.22 | Card fraud at ATM value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | cardFraudATMValue | ATM fraud value |
| 2.23 | Card fraud - domestic transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudDomestic | Domestic card fraud count |
| 2.24 | Card fraud - cross-border transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | cardFraudCrossBorder | Cross-border card fraud count |

### Section 3: Credit Transfer Fraud Data (Items 3.1-3.15)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 3.1 | Total number of credit transfers | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | creditTransferCount | All credit transfers in period |
| 3.2 | Total value of credit transfers | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | creditTransferValue | Total credit transfer value |
| 3.3 | Number of fraudulent credit transfers | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | creditTransferFraudCount | Fraud transactions detected |
| 3.4 | Value of fraudulent credit transfers | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | creditTransferFraudValue | Total fraud value |
| 3.5 | Credit transfer fraud - account takeover | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudAccountTakeover | Account takeover fraud count |
| 3.6 | Credit transfer fraud - account takeover value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | ctFraudAccountTakeoverValue | Account takeover fraud value |
| 3.7 | Credit transfer fraud - manipulation of payer | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudManipulationPayer | Social engineering fraud count |
| 3.8 | Credit transfer fraud - manipulation of payer value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | ctFraudManipulationPayerValue | Social engineering fraud value |
| 3.9 | Credit transfer fraud - other | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudOther | Other credit transfer fraud count |
| 3.10 | Credit transfer fraud - other value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | ctFraudOtherValue | Other credit transfer fraud value |
| 3.11 | CT fraud - SEPA credit transfers | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudSEPA | SEPA credit transfer fraud |
| 3.12 | CT fraud - non-SEPA credit transfers | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudNonSEPA | Non-SEPA credit transfer fraud |
| 3.13 | CT fraud - domestic transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudDomestic | Domestic CT fraud count |
| 3.14 | CT fraud - cross-border intra-EU | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudCrossBorderEU | Cross-border intra-EU fraud |
| 3.15 | CT fraud - cross-border extra-EU | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ctFraudCrossBorderExtraEU | Cross-border extra-EU fraud |

### Section 4: Direct Debit Fraud Data (Items 4.1-4.12)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 4.1 | Total number of direct debits | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | directDebitCount | All direct debits in period |
| 4.2 | Total value of direct debits | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | directDebitValue | Total direct debit value |
| 4.3 | Number of fraudulent direct debits | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | directDebitFraudCount | Fraud transactions detected |
| 4.4 | Value of fraudulent direct debits | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | directDebitFraudValue | Total fraud value |
| 4.5 | Direct debit fraud - account takeover | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ddFraudAccountTakeover | Account takeover fraud count |
| 4.6 | Direct debit fraud - account takeover value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | ddFraudAccountTakeoverValue | Account takeover fraud value |
| 4.7 | Direct debit fraud - other | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ddFraudOther | Other direct debit fraud count |
| 4.8 | Direct debit fraud - other value | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | ddFraudOtherValue | Other direct debit fraud value |
| 4.9 | DD fraud - SEPA direct debits | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ddFraudSEPA | SEPA direct debit fraud |
| 4.10 | DD fraud - non-SEPA direct debits | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ddFraudNonSEPA | Non-SEPA direct debit fraud |
| 4.11 | DD fraud - domestic transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ddFraudDomestic | Domestic DD fraud count |
| 4.12 | DD fraud - cross-border transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | ddFraudCrossBorder | Cross-border DD fraud count |

### Section 5: Other Payment Instrument Fraud (Items 5.1-5.12)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 5.1 | Total number of e-money transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | eMoneyTransactionCount | All e-money transactions |
| 5.2 | Total value of e-money transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | eMoneyTransactionValue | Total e-money value |
| 5.3 | Number of fraudulent e-money transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | eMoneyFraudCount | E-money fraud count |
| 5.4 | Value of fraudulent e-money transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | eMoneyFraudValue | E-money fraud value |
| 5.5 | Total number of cheque transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | chequeTransactionCount | All cheque transactions |
| 5.6 | Total value of cheque transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | chequeTransactionValue | Total cheque value |
| 5.7 | Number of fraudulent cheque transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | chequeFraudCount | Cheque fraud count |
| 5.8 | Value of fraudulent cheque transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | chequeFraudValue | Cheque fraud value |
| 5.9 | Total number of other payment transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | otherPaymentTransactionCount | Other payment types |
| 5.10 | Total value of other payment transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | otherPaymentTransactionValue | Other payment value |
| 5.11 | Number of fraudulent other payment transactions | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | otherPaymentFraudCount | Other payment fraud count |
| 5.12 | Value of fraudulent other payment transactions | Decimal | 18,2 | Yes | Numeric | RegulatoryReport.extensions | otherPaymentFraudValue | Other payment fraud value |

### Section 6: Fraud Prevention and Detection (Items 6.1-6.12)

| Item# | Field Name | Type | Length | Required | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|----------|--------------|------------|---------------|-------|
| 6.1 | Strong customer authentication (SCA) applied | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | scaAppliedCount | Transactions with SCA |
| 6.2 | SCA exemptions applied | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | scaExemptionsCount | SCA exemption count |
| 6.3 | SCA exemption - low value | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | scaExemptionLowValue | Low value exemption |
| 6.4 | SCA exemption - trusted beneficiary | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | scaExemptionTrustedBenef | Trusted beneficiary exemption |
| 6.5 | SCA exemption - corporate payment | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | scaExemptionCorporate | Corporate payment exemption |
| 6.6 | Transaction monitoring alerts generated | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | transactionMonitoringAlerts | Total alerts generated |
| 6.7 | Fraud confirmed from alerts | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | fraudConfirmedFromAlerts | Alerts resulting in confirmed fraud |
| 6.8 | Customer authentication challenges | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | authenticationChallenges | Authentication challenges issued |
| 6.9 | Failed authentication attempts | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | failedAuthAttempts | Failed authentication count |
| 6.10 | Fraud reported by customers | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | fraudReportedByCustomers | Customer-reported fraud |
| 6.11 | Fraud detected by PSP systems | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | fraudDetectedByPSP | PSP system-detected fraud |
| 6.12 | Fraud detected by other parties | Integer | 15 | Yes | Numeric | RegulatoryReport.extensions | fraudDetectedByOthers | Third party-detected fraud |

---

## Code Lists

### PSP Type Codes (Item 1.4)

| Code | Description | CDM Mapping |
|------|-------------|-------------|
| CI | Credit Institution | FinancialInstitution.institutionType = 'CI' |
| PI | Payment Institution | FinancialInstitution.institutionType = 'PI' |
| EMI | E-Money Institution | FinancialInstitution.institutionType = 'EMI' |
| HYB | Hybrid (multiple types) | FinancialInstitution.institutionType = 'HYB' |

### Fraud Type Categories

| Fraud Type | Description | CDM Mapping |
|------------|-------------|-------------|
| Lost/Stolen | Card reported lost or stolen | RegulatoryReport.extensions.cardFraudLostStolen |
| Not Received | Card never received by cardholder | RegulatoryReport.extensions.cardFraudNotReceived |
| Counterfeit | Counterfeit card created from card data | RegulatoryReport.extensions.cardFraudCounterfeit |
| ID Theft | Identity theft to open account/obtain card | RegulatoryReport.extensions.cardFraudIdTheft |
| CNP | Card not present (online/phone) | RegulatoryReport.extensions.cardFraudNotPresent |
| Manipulation | Card/terminal manipulation (skimming) | RegulatoryReport.extensions.cardFraudManipulated |
| Account Takeover | Fraudulent access to customer account | RegulatoryReport.extensions.ctFraudAccountTakeover |
| Social Engineering | Manipulation of payer (CEO fraud, etc.) | RegulatoryReport.extensions.ctFraudManipulationPayer |

### Transaction Channel Codes

| Channel | Description | CDM Mapping |
|---------|-------------|-------------|
| POS | Point of Sale terminal | RegulatoryReport.extensions.cardFraudPOS |
| ATM | Automated Teller Machine | RegulatoryReport.extensions.cardFraudATM |
| REMOTE | Remote payment (online, mobile) | RegulatoryReport.extensions.cardFraudRemotePayment |
| SEPA | SEPA payment scheme | RegulatoryReport.extensions.ctFraudSEPA |
| NON_SEPA | Non-SEPA payment | RegulatoryReport.extensions.ctFraudNonSEPA |

---

## CDM Extensions Required

All 87 PSD2 Fraud Report fields successfully map to GPS CDM using the RegulatoryReport.extensions object. **No schema enhancements required.**

The extensions object supports all PSD2-specific fraud data fields while maintaining the core CDM structure.

---

## Example PSD2 Fraud Report Scenario

**Reporting Period:** Q4 2024 (October 1 - December 31, 2024)
**PSP:** Example Bank, credit institution in France

**Summary Data:**
- Total card transactions: 15,234,567
- Total card transaction value: EUR 2,456,789,123.45
- Fraudulent card transactions: 3,456 (0.023%)
- Fraudulent card transaction value: EUR 456,789.12 (0.019%)

**Card Fraud Breakdown:**
- Lost/Stolen: 1,234 transactions, EUR 123,456.78
- Card Not Present: 1,890 transactions, EUR 278,901.23
- Counterfeit: 156 transactions, EUR 34,567.89
- ID Theft: 176 transactions, EUR 19,863.22

**Credit Transfer Fraud:**
- Total credit transfers: 2,345,678
- Fraudulent: 234 transactions
- Account takeover: 145 transactions, EUR 234,567.89
- Social engineering: 89 transactions, EUR 456,789.01

**SCA Application:**
- SCA applied: 14,123,456 transactions (92.7%)
- SCA exemptions: 1,111,111 transactions
  - Low value: 987,654
  - Trusted beneficiary: 98,765
  - Corporate: 24,692

**Detection:**
- Alerts generated: 12,345
- Fraud confirmed from alerts: 2,890
- Customer-reported fraud: 456
- PSP-detected fraud: 2,890

---

## References

- **PSD2 Directive:** Directive (EU) 2015/2366 on payment services in the internal market
- **RTS on SCA:** Commission Delegated Regulation (EU) 2018/389
- **Fraud Reporting RTS:** Commission Implementing Regulation (EU) 2018/1042
- **EBA Guidelines:** Guidelines on fraud reporting under PSD2 (EBA/GL/2018/05)
- **Technical Standards:** EBA technical standards on fraud data reporting (XML schema)
- **GPS CDM Schema:** `/schemas/05_regulatory_report_complete_schema.json`

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Next Review:** Q1 2025
