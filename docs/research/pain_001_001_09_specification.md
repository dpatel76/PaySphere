# ISO 20022 pain.001.001.09 - Customer Credit Transfer Initiation V09

## Overview

**Message ID**: pain.001.001.09
**Full Name**: CustomerCreditTransferInitiationV09
**Namespace**: `urn:iso:std:iso:20022:tech:xsd:pain.001.001.09`
**Purpose**: Sent by initiating party to request movement of funds from debtor account to creditor

## Message Structure

```
Document
└── CstmrCdtTrfInitn (CustomerCreditTransferInitiationV09) [1..1]
    ├── GrpHdr (GroupHeader85) [1..1]
    ├── PmtInf (PaymentInstruction30) [1..*]
    └── SplmtryData (SupplementaryData1) [0..*]
```

---

## 1. Group Header (GrpHdr) - GroupHeader85

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| MsgId | GrpHdr/MsgId | Max35Text | 1..1 | 35 | Unique message identifier |
| CreDtTm | GrpHdr/CreDtTm | ISODateTime | 1..1 | - | Creation date and time |
| Authstn | GrpHdr/Authstn | Authorisation1Choice | 0..2 | - | Authorization (Cd: AUTH/FDET/FSUM/ILEV or Prtry) |
| NbOfTxs | GrpHdr/NbOfTxs | Max15NumericText | 1..1 | 15 | Total number of transactions |
| CtrlSum | GrpHdr/CtrlSum | DecimalNumber | 0..1 | 18.17 | Control sum of all amounts |
| InitgPty | GrpHdr/InitgPty | PartyIdentification135 | 1..1 | - | Initiating party details |
| FwdgAgt | GrpHdr/FwdgAgt | BranchAndFinancialInstitutionIdentification6 | 0..1 | - | Forwarding agent |

### 1.1 Initiating Party (InitgPty) - PartyIdentification135

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| Nm | InitgPty/Nm | Max140Text | 0..1 | 140 | Party name |
| PstlAdr | InitgPty/PstlAdr | PostalAddress24 | 0..1 | - | Postal address |
| Id | InitgPty/Id | Party38Choice | 0..1 | - | Party identification (OrgId or PrvtId) |
| CtryOfRes | InitgPty/CtryOfRes | CountryCode | 0..1 | 2 | Country of residence |
| CtctDtls | InitgPty/CtctDtls | Contact4 | 0..1 | - | Contact details |

---

## 2. Payment Information (PmtInf) - PaymentInstruction30

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| PmtInfId | PmtInf/PmtInfId | Max35Text | 1..1 | 35 | Payment information identifier |
| PmtMtd | PmtInf/PmtMtd | PaymentMethod3Code | 1..1 | - | Payment method (CHK/TRF/TRA) |
| BtchBookg | PmtInf/BtchBookg | boolean | 0..1 | - | Batch booking indicator |
| NbOfTxs | PmtInf/NbOfTxs | Max15NumericText | 0..1 | 15 | Number of transactions |
| CtrlSum | PmtInf/CtrlSum | DecimalNumber | 0..1 | 18.17 | Control sum |
| PmtTpInf | PmtInf/PmtTpInf | PaymentTypeInformation26 | 0..1 | - | Payment type information |
| ReqdExctnDt | PmtInf/ReqdExctnDt | DateAndDateTime2Choice | 1..1 | - | Requested execution date (Dt or DtTm) |
| PoolgAdjstmntDt | PmtInf/PoolgAdjstmntDt | ISODate | 0..1 | - | Pooling adjustment date |
| Dbtr | PmtInf/Dbtr | PartyIdentification135 | 1..1 | - | Debtor details |
| DbtrAcct | PmtInf/DbtrAcct | CashAccount38 | 1..1 | - | Debtor account |
| DbtrAgt | PmtInf/DbtrAgt | BranchAndFinancialInstitutionIdentification6 | 1..1 | - | Debtor agent (bank) |
| DbtrAgtAcct | PmtInf/DbtrAgtAcct | CashAccount38 | 0..1 | - | Debtor agent account |
| InstrForDbtrAgt | PmtInf/InstrForDbtrAgt | Max140Text | 0..1 | 140 | Instructions for debtor agent |
| UltmtDbtr | PmtInf/UltmtDbtr | PartyIdentification135 | 0..1 | - | Ultimate debtor |
| ChrgBr | PmtInf/ChrgBr | ChargeBearerType1Code | 0..1 | - | Charge bearer (DEBT/CRED/SHAR/SLEV) |
| ChrgsAcct | PmtInf/ChrgsAcct | CashAccount38 | 0..1 | - | Charges account |
| ChrgsAcctAgt | PmtInf/ChrgsAcctAgt | BranchAndFinancialInstitutionIdentification6 | 0..1 | - | Charges account agent |
| CdtTrfTxInf | PmtInf/CdtTrfTxInf | CreditTransferTransaction34 | 1..* | - | Credit transfer transactions |

