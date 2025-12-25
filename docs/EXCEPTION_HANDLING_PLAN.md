# GPS CDM - Exception Handling & Data Governance System

## Overview

Build a comprehensive exception handling system that provides:
1. Record-level tracking through pipeline stages
2. Data quality validation with per-record scoring
3. Reconciliation between source (Bronze) and target (Gold)
4. Re-processing capability for failed/updated records
5. UI visualization for pipeline monitoring and exception management

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────┐             │
│   │ BRONZE  │───▶│ SILVER  │───▶│  GOLD   │───▶│ ANALYTICAL   │             │
│   │  (Raw)  │    │(Staged) │    │  (CDM)  │    │ (Aggregated) │             │
│   └────┬────┘    └────┬────┘    └────┬────┘    └──────────────┘             │
│        │              │              │                                        │
│        ▼              ▼              ▼                                        │
│   ┌─────────────────────────────────────────────────────────────┐           │
│   │              EXCEPTION TRACKING LAYER                        │           │
│   ├─────────────────────────────────────────────────────────────┤           │
│   │  • Processing Exceptions (failed records per stage)          │           │
│   │  • Data Quality Results (per-record DQ scores)               │           │
│   │  • Reconciliation Results (Bronze vs Gold comparison)        │           │
│   │  • Batch/Record Status Tracking                              │           │
│   └─────────────────────────────────────────────────────────────┘           │
│                              │                                               │
│                              ▼                                               │
│   ┌─────────────────────────────────────────────────────────────┐           │
│   │                    UI DASHBOARD                              │           │
│   ├─────────────────────────────────────────────────────────────┤           │
│   │  • Pipeline Visualization                                    │           │
│   │  • Exception Browser (filter by stage, type, severity)       │           │
│   │  • Record Editor (update and re-process)                     │           │
│   │  • Reconciliation View                                       │           │
│   │  • DQ Dashboard                                              │           │
│   └─────────────────────────────────────────────────────────────┘           │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Database Schema Changes

### 1.1 Add Processing Status to Data Tables

```sql
-- Bronze layer: Add status tracking
ALTER TABLE bronze.raw_payment_messages ADD COLUMN IF NOT EXISTS
    processing_status VARCHAR(20) DEFAULT 'PENDING'
    CHECK (processing_status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED', 'REPROCESSING'));
ALTER TABLE bronze.raw_payment_messages ADD COLUMN IF NOT EXISTS
    processing_error TEXT;
ALTER TABLE bronze.raw_payment_messages ADD COLUMN IF NOT EXISTS
    processing_attempts INTEGER DEFAULT 0;
ALTER TABLE bronze.raw_payment_messages ADD COLUMN IF NOT EXISTS
    last_processed_at TIMESTAMP;
ALTER TABLE bronze.raw_payment_messages ADD COLUMN IF NOT EXISTS
    promoted_to_silver_at TIMESTAMP;
ALTER TABLE bronze.raw_payment_messages ADD COLUMN IF NOT EXISTS
    silver_stg_id VARCHAR(36);

-- Silver layer: Add status and DQ tracking
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    processing_status VARCHAR(20) DEFAULT 'PENDING'
    CHECK (processing_status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED', 'REPROCESSING'));
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    processing_error TEXT;
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    dq_status VARCHAR(20) DEFAULT 'NOT_VALIDATED'
    CHECK (dq_status IN ('NOT_VALIDATED', 'VALIDATING', 'PASSED', 'FAILED', 'WARNING'));
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    dq_score DECIMAL(5,2);
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    dq_validated_at TIMESTAMP;
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    promoted_to_gold_at TIMESTAMP;
ALTER TABLE silver.stg_pain001 ADD COLUMN IF NOT EXISTS
    gold_instruction_id VARCHAR(36);

-- Gold layer: Add DQ and reconciliation tracking
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    dq_status VARCHAR(20) DEFAULT 'NOT_VALIDATED'
    CHECK (dq_status IN ('NOT_VALIDATED', 'VALIDATING', 'PASSED', 'FAILED', 'WARNING'));
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    dq_score DECIMAL(5,2);
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    dq_validated_at TIMESTAMP;
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    reconciliation_status VARCHAR(20) DEFAULT 'NOT_RECONCILED'
    CHECK (reconciliation_status IN ('NOT_RECONCILED', 'MATCHED', 'MISMATCHED', 'ORPHAN'));
ALTER TABLE gold.cdm_payment_instruction ADD COLUMN IF NOT EXISTS
    reconciled_at TIMESTAMP;
```

