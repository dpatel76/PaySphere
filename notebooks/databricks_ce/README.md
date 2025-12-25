# GPS CDM - Databricks Community Edition Notebooks

This directory contains Databricks notebooks for running the GPS CDM pipeline on Databricks Community Edition (free tier).

## Quick Start

1. **Create a Databricks CE Account**
   - Go to https://community.cloud.databricks.com
   - Sign up for a free account

2. **Import Notebooks**
   - In Databricks workspace, click "Workspace" > "Import"
   - Upload the `.py` files from this directory

3. **Run Setup**
   - Execute `01_setup_gps_cdm` to create database and tables
   - This only needs to run once

4. **Upload Sample Data**
   - Upload ISO 20022 XML files to `/cdm/raw_input/` in DBFS
   - Use the Databricks UI: Data > DBFS > Upload

5. **Process Data**
   - Run `02_ingest_payment_messages` to process XML files
   - View results with `03_explore_cdm_data`

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_setup_gps_cdm.py` | Initialize database, create tables |
| `02_ingest_payment_messages.py` | Process XML through bronze/silver/gold |
| `03_explore_cdm_data.py` | Query and explore CDM data |

## Supported Message Types

- pain.001 - Customer Credit Transfer Initiation
- pain.002 - Payment Status Report
- camt.053 - Bank to Customer Statement
- camt.054 - Bank to Customer Debit Credit Notification
- pacs.008 - FI to FI Customer Credit Transfer

## Directory Structure in DBFS

```
/cdm/
  raw_input/       # Upload XML files here
  bronze/          # Raw message storage
  silver/          # Standardized data
  gold/            # CDM entities
  observability/   # Lineage and tracking
```

## Database Schema

Database: `cdm_dev`

### Bronze Layer
- `bronze_raw_payment` - Raw XML messages

### Silver Layer
- `silver_stg_payment_instruction` - Standardized payment data with DQ scores

### Gold Layer (CDM Entities)
- `gold_cdm_payment_instruction` - Payment instructions
- `gold_cdm_party` - Debtors/Creditors
- `gold_cdm_account` - Bank accounts
- `gold_cdm_financial_institution` - Banks/FIs

### Observability
- `batch_tracking` - Processing batch status
- `data_lineage` - Layer-to-layer lineage
- `processing_errors` - Error records

## Databricks CE Limitations

- Single cluster (terminates after 2 hours idle)
- 15GB storage limit
- No Unity Catalog (uses Hive metastore)
- No job scheduling (manual runs only)

## Tips

1. **Keep Cluster Running**: Interact with notebooks periodically to prevent timeout
2. **Monitor Storage**: DBFS has limited space - use VACUUM to clean old files
3. **Use OPTIMIZE**: Run `OPTIMIZE table_name` after large loads for better performance

## Sample Data

Create a sample pain.001 file for testing:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>MSG001</MsgId>
      <CreDtTm>2024-01-15T10:00:00</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <Dbtr>
        <Nm>John Doe</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id><IBAN>DE89370400440532013000</IBAN></Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId><BIC>COBADEFFXXX</BIC></FinInstnId>
      </DbtrAgt>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>E2E001</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="EUR">1000.00</InstdAmt>
        </Amt>
        <Cdtr>
          <Nm>Jane Smith</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id><IBAN>FR1420041010050500013M02606</IBAN></Id>
        </CdtrAcct>
        <CdtrAgt>
          <FinInstnId><BIC>BNPAFRPPXXX</BIC></FinInstnId>
        </CdtrAgt>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
```