### 2.1 Payment Type Information (PmtTpInf) - PaymentTypeInformation26

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| InstrPrty | PmtTpInf/InstrPrty | Priority2Code | 0..1 | - | Instruction priority (HIGH/NORM) |
| SvcLvl | PmtTpInf/SvcLvl | ServiceLevel8Choice | 0..1 | - | Service level (Cd or Prtry) |
| LclInstrm | PmtTpInf/LclInstrm | LocalInstrument2Choice | 0..1 | - | Local instrument (Cd or Prtry) |
| CtgyPurp | PmtTpInf/CtgyPurp | CategoryPurpose1Choice | 0..1 | - | Category purpose (Cd or Prtry) |

### 2.2 Debtor (Dbtr) - PartyIdentification135

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| Nm | Dbtr/Nm | Max140Text | 0..1 | 140 | Debtor name |
| PstlAdr | Dbtr/PstlAdr | PostalAddress24 | 0..1 | - | Debtor postal address |
| Id | Dbtr/Id | Party38Choice | 0..1 | - | Debtor identification |
| CtryOfRes | Dbtr/CtryOfRes | CountryCode | 0..1 | 2 | Country of residence |
| CtctDtls | Dbtr/CtctDtls | Contact4 | 0..1 | - | Contact details |

### 2.3 Debtor Account (DbtrAcct) - CashAccount38

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| Id | DbtrAcct/Id | AccountIdentification4Choice | 1..1 | - | Account ID (IBAN or Othr) |
| Tp | DbtrAcct/Tp | CashAccountType2Choice | 0..1 | - | Account type |
| Ccy | DbtrAcct/Ccy | ActiveOrHistoricCurrencyCode | 0..1 | 3 | Currency |
| Nm | DbtrAcct/Nm | Max70Text | 0..1 | 70 | Account name |
| Prxy | DbtrAcct/Prxy | ProxyAccountIdentification1 | 0..1 | - | Proxy account ID |

### 2.4 Debtor Agent (DbtrAgt) - BranchAndFinancialInstitutionIdentification6

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| FinInstnId | DbtrAgt/FinInstnId | FinancialInstitutionIdentification18 | 1..1 | - | Financial institution ID |
| BrnchId | DbtrAgt/BrnchId | BranchData3 | 0..1 | - | Branch identification |

#### Financial Institution ID (FinInstnId) - FinancialInstitutionIdentification18

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| BICFI | FinInstnId/BICFI | BICFIDec2014Identifier | 0..1 | 11 | BIC code |
| ClrSysMmbId | FinInstnId/ClrSysMmbId | ClearingSystemMemberIdentification2 | 0..1 | - | Clearing system member ID |
| LEI | FinInstnId/LEI | LEIIdentifier | 0..1 | 20 | Legal Entity Identifier |
| Nm | FinInstnId/Nm | Max140Text | 0..1 | 140 | Institution name |
| PstlAdr | FinInstnId/PstlAdr | PostalAddress24 | 0..1 | - | Postal address |
| Othr | FinInstnId/Othr | GenericFinancialIdentification1 | 0..1 | - | Other identification |

---