### 1.2 Exception Tracking Tables

```sql
-- Processing Exceptions: Track all failures across pipeline
CREATE TABLE observability.obs_processing_exceptions (
    exception_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,
    pipeline_run_id VARCHAR(36),

    -- Source identification
    source_layer VARCHAR(20) NOT NULL,  -- bronze, silver, gold
    source_table VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(36) NOT NULL,

    -- Target identification (where it failed to go)
    target_layer VARCHAR(20),
    target_table VARCHAR(100),

    -- Exception details
    exception_type VARCHAR(50) NOT NULL,  -- PARSE_ERROR, VALIDATION_ERROR, TRANSFORM_ERROR, DQ_FAILURE, etc.
    exception_code VARCHAR(20),
    exception_message TEXT NOT NULL,
    exception_details JSONB,
    stack_trace TEXT,

    -- Severity and status
    severity VARCHAR(20) DEFAULT 'ERROR' CHECK (severity IN ('WARNING', 'ERROR', 'CRITICAL')),
    status VARCHAR(20) DEFAULT 'NEW' CHECK (status IN ('NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'IGNORED')),
    resolution_notes TEXT,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,

    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_retry_at TIMESTAMP,
    next_retry_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for exception queries
CREATE INDEX idx_exceptions_batch ON observability.obs_processing_exceptions(batch_id);
CREATE INDEX idx_exceptions_source ON observability.obs_processing_exceptions(source_layer, source_table);
CREATE INDEX idx_exceptions_status ON observability.obs_processing_exceptions(status);
CREATE INDEX idx_exceptions_type ON observability.obs_processing_exceptions(exception_type);
CREATE INDEX idx_exceptions_created ON observability.obs_processing_exceptions(created_at DESC);
```

### 1.3 Data Quality Tables

```sql
-- DQ Results: Per-record validation results
CREATE TABLE observability.obs_data_quality_results (
    dq_result_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36) NOT NULL,
    pipeline_run_id VARCHAR(36),

    -- Record identification
    layer VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(36) NOT NULL,

    -- Rule execution
    rule_id VARCHAR(50) NOT NULL,
    rule_name VARCHAR(200),
    rule_type VARCHAR(50),  -- COMPLETENESS, VALIDITY, ACCURACY, CONSISTENCY, UNIQUENESS, TIMELINESS
    rule_expression TEXT,

    -- Result
    passed BOOLEAN NOT NULL,
    actual_value TEXT,
    expected_value TEXT,
    error_message TEXT,

    -- Scoring
    weight DECIMAL(5,2) DEFAULT 1.0,
    score DECIMAL(5,2),  -- 0-100

    -- Metadata
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DQ Metrics: Aggregated quality metrics
CREATE TABLE observability.obs_data_quality_metrics (
    metric_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    batch_id VARCHAR(36),
    pipeline_run_id VARCHAR(36),

    -- Scope
    layer VARCHAR(20) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    field_name VARCHAR(100),  -- NULL for table-level metrics

    -- Dimension scores (0-100)
    completeness_score DECIMAL(5,2),
    validity_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2),
    consistency_score DECIMAL(5,2),
    uniqueness_score DECIMAL(5,2),
    timeliness_score DECIMAL(5,2),

    -- Overall
    overall_score DECIMAL(5,2),

    -- Counts
    total_records INTEGER,
    passed_records INTEGER,
    failed_records INTEGER,
    warning_records INTEGER,

    -- Rules executed
    rules_executed INTEGER,
    rules_passed INTEGER,
    rules_failed INTEGER,

    -- Period
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dq_results_batch ON observability.obs_data_quality_results(batch_id);
CREATE INDEX idx_dq_results_record ON observability.obs_data_quality_results(layer, table_name, record_id);
CREATE INDEX idx_dq_metrics_table ON observability.obs_data_quality_metrics(layer, table_name);
```

### 1.4 Reconciliation Tables

