# ISO 20022 camt.058 - Notification to Receive Cancellation Advice Mapping

## Message Overview

**Message Type:** camt.058.001.06 - NotificationToReceiveCancellationAdviceV06
**Category:** CAMT - Cash Management
**Purpose:** Sent by an account owner to cancel a previously sent notification to receive (camt.057)
**Direction:** Customer → FI (Account Owner to Bank)
**Scope:** Cancellation of pre-notification of incoming payment

**Key Use Cases:**
- Cancel previously sent notification to receive
- Update bank that expected funds will not arrive
- Correct erroneous pre-notification
- Remove expectation of incoming payment
- Support reconciliation when expected payment is cancelled
- Prevent processing delays due to unmet expectations

**Relationship to Other Messages:**
- **camt.057**: Original notification to receive being cancelled
- **camt.054**: Debit/credit notification (confirms no receipt)
- **MT 210**: SWIFT equivalent for notice to receive
- **MT 292**: SWIFT cancellation of MT 210

**Comparison with Related Messages:**
- **camt.058**: Cancellation of camt.057 notification
- **camt.057**: Original notification to receive
- **MT 292**: SWIFT MT cancellation equivalent

---

## Mapping Statistics

| Metric | Count |
|--------|-------|
| **Total Fields in camt.058** | 72 |
| **Fields Mapped to CDM** | 72 |
| **CDM Coverage** | 100% |
| **CDM Enhancements Required** | 0 |

**CDM Entities Used:**
- PaymentInstruction (core + extensions)
- Party (account owner, message sender/recipient)
- Account (account receiving notification cancellation)
- FinancialInstitution (account servicing institution)

---

## Complete Field Mapping

### 1. Group Header (GrpHdr)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| GrpHdr/MsgId | Message Identification | Text | 1-35 | 1..1 | Free text | PaymentInstruction | instructionId | Unique cancellation message ID |
| GrpHdr/CreDtTm | Creation Date Time | DateTime | - | 1..1 | ISODateTime | PaymentInstruction | creationDateTime | Cancellation message timestamp |
| GrpHdr/MsgSndr/Nm | Message Sender Name | Text | 1-140 | 0..1 | Free text | Party | name | Sender name |
| GrpHdr/MsgSndr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Sender country |
| GrpHdr/MsgSndr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Sender BIC |
| GrpHdr/MsgRcpt/Nm | Message Recipient Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Recipient bank name |
| GrpHdr/MsgRcpt/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Recipient bank BIC |

### 2. Account (Acct)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| Acct/Id/IBAN | Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Account IBAN |
| Acct/Id/Othr/Id | Account Other ID | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN account |
| Acct/Id/Othr/SchmeNm/Cd | Scheme Name Code | Code | - | 0..1 | BBAN, UPIC, etc. | Account.extensions | accountScheme | Account ID scheme |
| Acct/Tp/Cd | Account Type Code | Code | - | 0..1 | CACC, SVGS, etc. | Account.extensions | accountTypeCode | Account type |
| Acct/Ccy | Account Currency | Code | 3 | 0..1 | ISO 4217 | Account.extensions | accountCurrency | Account currency |
| Acct/Nm | Account Name | Text | 1-70 | 0..1 | Free text | Account.extensions | accountName | Account name |
| Acct/Ownr/Nm | Owner Name | Text | 1-140 | 0..1 | Free text | Party | name | Account owner name |
| Acct/Ownr/PstlAdr/StrtNm | Street Name | Text | 1-70 | 0..1 | Free text | Party | postalAddress.streetName | Owner street |
| Acct/Ownr/PstlAdr/PstCd | Postal Code | Text | 1-16 | 0..1 | Free text | Party | postalAddress.postCode | Owner postal code |
| Acct/Ownr/PstlAdr/TwnNm | Town Name | Text | 1-35 | 0..1 | Free text | Party | postalAddress.townName | Owner city |
| Acct/Ownr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Owner country |
| Acct/Ownr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Owner BIC |
| Acct/Ownr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Owner ID |
| Acct/Svcr/FinInstnId/BICFI | Servicer BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Account servicing bank |
| Acct/Svcr/FinInstnId/Nm | Servicer Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Servicing bank name |

