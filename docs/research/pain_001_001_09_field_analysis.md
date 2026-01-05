# ISO 20022 pain.001.001.09 Field Analysis

## Summary

**Official Standard**: ISO 20022 CustomerCreditTransferInitiationV09 (pain.001.001.09)
**Total Unique Element Names in XSD**: ~134 (from XSD schema analysis)
**Total Field Paths in GPS CDM**: 213 (includes nested paths like Dbtr/PstlAdr/StrtNm)
  - Complex container types: 95
  - Leaf data fields: **118** (actual mappable fields)
**Previously Inserted (INCORRECT)**: 267 fields (many were duplicates or fabricated)

## Current Coverage Status (GPS CDM)

### Standard to Silver Coverage: 100%
- Standard leaf fields: 118
- Silver mappings linked: 118 (100% coverage)
- Silver table columns added: 39 new columns to stg_pain001

### Silver to Gold Coverage
- Total Gold mappings: 116
- Unique Silver columns mapped to Gold: 68
- Gold tables covered:
  | Table | Mappings |
  |-------|----------|
  | cdm_payment_instruction | 32 |
  | cdm_party | 28 (DEBTOR, CREDITOR, ULTIMATE_DEBTOR, ULTIMATE_CREDITOR, INITIATING_PARTY) |
  | cdm_payment_extension_iso20022 | 24 |
  | cdm_account | 16 (DEBTOR, CREDITOR) |
  | cdm_financial_institution | 16 (DEBTOR_AGENT, CREDITOR_AGENT) |

## Sources