```sql
-- Reconciliation Results: Bronze vs Gold comparison
CREATE TABLE observability.obs_reconciliation_results (
    recon_id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    recon_run_id VARCHAR(36) NOT NULL,
    batch_id VARCHAR(36),

    -- Source (Bronze)
    bronze_raw_id VARCHAR(36) NOT NULL,
    bronze_message_type VARCHAR(50),
    bronze_key_fields JSONB,  -- Key identifying fields from bronze

    -- Target (Gold)
    gold_instruction_id VARCHAR(36),
    gold_key_fields JSONB,  -- Corresponding fields from gold

    -- Reconciliation result
    match_status VARCHAR(20) NOT NULL CHECK (match_status IN (
        'MATCHED',           -- All key fields match
        'PARTIAL_MATCH',     -- Some fields match, some differ
        'MISMATCHED',        -- Key fields don't match
        'BRONZE_ONLY',       -- Exists in bronze, not in gold
        'GOLD_ONLY',         -- Exists in gold, not in bronze (shouldn't happen)
        'MULTIPLE_MATCHES'   -- One bronze maps to multiple gold records
    )),

    -- Field-level comparison
    field_comparisons JSONB,  -- {field: {bronze: val, gold: val, match: bool}}
    mismatched_fields TEXT[], -- List of fields that don't match

    -- Investigation
    investigation_notes TEXT,
    investigated_by VARCHAR(100),
    investigated_at TIMESTAMP,

    -- Resolution
    resolution_action VARCHAR(50),  -- ACCEPTED, CORRECTED, REJECTED
    resolution_notes TEXT,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP,

    -- Metadata
    reconciled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recon_run ON observability.obs_reconciliation_results(recon_run_id);
CREATE INDEX idx_recon_status ON observability.obs_reconciliation_results(match_status);
CREATE INDEX idx_recon_bronze ON observability.obs_reconciliation_results(bronze_raw_id);
CREATE INDEX idx_recon_gold ON observability.obs_reconciliation_results(gold_instruction_id);
```

---

## 2. Python Services

### 2.1 Exception Manager

```python
# src/gps_cdm/orchestration/exception_manager.py

class ExceptionManager:
    """Manages processing exceptions across the pipeline."""

    def log_exception(
        self,
        batch_id: str,
        source_layer: str,
        source_table: str,
        source_record_id: str,
        exception_type: str,
        exception_message: str,
        target_layer: str = None,
        exception_details: dict = None,
        severity: str = "ERROR"
    ) -> str:
        """Log a processing exception."""

    def get_exceptions(
        self,
        batch_id: str = None,
        source_layer: str = None,
        status: str = None,
        exception_type: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get exceptions with filters."""

    def acknowledge_exception(self, exception_id: str, notes: str = None):
        """Mark exception as acknowledged."""

    def resolve_exception(self, exception_id: str, resolution_notes: str, resolved_by: str):
        """Mark exception as resolved."""

    def schedule_retry(self, exception_id: str, retry_at: datetime = None):
        """Schedule a retry for the exception."""

    def get_exception_summary(self, batch_id: str = None) -> Dict:
        """Get summary counts by type, layer, status."""
```

### 2.2 Data Quality Validator

```python
# src/gps_cdm/orchestration/dq_validator.py

class DataQualityValidator:
    """Validates data quality and stores results."""

    def __init__(self, db_connection, rules_config: Dict):
        self.db = db_connection
        self.rules = self._load_rules(rules_config)

    def validate_record(
        self,
        record: Dict,
        layer: str,
        table_name: str,
        batch_id: str
    ) -> DQValidationResult:
        """Validate a single record against all applicable rules."""

    def validate_batch(
        self,
        batch_id: str,
        layer: str,
        table_name: str
    ) -> DQBatchResult:
        """Validate all records in a batch."""

    def calculate_metrics(
        self,
        batch_id: str,
        layer: str,
        table_name: str
    ) -> DQMetrics:
        """Calculate aggregated DQ metrics for a batch."""

    def get_failed_records(
        self,
        batch_id: str = None,
        layer: str = None,
        min_score: float = None
    ) -> List[Dict]:
        """Get records that failed DQ validation."""

    def revalidate_record(self, layer: str, table_name: str, record_id: str) -> DQValidationResult:
        """Re-run validation on a single record (after update)."""
```

### 2.3 Reconciliation Service