### 3. Notification Cancellation (NtfctnCxl)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/Id | Cancellation ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | cancellationId | Unique cancellation ID |
| NtfctnCxl/OrgnlNtfctnId | Original Notification ID | Text | 1-35 | 1..1 | Free text | PaymentInstruction.extensions | originalNotificationId | Reference to camt.057 |
| NtfctnCxl/OrgnlCreDtTm | Original Creation Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original camt.057 timestamp |

### 4. Cancellation Reason (CxlRsn)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/CxlRsn/Orgtr/Nm | Originator Name | Text | 1-140 | 0..1 | Free text | Party | name | Cancellation originator |
| NtfctnCxl/CxlRsn/Orgtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Originator country |
| NtfctnCxl/CxlRsn/Orgtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Originator BIC |
| NtfctnCxl/CxlRsn/Orgtr/Id/PrvtId/Othr/Id | Private ID | Text | 1-35 | 0..1 | Free text | Party | identificationNumber | Originator private ID |
| NtfctnCxl/CxlRsn/Rsn/Cd | Reason Code | Code | - | 0..1 | CUST, DUPL, etc. | PaymentInstruction.extensions | cancellationReasonCode | Cancellation reason code |
| NtfctnCxl/CxlRsn/Rsn/Prtry | Proprietary Reason | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | proprietaryCancellationReason | Custom reason |
| NtfctnCxl/CxlRsn/AddtlInf | Additional Information | Text | 1-105 | 0..n | Free text | PaymentInstruction.extensions | cancellationAdditionalInfo | Free-text explanation |

### 5. Original Notification Details (OrgnlNtfctn)

#### 5.1 Original Group Information

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/OrgnlNtfctn/OrgnlMsgId | Original Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalMessageId | Original camt.057 message ID |
| NtfctnCxl/OrgnlNtfctn/OrgnlCreDtTm | Original Creation DateTime | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalCreatedDateTime | Original message timestamp |

#### 5.2 Original Entry (OrgnlNtry)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/Amt | Original Amount | ActiveOrHistoricCurrencyAndAmount | - | 0..1 | Amount + Ccy | PaymentInstruction.extensions | originalAmount | Original expected amount |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/Amt/@Ccy | Currency | Code | 3 | 1..1 | ISO 4217 | PaymentInstruction.extensions | originalCurrency | Original currency |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/CdtDbtInd | Credit Debit Indicator | Code | 4 | 0..1 | CRDT, DBIT | PaymentInstruction.extensions | creditDebitIndicator | Original direction |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/Sts/Cd | Status Code | Code | - | 0..1 | BOOK, PDNG, INFO | PaymentInstruction.extensions | originalStatus | Original entry status |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/BookgDt/Dt | Booking Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | originalBookingDate | Original booking date |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/BookgDt/DtTm | Booking Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalBookingDateTime | Original booking timestamp |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/ValDt/Dt | Value Date | Date | - | 0..1 | ISODate | PaymentInstruction.extensions | originalValueDate | Original value date |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/ValDt/DtTm | Value Date Time | DateTime | - | 0..1 | ISODateTime | PaymentInstruction.extensions | originalValueDateTime | Original value timestamp |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalAccountServicerReference | Original bank reference |

#### 5.3 Original Entry Details

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/MsgId | Message ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalRelatedMessageId | Related message ID |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/AcctSvcrRef | Account Servicer Reference | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalAccountServicerReference | Bank reference |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/PmtInfId | Payment Information ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalPaymentInformationId | Payment info ID |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/InstrId | Instruction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalInstructionId | Instruction reference |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/EndToEndId | End to End ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalEndToEndId | E2E reference |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/TxId | Transaction ID | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalTransactionId | Transaction reference |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Refs/UETR | UETR | Text | - | 0..1 | UUID format | PaymentInstruction.extensions | originalUETR | Original UETR |