- [ISO 20022 Message Archive](https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive?search=pain)
- [pain.001.001.09 XSD Schema (GitHub)](https://github.com/fortesp/xsd2xml/blob/master/tests/resources/pain.001.001.09.xsd)
- [LHV Bank Documentation](https://docs.lhv.com/home/connect/services/payments/pain.001.001.09-format)
- [XMLdation Blog - Version Differences](https://blog.xmldation.com/resources/differences-between-iso-20022-pain.001-message-versions-03-and-09)

## XSD Element Names (134 unique)

From analysis of the official XSD schema:

### Root and Container Elements
- Document
- CstmrCdtTrfInitn (CustomerCreditTransferInitiationV09)

### Group Header (GrpHdr)
- MsgId - Message identification
- CreDtTm - Creation date/time
- Authstn - Authorisation
- NbOfTxs - Number of transactions
- CtrlSum - Control sum
- InitgPty - Initiating party
- FwdgAgt - Forwarding agent

### Payment Information (PmtInf)
- PmtInfId - Payment information ID
- PmtMtd - Payment method
- BtchBookg - Batch booking
- NbOfTxs - Number of transactions
- CtrlSum - Control sum
- PmtTpInf - Payment type information
- ReqdExctnDt - Requested execution date
- PoolgAdjstmntDt - Pooling adjustment date
- Dbtr - Debtor
- DbtrAcct - Debtor account
- DbtrAgt - Debtor agent
- DbtrAgtAcct - Debtor agent account
- UltmtDbtr - Ultimate debtor
- ChrgBr - Charges bearer
- ChrgsAcct - Charges account
- ChrgsAcctAgt - Charges account agent
- CdtTrfTxInf - Credit transfer transaction info

### Credit Transfer Transaction (CdtTrfTxInf)
- PmtId - Payment identification
- PmtTpInf - Payment type information
- Amt - Amount
- XchgRateInf - Exchange rate information
- ChqInstr - Cheque instruction
- UltmtDbtr - Ultimate debtor
- IntrmyAgt1 - Intermediary agent 1
- IntrmyAgt1Acct - Intermediary agent 1 account
- IntrmyAgt2 - Intermediary agent 2
- IntrmyAgt2Acct - Intermediary agent 2 account
- IntrmyAgt3 - Intermediary agent 3
- IntrmyAgt3Acct - Intermediary agent 3 account
- CdtrAgt - Creditor agent
- CdtrAgtAcct - Creditor agent account
- Cdtr - Creditor
- CdtrAcct - Creditor account
- UltmtCdtr - Ultimate creditor
- InstrForCdtrAgt - Instruction for creditor agent
- InstrForDbtrAgt - Instruction for debtor agent
- Purp - Purpose
- RgltryRptg - Regulatory reporting
- Tax - Tax information
- RltdRmtInf - Related remittance information
- RmtInf - Remittance information
- SplmtryData - Supplementary data

### Payment Identification (PmtId)
- InstrId - Instruction ID
- EndToEndId - End-to-end ID
- UETR - Unique end-to-end transaction reference

### Common Reusable Elements
- Id - Identification
- Nm - Name
- PstlAdr - Postal address
- IBAN - International bank account number
- Othr - Other identification
- Cd - Code
- Prtry - Proprietary
- Tp - Type
- Ctry - Country
- LEI - Legal entity identifier
- BrnchId - Branch identification
- ClrSysId - Clearing system identification
- MmbId - Member identification

### Address Elements (PstlAdr)
- AdrTp - Address type
- Dept - Department
- SubDept - Sub-department
- StrtNm - Street name
- BldgNb - Building number
- BldgNm - Building name
- Flr - Floor
- PstBx - Post box
- Room - Room
- PstCd - Post code
- TwnNm - Town name
- TwnLctnNm - Town location name
- DstrctNm - District name
- CtrySubDvsn - Country sub-division
- Ctry - Country
- AdrLine - Address line

### Contact Details (CtctDtls)
- NmPrfx - Name prefix
- Nm - Name
- PhneNb - Phone number
- MobNb - Mobile number
- FaxNb - Fax number
- EmailAdr - Email address
- EmailPurp - Email purpose
- JobTitl - Job title
- Rspnsblty - Responsibility
- Dept - Department
- Othr - Other
- PrefrdMtd - Preferred method

### Amount Elements
- InstdAmt - Instructed amount
- EqvtAmt - Equivalent amount
- Amt - Amount
- Ccy - Currency

### Date Elements
- Dt - Date
- DtTm - Date time
- FrDt - From date
- ToDt - To date
- FrToDt - From to date period

### Tax Elements (Tax)
- Cdtr - Creditor (tax authority)
- Dbtr - Debtor
- UltmtDbtr - Ultimate debtor
- AdmstnZone - Administration zone
- RefNb - Reference number
- Mtd - Method
- TtlTaxblBaseAmt - Total taxable base amount
- TtlTaxAmt - Total tax amount
- Dt - Date
- SeqNb - Sequence number
- Rcrd - Record

### Remittance Information (RmtInf)
- Ustrd - Unstructured
- Strd - Structured
- RfrdDocInf - Referred document info
- RfrdDocAmt - Referred document amount
- CdtrRefInf - Creditor reference info
- Invcr - Invoicer
- Invcee - Invoicee
- TaxRmt - Tax remittance
- GrnshmtRmt - Garnishment remittance
- AddtlRmtInf - Additional remittance info

### Regulatory Reporting (RgltryRptg)
- DbtCdtRptgInd - Debit/credit reporting indicator
- Authrty - Authority
- Dtls - Details

### Cheque Instruction (ChqInstr)
- ChqTp - Cheque type
- ChqNb - Cheque number
- ChqFr - Cheque from
- DlvryMtd - Delivery method
- DlvrTo - Deliver to
- InstrPrty - Instruction priority
- ChqMtrtyDt - Cheque maturity date
- FrmsCd - Forms code
- MemoFld - Memo field
- RgnlClrZone - Regional clearing zone
- PrtLctn - Print location

### Other Elements
- Ref - Reference
- PlcAndNm - Place and name
- Envlp - Envelope
- Rate - Rate
- Prxy - Proxy
- Issr - Issuer
- CdOrPrtry - Code or proprietary
- Yr - Year
- Prd - Period
- DocLineId - Document line ID
- Desc - Description
- CdtDbtInd - Credit/debit indicator
- Rsn - Reason
- Nb - Number
- RltdDt - Related date
- AddtlInf - Additional information
- BirthDt - Birth date
- PrvcOfBirth - Province of birth
- CityOfBirth - City of birth
- CtryOfBirth - Country of birth
- TaxId - Tax identification
- RegnId - Registration ID
- TaxTp - Tax type
- Ctgy - Category
- CtgyDtls - Category details
- DbtrSts - Debtor status
- CertId - Certificate ID
- SeqNb - Sequence number
- ElctrncAdr - Electronic address
- RmtId - Remittance ID
- RmtLctnDtls - Remittance location details
- Mtd - Method
- Inf - Information
- Titl - Title

## Key Version 9 Changes from Version 3

1. **SupplementaryData field**: Allows banks/corporates to add custom information (xs:any)
2. **RequestedExecutionDate**: Now supports both ISODate and ISODateTime
3. **Structured Addresses**: More PstlAdr elements supported
4. **BICFI**: Replaces BIC for financial institution identification
5. **LEI**: Legal Entity Identifier added for global entity identification
6. **UETR**: Unique End-to-End Transaction Reference added

## Implications for GPS CDM

The standard_fields table should contain approximately **134 fields** for pain.001.001.09, not 267. The previous insertion was incorrect and needs to be corrected.

### Recommended Approach

1. Delete incorrect 267 fields from standard_fields
2. Insert accurate 134 fields based on XSD schema
3. Use XPath format matching the actual XML structure:
   - `CstmrCdtTrfInitn/GrpHdr/MsgId`
   - `CstmrCdtTrfInitn/PmtInf/Dbtr/Nm`
   - `CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt`

## Analysis Date
2026-01-05