```python
# src/gps_cdm/orchestration/reconciliation.py

class ReconciliationService:
    """Reconciles Bronze source with Gold target."""

    def __init__(self, db_connection):
        self.db = db_connection

    def reconcile_batch(self, batch_id: str) -> ReconciliationResult:
        """Reconcile all records in a batch."""

    def reconcile_record(self, bronze_raw_id: str) -> RecordReconciliation:
        """Reconcile a single bronze record with its gold target."""

    def get_mismatches(
        self,
        batch_id: str = None,
        status: str = None
    ) -> List[Dict]:
        """Get records with reconciliation mismatches."""

    def get_orphans(self, direction: str = "bronze") -> List[Dict]:
        """Get orphan records (bronze without gold or vice versa)."""

    def accept_mismatch(self, recon_id: str, notes: str, accepted_by: str):
        """Accept a mismatch as valid (e.g., intentional transformation)."""

    def flag_for_correction(self, recon_id: str, notes: str):
        """Flag a mismatch for data correction."""
```

### 2.4 Re-processing Service

```python
# src/gps_cdm/orchestration/reprocessor.py

class PipelineReprocessor:
    """Handles re-processing of failed or updated records."""

    def __init__(self, db_connection, celery_app=None):
        self.db = db_connection
        self.celery = celery_app

    def reprocess_bronze_record(self, raw_id: str) -> ReprocessResult:
        """Re-process a single bronze record through Silver → Gold."""

    def reprocess_silver_record(self, stg_id: str) -> ReprocessResult:
        """Re-process a silver record to Gold."""

    def reprocess_failed_batch(self, batch_id: str, layer: str = None) -> BatchReprocessResult:
        """Re-process all failed records in a batch."""

    def reprocess_dq_failures(self, batch_id: str = None) -> BatchReprocessResult:
        """Re-process records that failed DQ after data correction."""

    def update_and_reprocess(
        self,
        layer: str,
        table_name: str,
        record_id: str,
        updates: Dict,
        reprocess: bool = True
    ) -> Tuple[bool, Optional[ReprocessResult]]:
        """Update a record and optionally re-process through pipeline."""
```

---

## 3. API Endpoints (FastAPI)

```python
# src/gps_cdm/api/routes/exceptions.py

@router.get("/exceptions")
async def list_exceptions(
    batch_id: str = None,
    layer: str = None,
    status: str = None,
    exception_type: str = None,
    page: int = 1,
    page_size: int = 50
) -> ExceptionListResponse:
    """List processing exceptions with filters."""

@router.get("/exceptions/{exception_id}")
async def get_exception(exception_id: str) -> ExceptionDetailResponse:
    """Get detailed exception information."""

@router.post("/exceptions/{exception_id}/acknowledge")
async def acknowledge_exception(exception_id: str, notes: str = None):
    """Acknowledge an exception."""

@router.post("/exceptions/{exception_id}/resolve")
async def resolve_exception(exception_id: str, resolution: ResolutionRequest):
    """Resolve an exception."""

@router.post("/exceptions/{exception_id}/retry")
async def retry_exception(exception_id: str):
    """Retry processing for a failed record."""


# src/gps_cdm/api/routes/data_quality.py

@router.get("/dq/summary")
async def dq_summary(batch_id: str = None, layer: str = None) -> DQSummaryResponse:
    """Get DQ summary metrics."""

@router.get("/dq/failures")
async def dq_failures(
    batch_id: str = None,
    layer: str = None,
    min_score: float = None
) -> DQFailureListResponse:
    """List records with DQ failures."""

@router.post("/dq/validate/{layer}/{table}/{record_id}")
async def validate_record(layer: str, table: str, record_id: str) -> DQValidationResponse:
    """Validate a single record."""

@router.post("/dq/validate-batch/{batch_id}")
async def validate_batch(batch_id: str, layer: str = "gold") -> DQBatchResponse:
    """Run DQ validation on entire batch."""


# src/gps_cdm/api/routes/reconciliation.py

@router.get("/recon/summary")
async def recon_summary(batch_id: str = None) -> ReconSummaryResponse:
    """Get reconciliation summary."""

@router.get("/recon/mismatches")
async def list_mismatches(
    batch_id: str = None,
    status: str = None
) -> MismatchListResponse:
    """List reconciliation mismatches."""

@router.post("/recon/run/{batch_id}")
async def run_reconciliation(batch_id: str) -> ReconRunResponse:
    """Run reconciliation for a batch."""

@router.post("/recon/{recon_id}/accept")
async def accept_mismatch(recon_id: str, request: AcceptRequest):
    """Accept a mismatch as valid."""


# src/gps_cdm/api/routes/reprocess.py

@router.post("/reprocess/record")
async def reprocess_record(request: ReprocessRecordRequest) -> ReprocessResponse:
    """Re-process a single record."""

@router.post("/reprocess/batch/{batch_id}")
async def reprocess_batch(batch_id: str, layer: str = None) -> ReprocessBatchResponse:
    """Re-process failed records in batch."""

@router.put("/records/{layer}/{table}/{record_id}")
async def update_record(
    layer: str,
    table: str,
    record_id: str,
    updates: Dict,
    reprocess: bool = True
) -> UpdateResponse:
    """Update a record and optionally re-process."""
```

