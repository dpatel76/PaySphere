# GPS CDM - Databricks Free Edition Notebooks

Notebooks for running GPS CDM on **Databricks Free Edition** (the new replacement for Community Edition).

## Quick Start

1. **Create Account**: https://www.databricks.com/try-databricks
2. **Import Notebooks**: Workspace > Import > Upload `.py` files
3. **Run Setup**: Execute `01_setup_gps_cdm`
4. **Upload Data**: Catalog > Volumes > cdm_data > Upload XML files
5. **Process**: Run `02_ingest_payment_messages`

## Key Differences from Community Edition

| Feature | Community Edition | Free Edition |
|---------|------------------|--------------|
| Compute | Classic clusters | **Serverless** |
| Storage | DBFS paths | **Unity Catalog Volumes** |
| Governance | None | **Unity Catalog** |
| Languages | Python, Scala, SQL, R | Python, SQL only |
| Status | Retiring Jan 2026 | **Current** |

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_setup_gps_cdm.py` | Create schema, volume, and tables |
| `02_ingest_payment_messages.py` | Process XML through medallion layers |

## Data Storage

### Unity Catalog Structure
```
main (catalog)
  cdm_dev (schema)
    cdm_data (volume)  <- Upload files here
      raw_input/
        sample_pain001.xml
    bronze_raw_payment (table)
    silver_stg_payment_instruction (table)
    gold_cdm_payment_instruction (table)
    gold_cdm_party (table)
    gold_cdm_account (table)
    gold_cdm_financial_institution (table)
    obs_batch_tracking (table)
    obs_data_lineage (table)
    obs_processing_errors (table)
```

### Volume Paths
- Upload: `/Volumes/main/cdm_dev/cdm_data/raw_input/`
- Access in SQL: `FROM read_files('/Volumes/main/cdm_dev/cdm_data/raw_input/*.xml')`

## Uploading Files

### Option 1: UI (Easiest)
1. Go to Catalog in left sidebar
2. Navigate: main > cdm_dev > Volumes > cdm_data
3. Click "Upload" and select XML files

### Option 2: Python
```python
dbutils.fs.put(
    "/Volumes/main/cdm_dev/cdm_data/raw_input/payment.xml",
    xml_content,
    overwrite=True
)
```

### Option 3: REST API
```bash
curl -X PUT "https://<workspace>.cloud.databricks.com/api/2.0/fs/files/Volumes/main/cdm_dev/cdm_data/raw_input/payment.xml" \
  -H "Authorization: Bearer <token>" \
  -d @payment.xml
```

## Supported Message Types

- `pain.001` - Customer Credit Transfer Initiation
- `pain.002` - Payment Status Report
- `camt.053` - Bank to Customer Statement
- `camt.054` - Bank to Customer Debit Credit Notification
- `pacs.008` - FI to FI Customer Credit Transfer

## Free Edition Limits

- **Daily compute quota** - Generous for learning (99% of users won't hit limits)
- **Storage** - Included with account
- **No GPUs** - CPU only
- **Python/SQL only** - No Scala or RDDs

If you hit daily limits, compute pauses until the next day.

## Sample Data

Create sample pain.001 in notebook:
```python
sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>MSG001</MsgId>
      <CreDtTm>2024-01-15T10:00:00</CreDtTm>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT001</PmtInfId>
      <Dbtr><Nm>John Doe</Nm></Dbtr>
      <DbtrAcct><Id><IBAN>DE89370400440532013000</IBAN></Id></DbtrAcct>
      <CdtTrfTxInf>
        <Amt><InstdAmt Ccy="EUR">1000.00</InstdAmt></Amt>
        <Cdtr><Nm>Jane Smith</Nm></Cdtr>
        <CdtrAcct><Id><IBAN>FR1420041010050500013M02606</IBAN></Id></CdtrAcct>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>'''

dbutils.fs.put("/Volumes/main/cdm_dev/cdm_data/raw_input/sample.xml", sample_xml, overwrite=True)
```

## References

- [Databricks Free Edition FAQ](https://www.databricks.com/product/faq/community-edition)
- [Unity Catalog Volumes](https://docs.databricks.com/en/connect/unity-catalog/volumes.html)
- [Delta Lake Documentation](https://docs.delta.io/)
