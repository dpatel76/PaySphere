# GPS CDM Test Data Samples

This directory contains sample payment messages in their native formats for E2E testing.

## Files

| File | Standard | Format | Description |
|------|----------|--------|-------------|
| `pain.001_sample.xml` | ISO 20022 pain.001.001.09 | XML | Customer Credit Transfer Initiation |
| `MT103_sample.txt` | SWIFT MT103 | Block format | Single Customer Credit Transfer |
| `fedwire_sample.txt` | FEDWIRE | Tag-value | Funds Transfer Message |
| `ach_sample.txt` | NACHA ACH | Fixed-width | ACH PPD Credit Entry |
| `sepa_sample.xml` | SEPA CT (pain.001) | XML | SEPA Credit Transfer |
| `rtp_sample.xml` | TCH RTP (pacs.008) | XML | Real-Time Payment Credit Transfer |

## Format Details

### pain.001 (ISO 20022)
- Namespace: `urn:iso:std:iso:20022:tech:xsd:pain.001.001.09`
- Root element: `Document/CstmrCdtTrfInitn`
- Used for: Batch payment initiation from customer to bank

### MT103 (SWIFT)
- Block structure: {1:Basic}{2:App}{3:User}{4:Text}{5:Trailer}
- Fields prefixed with `:XX:` where XX is field tag
- Used for: Individual cross-border wire transfers

### FEDWIRE
- Tag-value format: `{XXXX}value` where XXXX is 4-digit tag
- Fixed structure with mandatory/optional tags
- Used for: US domestic high-value wire transfers

### ACH (NACHA)
- Fixed-width records (94 characters per line)
- Record types: 1 (File Header), 5 (Batch Header), 6 (Entry Detail), 7 (Addenda), 8 (Batch Control), 9 (File Control)
- Used for: US domestic batch ACH payments

### SEPA
- Same as pain.001 with SEPA-specific rules
- Charge Bearer must be SLEV
- Currency must be EUR
- IBANs required for both debtor and creditor

### RTP (Real-Time Payments)
- Based on ISO 20022 pacs.008
- Namespace: `urn:tch:xsd:pacs.008.001.01`
- Uses RTN (Routing Transit Numbers) for FI identification
- Settlement is same-day (instant)

## Usage

### Copy to NiFi input directory
```bash
# Copy pain.001 sample
docker cp tests/data/samples/pain.001_sample.xml gps-cdm-nifi:/opt/nifi/nifi-current/input/

# Wait for processing
sleep 35

# Check results in database
docker exec gps-cdm-postgres psql -U gps_cdm_svc -d gps_cdm -c \
  "SELECT * FROM gold.cdm_payment_instruction ORDER BY created_at DESC LIMIT 5;"
```

### Direct Celery submission
```python
from gps_cdm.orchestration.celery_tasks import process_bronze_partition
import json

# Read sample file
with open('tests/data/samples/pain.001_sample.xml', 'r') as f:
    content = f.read()

# Submit to Celery
result = process_bronze_partition.delay(
    partition_id="test_pain001",
    file_paths=[],
    message_type="pain.001",
    batch_id="test_batch_001",
    config={"message_content": {"raw_xml": content}}
)

print(f"Task ID: {result.id}")
print(f"Result: {result.get(timeout=60)}")
```

## Validation

All samples have been validated against their respective standards:
- pain.001/SEPA: XSD schema validation
- MT103: SWIFT format rules
- FEDWIRE: Fed specification tags
- ACH: NACHA file format rules
- RTP: TCH message specification