---

## 4. UI Components

### 4.1 Pipeline Visualization Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GPS CDM Pipeline Monitor                                    [Batch: xyz123]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│   │  BRONZE  │─────▶│  SILVER  │─────▶│   GOLD   │─────▶│ANALYTICAL│       │
│   │          │      │          │      │          │      │          │       │
│   │ 1,000    │      │   950    │      │   920    │      │   920    │       │
│   │ records  │      │ records  │      │ records  │      │ records  │       │
│   │          │      │          │      │          │      │          │       │
│   │ ⚠ 50     │      │ ⚠ 30     │      │ ⚠ 15     │      │          │       │
│   │ failed   │      │ failed   │      │ DQ fail  │      │          │       │
│   └──────────┘      └──────────┘      └──────────┘      └──────────┘       │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Data Quality Score: 92%  │  Reconciliation: 98% Match  │  Exceptions: 95  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Exception Browser

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Exceptions  [Filter: Layer▼] [Type▼] [Status▼] [Severity▼]     [Search 🔍]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ☐ │ ID        │ Layer  │ Type           │ Message          │ Status │ Act │
│  ──┼───────────┼────────┼────────────────┼──────────────────┼────────┼─────│
│  ☐ │ exc-001   │ Bronze │ PARSE_ERROR    │ Invalid XML...   │ NEW    │ ⟳ 👁│
│  ☐ │ exc-002   │ Silver │ VALIDATION_ERR │ Amount negative  │ NEW    │ ⟳ 👁│
│  ☐ │ exc-003   │ Gold   │ DQ_FAILURE     │ BIC invalid      │ ACK    │ ✏️ 👁│
│  ☐ │ exc-004   │ Bronze │ TRANSFORM_ERR  │ Date parse fail  │ RESOL  │ 👁  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Bulk Actions: Acknowledge ▼]  [Re-process Selected]  [Export]             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Record Editor with Re-process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Edit Record: silver.stg_pain001.abc123                   [Save] [Reprocess]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ Source (Bronze) ──────────────────┐  ┌─ Current (Silver) ─────────────┐│
│  │ msg_id: PAIN001-2024-001           │  │ msg_id: [PAIN001-2024-001    ]│ │
│  │ debtor_name: John Smith            │  │ debtor_name: [John Smith     ]│ │
│  │ amount: 10000.00                   │  │ amount: [10000.00      ] ⚠ DQ │ │
│  │ currency: USD                      │  │ currency: [USD           ]    │ │
│  │ debtor_bic: CHASUS33XXX            │  │ debtor_bic: [CHASUS33    ] ❌ │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘│
│                                                                              │
│  DQ Issues:                                                                  │
│  ❌ debtor_bic: Invalid BIC format (expected 8 or 11 chars, got 9)          │
│  ⚠ amount: Unusually high value - review required                           │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  History: [Created: 2024-12-24 10:00] [Validated: 2024-12-24 10:01 - FAIL]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 Reconciliation View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Reconciliation: Bronze ↔ Gold                              [Run Recon 🔄] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Summary:  ✅ Matched: 920  │  ⚠ Mismatched: 15  │  🔶 Bronze Only: 50      │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────│
│  │ Bronze ID   │ Gold ID     │ Status      │ Mismatched Fields    │ Action│
│  ├─────────────┼─────────────┼─────────────┼──────────────────────┼───────│
│  │ raw-001     │ inst-001    │ MISMATCHED  │ amount, currency     │ [👁]  │
│  │ raw-002     │ -           │ BRONZE_ONLY │ (not promoted)       │ [⟳]   │
│  │ raw-003     │ inst-003    │ MATCHED     │ -                    │ -     │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Field Comparison for raw-001:                                              │
│  ┌──────────────┬──────────────┬──────────────┬────────┐                    │
│  │ Field        │ Bronze       │ Gold         │ Match  │                    │
│  ├──────────────┼──────────────┼──────────────┼────────┤                    │
│  │ amount       │ 10000.00     │ 10000.0000   │ ✅     │                    │
│  │ currency     │ USD          │ US           │ ❌     │                    │
│  │ debtor_name  │ John Smith   │ John Smith   │ ✅     │                    │
│  └──────────────┴──────────────┴──────────────┴────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Implementation Phases