## 3. Credit Transfer Transaction (CdtTrfTxInf) - CreditTransferTransaction34

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| PmtId | CdtTrfTxInf/PmtId | PaymentIdentification6 | 1..1 | - | Payment identification |
| PmtTpInf | CdtTrfTxInf/PmtTpInf | PaymentTypeInformation26 | 0..1 | - | Payment type information |
| Amt | CdtTrfTxInf/Amt | AmountType4Choice | 1..1 | - | Amount (InstdAmt or EqvtAmt) |
| XchgRateInf | CdtTrfTxInf/XchgRateInf | ExchangeRate1 | 0..1 | - | Exchange rate information |
| ChrgBr | CdtTrfTxInf/ChrgBr | ChargeBearerType1Code | 0..1 | - | Charge bearer |
| ChqInstr | CdtTrfTxInf/ChqInstr | Cheque11 | 0..1 | - | Cheque instruction |
| UltmtDbtr | CdtTrfTxInf/UltmtDbtr | PartyIdentification135 | 0..1 | - | Ultimate debtor |
| IntrmyAgt1 | CdtTrfTxInf/IntrmyAgt1 | BranchAndFinancialInstitutionIdentification6 | 0..1 | - | Intermediary agent 1 |
| IntrmyAgt1Acct | CdtTrfTxInf/IntrmyAgt1Acct | CashAccount38 | 0..1 | - | Intermediary agent 1 account |
| IntrmyAgt2 | CdtTrfTxInf/IntrmyAgt2 | BranchAndFinancialInstitutionIdentification6 | 0..1 | - | Intermediary agent 2 |
| IntrmyAgt2Acct | CdtTrfTxInf/IntrmyAgt2Acct | CashAccount38 | 0..1 | - | Intermediary agent 2 account |
| IntrmyAgt3 | CdtTrfTxInf/IntrmyAgt3 | BranchAndFinancialInstitutionIdentification6 | 0..1 | - | Intermediary agent 3 |
| IntrmyAgt3Acct | CdtTrfTxInf/IntrmyAgt3Acct | CashAccount38 | 0..1 | - | Intermediary agent 3 account |
| CdtrAgt | CdtTrfTxInf/CdtrAgt | BranchAndFinancialInstitutionIdentification6 | 0..1 | - | Creditor agent |
| CdtrAgtAcct | CdtTrfTxInf/CdtrAgtAcct | CashAccount38 | 0..1 | - | Creditor agent account |
| Cdtr | CdtTrfTxInf/Cdtr | PartyIdentification135 | 0..1 | - | Creditor |
| CdtrAcct | CdtTrfTxInf/CdtrAcct | CashAccount38 | 0..1 | - | Creditor account |
| UltmtCdtr | CdtTrfTxInf/UltmtCdtr | PartyIdentification135 | 0..1 | - | Ultimate creditor |
| InstrForCdtrAgt | CdtTrfTxInf/InstrForCdtrAgt | InstructionForCreditorAgent1 | 0..* | - | Instructions for creditor agent |
| InstrForDbtrAgt | CdtTrfTxInf/InstrForDbtrAgt | Max140Text | 0..1 | 140 | Instructions for debtor agent |
| Purp | CdtTrfTxInf/Purp | Purpose2Choice | 0..1 | - | Purpose (Cd or Prtry) |
| RgltryRptg | CdtTrfTxInf/RgltryRptg | RegulatoryReporting3 | 0..10 | - | Regulatory reporting |
| Tax | CdtTrfTxInf/Tax | TaxInformation8 | 0..1 | - | Tax information |
| RltdRmtInf | CdtTrfTxInf/RltdRmtInf | RemittanceLocation7 | 0..10 | - | Related remittance information |
| RmtInf | CdtTrfTxInf/RmtInf | RemittanceInformation16 | 0..1 | - | Remittance information |
| SplmtryData | CdtTrfTxInf/SplmtryData | SupplementaryData1 | 0..* | - | Supplementary data |

### 3.1 Payment Identification (PmtId) - PaymentIdentification6

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| InstrId | PmtId/InstrId | Max35Text | 0..1 | 35 | Instruction identification |
| EndToEndId | PmtId/EndToEndId | Max35Text | 1..1 | 35 | End-to-end identification |
| UETR | PmtId/UETR | UUIDv4Identifier | 0..1 | 36 | Unique end-to-end transaction reference |

### 3.2 Amount (Amt) - AmountType4Choice

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| InstdAmt | Amt/InstdAmt | ActiveOrHistoricCurrencyAndAmount | 0..1 | - | Instructed amount with @Ccy |
| EqvtAmt | Amt/EqvtAmt | EquivalentAmount2 | 0..1 | - | Equivalent amount |

### 3.3 Creditor (Cdtr) - PartyIdentification135

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| Nm | Cdtr/Nm | Max140Text | 0..1 | 140 | Creditor name |
| PstlAdr | Cdtr/PstlAdr | PostalAddress24 | 0..1 | - | Creditor postal address |
| Id | Cdtr/Id | Party38Choice | 0..1 | - | Creditor identification |
| CtryOfRes | Cdtr/CtryOfRes | CountryCode | 0..1 | 2 | Country of residence |
| CtctDtls | Cdtr/CtctDtls | Contact4 | 0..1 | - | Contact details |

### 3.4 Creditor Account (CdtrAcct) - CashAccount38

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| Id | CdtrAcct/Id | AccountIdentification4Choice | 1..1 | - | Account ID (IBAN or Othr) |
| Tp | CdtrAcct/Tp | CashAccountType2Choice | 0..1 | - | Account type |
| Ccy | CdtrAcct/Ccy | ActiveOrHistoricCurrencyCode | 0..1 | 3 | Currency |
| Nm | CdtrAcct/Nm | Max70Text | 0..1 | 70 | Account name |
| Prxy | CdtrAcct/Prxy | ProxyAccountIdentification1 | 0..1 | - | Proxy account ID |