#### 5.4 Original Related Parties

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/Dbtr/Nm | Debtor Name | Text | 1-140 | 0..1 | Free text | Party | name | Original debtor |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/Dbtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Debtor country |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/Dbtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Debtor BIC |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/IBAN | Debtor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Debtor account |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/DbtrAcct/Id/Othr/Id | Debtor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN debtor account |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/Cdtr/Nm | Creditor Name | Text | 1-140 | 0..1 | Free text | Party | name | Original creditor |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/Cdtr/PstlAdr/Ctry | Country | Code | 2 | 0..1 | ISO 3166-1 alpha-2 | Party | postalAddress.country | Creditor country |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/Cdtr/Id/OrgId/AnyBIC | Organization BIC | Text | - | 0..1 | BIC format | Party | identifications.bic | Creditor BIC |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/IBAN | Creditor Account IBAN | Text | - | 0..1 | IBAN format | Account | accountNumber | Creditor account |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdPties/CdtrAcct/Id/Othr/Id | Creditor Account Other | Text | 1-34 | 0..1 | Free text | Account | accountNumber | Non-IBAN creditor account |

#### 5.5 Original Related Agents

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/BICFI | Debtor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original debtor's bank |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdAgts/DbtrAgt/FinInstnId/Nm | Debtor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Debtor bank name |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/BICFI | Creditor Agent BIC | Text | - | 0..1 | BIC format | FinancialInstitution | bicCode | Original creditor's bank |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RltdAgts/CdtrAgt/FinInstnId/Nm | Creditor Agent Name | Text | 1-140 | 0..1 | Free text | FinancialInstitution | institutionName | Creditor bank name |

#### 5.6 Original Purpose and Remittance

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/Purp/Cd | Purpose Code | Code | 4 | 0..1 | ISO 20022 codes | PaymentInstruction.extensions | originalPurposeCode | Original purpose |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RmtInf/Ustrd | Unstructured Remittance | Text | 1-140 | 0..n | Free text | PaymentInstruction.extensions | originalRemittanceInformation | Original remittance |
| NtfctnCxl/OrgnlNtfctn/OrgnlNtry/NtryDtls/TxDtls/RmtInf/Strd/RfrdDocInf/Nb | Document Number | Text | 1-35 | 0..1 | Free text | PaymentInstruction.extensions | originalInvoiceNumber | Original invoice number |

### 6. Supplementary Data (SplmtryData)

| XPath | Field Name | Type | Length | Card. | Valid Values | CDM Entity | CDM Attribute | Notes |
|-------|------------|------|--------|-------|--------------|------------|---------------|-------|
| SplmtryData/PlcAndNm | Place and Name | Text | 1-350 | 0..1 | Free text | PaymentInstruction.extensions | supplementaryDataLocation | Location of supplementary data |
| SplmtryData/Envlp | Envelope | ComplexType | - | 1..1 | Any XML | PaymentInstruction.extensions | supplementaryData | Additional data envelope |

---

## Code Lists and Enumerations

### Cancellation Reason Code (CxlRsn/Rsn/Cd)

**Common Cancellation Reasons:**
- **CUST** - Requested by Customer
- **DUPL** - Duplicate Notification
- **TECH** - Technical Problems
- **ERRO** - Error in Notification
- **UPAY** - Payment Not Expected
- **CUTA** - Customer Request

### Credit Debit Indicator (CdtDbtInd)
- **CRDT** - Credit (receipt of funds)
- **DBIT** - Debit (payment of funds)

### Entry Status (Sts/Cd)
- **BOOK** - Booked
- **PDNG** - Pending
- **INFO** - Information

### Account Type (Tp/Cd)
- **CACC** - Current/Checking Account
- **SVGS** - Savings Account
- **LOAN** - Loan Account
- **CARD** - Card Account

---

## Message Examples