### Phase 1: Database Schema & Core Services (2-3 hours)
- Create exception tracking tables
- Create DQ results/metrics tables
- Create reconciliation tables
- Add status columns to Bronze/Silver/Gold tables
- Create ExceptionManager service
- Create basic DQ Validator

### Phase 2: Re-processing & Reconciliation (2-3 hours)
- Create PipelineReprocessor service
- Create ReconciliationService
- Integrate with Celery tasks
- Add re-processing queues

### Phase 3: API Layer (2 hours)
- Create FastAPI routes for exceptions
- Create routes for DQ management
- Create routes for reconciliation
- Create routes for re-processing

### Phase 4: Integration Testing (1-2 hours)
- Test exception capture at each stage
- Test DQ validation workflow
- Test reconciliation workflow
- Test re-processing workflow

### Phase 5: UI Dashboard (optional, 4-6 hours)
- React/Vue dashboard components
- Pipeline visualization
- Exception browser
- Record editor
- Reconciliation view

---

## 6. Key Queries

### Get records stuck at each stage
```sql
-- Records that failed Bronze → Silver
SELECT b.raw_id, b.message_type, b.processing_status, b.processing_error
FROM bronze.raw_payment_messages b
WHERE b.processing_status = 'FAILED'
   OR (b.processing_status = 'PROCESSED' AND b.silver_stg_id IS NULL);

-- Records that failed Silver → Gold
SELECT s.stg_id, s.msg_id, s.processing_status, s.processing_error
FROM silver.stg_pain001 s
WHERE s.processing_status = 'FAILED'
   OR (s.processing_status = 'PROCESSED' AND s.gold_instruction_id IS NULL);

-- Records with DQ failures at Gold
SELECT g.instruction_id, g.end_to_end_id, g.dq_status, g.dq_score
FROM gold.cdm_payment_instruction g
WHERE g.dq_status = 'FAILED';
```

### Reconciliation query
```sql
-- Find Bronze records not in Gold
SELECT b.raw_id, b.message_type, s.stg_id
FROM bronze.raw_payment_messages b
LEFT JOIN silver.stg_pain001 s ON b.raw_id = s.raw_id
LEFT JOIN gold.cdm_payment_instruction g ON s.stg_id = g.source_stg_id
WHERE g.instruction_id IS NULL
  AND b.processing_status = 'PROCESSED';
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `/ddl/postgresql/07_exception_handling.sql` | Exception, DQ, Recon tables |
| `/src/gps_cdm/orchestration/exception_manager.py` | Exception tracking service |
| `/src/gps_cdm/orchestration/dq_validator.py` | Data quality validation |
| `/src/gps_cdm/orchestration/reconciliation.py` | Bronze-Gold reconciliation |
| `/src/gps_cdm/orchestration/reprocessor.py` | Re-processing service |
| `/src/gps_cdm/api/__init__.py` | FastAPI app setup |
| `/src/gps_cdm/api/routes/exceptions.py` | Exception API routes |
| `/src/gps_cdm/api/routes/data_quality.py` | DQ API routes |
| `/src/gps_cdm/api/routes/reconciliation.py` | Reconciliation API routes |
| `/src/gps_cdm/api/routes/reprocess.py` | Re-processing API routes |