### 3.5 Remittance Information (RmtInf) - RemittanceInformation16

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| Ustrd | RmtInf/Ustrd | Max140Text | 0..* | 140 | Unstructured remittance info |
| Strd | RmtInf/Strd | StructuredRemittanceInformation16 | 0..* | - | Structured remittance info |

---

## 4. Postal Address (PstlAdr) - PostalAddress24

| Element | XPath | Type | Occurs | MaxLen | Description |
|---------|-------|------|--------|--------|-------------|
| AdrTp | PstlAdr/AdrTp | AddressType3Choice | 0..1 | - | Address type |
| Dept | PstlAdr/Dept | Max70Text | 0..1 | 70 | Department |
| SubDept | PstlAdr/SubDept | Max70Text | 0..1 | 70 | Sub-department |
| StrtNm | PstlAdr/StrtNm | Max70Text | 0..1 | 70 | Street name |
| BldgNb | PstlAdr/BldgNb | Max16Text | 0..1 | 16 | Building number |
| BldgNm | PstlAdr/BldgNm | Max35Text | 0..1 | 35 | Building name |
| Flr | PstlAdr/Flr | Max70Text | 0..1 | 70 | Floor |
| PstBx | PstlAdr/PstBx | Max16Text | 0..1 | 16 | Post box |
| Room | PstlAdr/Room | Max70Text | 0..1 | 70 | Room |
| PstCd | PstlAdr/PstCd | Max16Text | 0..1 | 16 | Post code |
| TwnNm | PstlAdr/TwnNm | Max35Text | 0..1 | 35 | Town name |
| TwnLctnNm | PstlAdr/TwnLctnNm | Max35Text | 0..1 | 35 | Town location name |
| DstrctNm | PstlAdr/DstrctNm | Max35Text | 0..1 | 35 | District name |
| CtrySubDvsn | PstlAdr/CtrySubDvsn | Max35Text | 0..1 | 35 | Country subdivision |
| Ctry | PstlAdr/Ctry | CountryCode | 0..1 | 2 | Country code |
| AdrLine | PstlAdr/AdrLine | Max70Text | 0..7 | 70 | Address line (up to 7) |

---

## 5. Key Enumerations

### PaymentMethod3Code
| Code | Description |
|------|-------------|
| CHK | Cheque |
| TRF | Credit Transfer |
| TRA | Transfer Advice |

### ChargeBearerType1Code
| Code | Description |
|------|-------------|
| DEBT | Borne by debtor |
| CRED | Borne by creditor |
| SHAR | Shared |
| SLEV | Service level |

### Priority2Code
| Code | Description |
|------|-------------|
| HIGH | High priority |
| NORM | Normal priority |

### AddressType2Code
| Code | Description |
|------|-------------|
| ADDR | Postal address |
| PBOX | PO Box |
| HOME | Residential |
| BIZZ | Business |
| MLTO | Mail to |
| DLVY | Delivery to |

---

## 6. Data Type Patterns

| Type | Pattern/Format | Example |
|------|----------------|---------|
| IBAN2007Identifier | `[A-Z]{2}[0-9]{2}[a-zA-Z0-9]{1,30}` | DE89370400440532013000 |
| BICFIDec2014Identifier | `[A-Z0-9]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?` | DEUTDEFF |
| LEIIdentifier | `[A-Z0-9]{18}[0-9]{2}` | 549300HXDIVT86CAX538 |
| UUIDv4Identifier | UUID v4 format | eb6305c8-5bb1-4f74-b1f5-00000000001 |
| ISODateTime | `YYYY-MM-DDTHH:MM:SS` | 2024-01-15T10:30:00 |
| ISODate | `YYYY-MM-DD` | 2024-01-15 |
| CountryCode | `[A-Z]{2}` | US, DE, GB |
| CurrencyCode | `[A-Z]{3}` | USD, EUR, GBP |
| DecimalNumber | 18 digits, 17 fractions | 12345.67 |

---

## Sources

- [ISO 20022 Messages Archive](https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pain)
- [GitHub: pain.001.001.09 XSD](https://github.com/fortesp/xsd2xml/blob/master/tests/resources/pain.001.001.09.xsd)
- [LHV Connect Documentation](https://docs.lhv.com/home/connect/services/payments/pain.001.001.09-format)
- [Nordea Message Implementation Guide](https://www.nordea.com/en/doc/nordea-message-implementation-guide-pain-001-001-09-payments-v-1-1.pdf)