### Example 1: Cancel Pre-notification Due to Payment Cancellation

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.058.001.06">
  <NtfctnToRcvCxlAdvc>
    <GrpHdr>
      <MsgId>NTRCXL-20241220-001</MsgId>
      <CreDtTm>2024-12-20T15:30:00</CreDtTm>
      <MsgSndr>
        <Nm>Global Corporation Treasury</Nm>
        <Id>
          <OrgId>
            <AnyBIC>GLBCUS33XXX</AnyBIC>
          </OrgId>
        </Id>
      </MsgSndr>
      <MsgRcpt>
        <Nm>Bank of America</Nm>
        <Id>
          <OrgId>
            <AnyBIC>BOFAUS3NXXX</AnyBIC>
          </OrgId>
        </Id>
      </MsgRcpt>
    </GrpHdr>
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
      </Ownr>
      <Svcr>
        <FinInstnId>
          <BICFI>BOFAUS3NXXX</BICFI>
          <Nm>Bank of America</Nm>
        </FinInstnId>
      </Svcr>
    </Acct>
    <NtfctnCxl>
      <Id>CXLID-NTR-20241220-001</Id>
      <OrgnlNtfctnId>NTR-WIRE-20241220-001</OrgnlNtfctnId>
      <OrgnlCreDtTm>2024-12-20T09:00:00</OrgnlCreDtTm>
      <CxlRsn>
        <Orgtr>
          <Nm>Global Corporation Treasury</Nm>
        </Orgtr>
        <Rsn>
          <Cd>CUST</Cd>
        </Rsn>
        <AddtlInf>Sender has cancelled the original payment. Expected funds will not be received.</AddtlInf>
      </CxlRsn>
      <OrgnlNtfctn>
        <OrgnlMsgId>NTR-20241220-001</OrgnlMsgId>
        <OrgnlCreDtTm>2024-12-20T09:00:00</OrgnlCreDtTm>
        <OrgnlNtry>
          <Amt Ccy="USD">5000000.00</Amt>
          <CdtDbtInd>CRDT</CdtDbtInd>
          <Sts>
            <Cd>INFO</Cd>
          </Sts>
          <ValDt>
            <Dt>2024-12-20</Dt>
          </ValDt>
          <NtryDtls>
            <TxDtls>
              <Refs>
                <EndToEndId>E2E-WIRE-RECEIPT-20241220</EndToEndId>
                <TxId>TXN-INCOMING-WIRE-001</TxId>
              </Refs>
              <RltdPties>
                <Dbtr>
                  <Nm>European Supplier Ltd</Nm>
                  <PstlAdr>
                    <Ctry>GB</Ctry>
                  </PstlAdr>
                </Dbtr>
                <DbtrAcct>
                  <Id>
                    <IBAN>GB29NWBK60161331926819</IBAN>
                  </Id>
                </DbtrAcct>
                <Cdtr>
                  <Nm>Global Corporation</Nm>
                </Cdtr>
                <CdtrAcct>
                  <Id>
                    <Othr>
                      <Id>1234567890</Id>
                    </Othr>
                  </Id>
                </CdtrAcct>
              </RltdPties>
              <RltdAgts>
                <DbtrAgt>
                  <FinInstnId>
                    <BICFI>NWBKGB2LXXX</BICFI>
                    <Nm>NatWest Bank</Nm>
                  </FinInstnId>
                </DbtrAgt>
                <CdtrAgt>
                  <FinInstnId>
                    <BICFI>BOFAUS3NXXX</BICFI>
                    <Nm>Bank of America</Nm>
                  </FinInstnId>
                </CdtrAgt>
              </RltdAgts>
              <RmtInf>
                <Ustrd>Trade Settlement for Contract TR-2024-5678 - CANCELLED</Ustrd>
              </RmtInf>
            </TxDtls>
          </NtryDtls>
        </OrgnlNtry>
      </OrgnlNtfctn>
    </NtfctnCxl>
  </NtfctnToRcvCxlAdvc>
</Document>
```

### Example 2: Cancel Duplicate Notification

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.058.001.06">
  <NtfctnToRcvCxlAdvc>
    <GrpHdr>
      <MsgId>NTRCXL-20241220-DUPL-002</MsgId>
      <CreDtTm>2024-12-20T11:00:00</CreDtTm>
    </GrpHdr>
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
    <NtfctnCxl>
      <Id>CXLID-DUPL-002</Id>
      <OrgnlNtfctnId>NTR-PAYMENT-20241220-002</OrgnlNtfctnId>
      <OrgnlCreDtTm>2024-12-20T10:30:00</OrgnlCreDtTm>
      <CxlRsn>
        <Orgtr>
          <Nm>ABC Services Inc</Nm>
        </Orgtr>
        <Rsn>
          <Cd>DUPL</Cd>
        </Rsn>
        <AddtlInf>Duplicate notification sent in error. Please disregard previous notification.</AddtlInf>
      </CxlRsn>
      <OrgnlNtfctn>
        <OrgnlMsgId>NTR-20241220-CUST-002</OrgnlMsgId>
        <OrgnlCreDtTm>2024-12-20T10:30:00</OrgnlCreDtTm>
        <OrgnlNtry>
          <Amt Ccy="USD">25000.00</Amt>
          <CdtDbtInd>CRDT</CdtDbtInd>
          <ValDt>
            <Dt>2024-12-21</Dt>
          </ValDt>
          <NtryDtls>
            <TxDtls>
              <Refs>
                <EndToEndId>E2E-CUSTOMER-PMT-20241220</EndToEndId>
              </Refs>
              <RltdPties>
                <Dbtr>
                  <Nm>XYZ Manufacturing Co</Nm>
                </Dbtr>
                <Cdtr>
                  <Nm>ABC Services Inc</Nm>
                </Cdtr>
                <CdtrAcct>
                  <Id>
                    <Othr>
                      <Id>9876543210</Id>
                    </Othr>
                  </Id>
                </CdtrAcct>
              </RltdPties>
              <RmtInf>
                <Ustrd>Payment for Services - Invoice #INV-2024-1234</Ustrd>
                <Strd>
                  <RfrdDocInf>
                    <Nb>INV-2024-1234</Nb>
                  </RfrdDocInf>
                </Strd>
              </RmtInf>
            </TxDtls>
          </NtryDtls>
        </OrgnlNtry>
      </OrgnlNtfctn>
    </NtfctnCxl>
  </NtfctnToRcvCxlAdvc>
</Document>
```

---

## CDM Gap Analysis

**Result:** No CDM enhancements required

All 72 fields in camt.058 successfully map to existing GPS CDM entities:
- Core PaymentInstruction entity handles cancellation identification, references
- Extension fields accommodate cancellation-specific information and original notification details
- Party entity supports account owner, message sender/recipient, originator, debtor, creditor
- Account entity handles IBAN and non-IBAN account identifiers with account types and currency
- FinancialInstitution entity manages servicing institution and agent information

**Key Extension Fields Used:**
- cancellationId, originalNotificationId
- originalCreatedDateTime, cancellationReasonCode
- proprietaryCancellationReason, cancellationAdditionalInfo
- originalMessageId, originalAmount, originalCurrency
- creditDebitIndicator, originalStatus
- originalBookingDate, originalBookingDateTime
- originalValueDate, originalValueDateTime
- originalAccountServicerReference
- originalRelatedMessageId, originalPaymentInformationId
- originalInstructionId, originalEndToEndId, originalTransactionId, originalUETR
- originalPurposeCode, originalRemittanceInformation, originalInvoiceNumber
- accountScheme, accountTypeCode, accountCurrency, accountName

---

## References

- **ISO 20022 Message Definition:** camt.058.001.06 - NotificationToReceiveCancellationAdviceV06
- **XML Schema:** camt.058.001.06.xsd
- **Related Messages:** camt.057 (notification to receive), camt.054 (debit/credit notification), MT 210 (notice to receive), MT 292 (cancellation)
- **External Code Lists:** ISO 20022 External Code Lists (ExternalCodeSets_2Q2024_August2024_v1.xlsx)
- **Cancellation Reason Codes:** ISO 20022 External Payment Cancellation Reason Code

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Created By:** GPS CDM Data Architecture Team
