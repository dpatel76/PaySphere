/**
 * GPS CDM TypeScript Types
 */

// Pipeline & Batch Types
export interface BatchTracking {
  batch_id: string;
  source_system: string;
  message_type: string;
  status: string;
  bronze_records: number;
  silver_records: number;
  gold_records: number;
  failed_records: number;
  started_at: string;
  completed_at?: string;
  dq_score?: number;
  dq_status?: string;
  recon_status?: string;
  recon_match_rate?: number;
}

// Exception Types
export interface ProcessingException {
  exception_id: string;
  batch_id: string;
  source_layer: string;
  source_table: string;
  source_record_id: string;
  exception_type: string;
  exception_code?: string;
  exception_message: string;
  exception_details?: Record<string, any>;
  severity: 'WARNING' | 'ERROR' | 'CRITICAL';
  status: 'NEW' | 'ACKNOWLEDGED' | 'IN_PROGRESS' | 'RESOLVED' | 'IGNORED';
  resolution_notes?: string;
  resolved_by?: string;
  resolved_at?: string;
  retry_count: number;
  max_retries: number;
  can_retry: boolean;
  created_at: string;
}

export interface ExceptionSummary {
  total: number;
  by_type: Record<string, number>;
  by_layer: Record<string, number>;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  new_count: number;
  resolved_count: number;
  critical_count: number;
  retryable_count: number;
}

// Data Quality Types
export interface DQMetrics {
  layer: string;
  table_name: string;
  batch_id?: string;
  completeness_score?: number;
  validity_score?: number;
  accuracy_score?: number;
  overall_score?: number;
  overall_status: string;
  total_records: number;
  passed_records: number;
  failed_records: number;
}

export interface DQRule {
  rule_id: string;
  rule_name: string;
  rule_description?: string;
  layer: string;
  table_name: string;
  field_name?: string;
  rule_type: string;
  rule_expression?: string;
  weight: number;
  is_blocking: boolean;
}

export interface DQResult {
  dq_result_id: string;
  layer: string;
  table_name: string;
  record_id: string;
  rule_id: string;
  rule_name: string;
  passed: boolean;
  actual_value?: string;
  expected_value?: string;
  error_message?: string;
  score: number;
  validated_at: string;
}

// Reconciliation Types
export interface ReconciliationRun {
  recon_run_id: string;
  batch_id?: string;
  status: string;
  total_source_records: number;
  total_target_records: number;
  matched_count: number;
  mismatched_count: number;
  source_only_count: number;
  match_rate: number;
  started_at: string;
  completed_at?: string;
}

export interface ReconciliationMismatch {
  recon_id: string;
  batch_id: string;
  bronze_raw_id?: string;
  silver_stg_id?: string;
  gold_instruction_id?: string;
  mismatch_type: string;
  field_name?: string;
  source_value?: string;
  target_value?: string;
  investigation_status: string;
  investigation_notes?: string;
  resolution_action?: string;
  created_at: string;
}

// Lineage Types
export interface FieldLineage {
  source_layer: string;
  source_table: string;
  source_field: string;
  source_path?: string;
  target_layer: string;
  target_table: string;
  target_field: string;
  transformation_type?: string;
  transformation_logic?: string;
  data_type: string;
  message_type: string;
}

export interface LineageGraph {
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export interface LineageNode {
  id: string;
  label: string;
  type: 'layer' | 'table' | 'field';
  layer?: string;
  data?: Record<string, any>;
}

export interface LineageEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  transformation?: string;
}

// Record Types
export interface BronzeRecord {
  raw_id: string;
  batch_id: string;
  message_type: string;
  message_format: string;
  raw_content: string;
  source_system: string;
  processing_status: string;
  processing_error?: string;
  ingested_at: string;
  silver_stg_id?: string;
}

export interface SilverRecord {
  stg_id: string;
  batch_id: string;
  msg_id: string;
  instructed_amount?: number;
  instructed_currency?: string;
  debtor_name?: string;
  creditor_name?: string;
  processing_status: string;
  dq_status: string;
  dq_score?: number;
  gold_instruction_id?: string;
}

export interface GoldRecord {
  instruction_id: string;
  payment_id: string;
  source_message_type: string;
  payment_type: string;
  instructed_amount: number;
  instructed_currency: string;
  dq_status: string;
  reconciliation_status: string;
  created_at: string;
}

// Pipeline Overview
export interface PipelineStats {
  bronze: {
    total: number;
    processed: number;
    failed: number;
    pending: number;
  };
  silver: {
    total: number;
    processed: number;
    failed: number;
    pending: number;
    dq_passed: number;
    dq_failed: number;
  };
  gold: {
    total: number;
    reconciled: number;
    mismatched: number;
  };
  exceptions: {
    total: number;
    critical: number;
    unresolved: number;
  };
}

// Reprocess Types
export interface ReprocessResult {
  record_id: string;
  source_layer: string;
  status: string;
  promoted_to_layer?: string;
  new_record_id?: string;
  error_message?: string;
}

export interface BatchReprocessResult {
  batch_id: string;
  total_records: number;
  success_count: number;
  failed_count: number;
  skipped_count: number;
  duration_seconds: number;
}

// =====================
// Extended Batch Tracking Types
// =====================

// Zone-level metrics for a batch
export interface ZoneMetrics {
  input_records: number;
  processed_records: number;
  failed_records: number;
  pending_records: number;
  exceptions: number;
  dq_passed?: number;
  dq_failed?: number;
  dq_score?: number;
}

// Extended batch tracking with per-zone metrics
export interface BatchTrackingExtended extends BatchTracking {
  created_at: string;
  bronze_input: number;
  bronze_processed: number;
  bronze_exceptions: number;
  silver_input: number;
  silver_processed: number;
  silver_exceptions: number;
  gold_input: number;
  gold_processed: number;
  gold_exceptions: number;
  analytics_input: number;
  analytics_processed: number;
  analytics_exceptions: number;
}

// Detailed batch information
export interface BatchDetail {
  batch_id: string;
  source_system: string;
  message_type: string;
  source_file?: string;
  status: string;
  created_at: string;
  completed_at?: string;
  duration_seconds?: number;
  metrics: {
    bronze: ZoneMetrics;
    silver: ZoneMetrics;
    gold: ZoneMetrics;
    analytics: ZoneMetrics;
  };
  timing: {
    ingestion_start: string;
    bronze_complete?: string;
    silver_complete?: string;
    gold_complete?: string;
    analytics_complete?: string;
  };
  error_summary?: {
    total_errors: number;
    by_type: Record<string, number>;
    by_severity: Record<string, number>;
  };
}

// Paginated response wrapper
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Generic record for any layer/table (JSON-driven)
export interface GenericRecord {
  _id: string;
  _table: string;
  _layer: string;
  _batch_id: string;
  _created_at: string;
  _message_type?: string;
  [key: string]: unknown;
}

// =====================
// Schema Types (for JSON-driven UI)
// =====================

export interface RecordDisplayConfig {
  message_type: string;
  layer: 'bronze' | 'silver' | 'gold' | 'analytics';
  table_name: string;
  primary_key: string;
  display_columns: FieldDisplayConfig[];
  editable_fields: string[];
  key_mapping?: KeyMappingConfig;
}

export interface FieldDisplayConfig {
  field_name: string;
  display_name: string;
  data_type: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  render_type?: 'text' | 'currency' | 'date' | 'datetime' | 'chip' | 'json' | 'link';
  format?: string;
  enum_values?: string[];
  validation?: ValidationConfig;
}

export interface ValidationConfig {
  required?: boolean;
  max_length?: number;
  pattern?: string;
  min?: number;
  max?: number;
}

export interface KeyMappingConfig {
  bronze_key: string;
  silver_key: string;
  gold_key: string;
  lookup_paths: {
    bronze_to_silver: string;
    silver_to_gold: string;
  };
}

// =====================
// Enhanced Lineage Types (for graph visualization)
// =====================

export interface LineageGraphData {
  nodes: EnhancedLineageNode[];
  edges: EnhancedLineageEdge[];
}

export interface EnhancedLineageNode {
  id: string;
  type: 'zone' | 'entity' | 'field';
  zone: 'bronze' | 'silver' | 'gold' | 'analytics';
  label: string;
  entityType?: string;
  fieldName?: string;
  dataType?: string;
  position?: { x: number; y: number };
}

export interface EnhancedLineageEdge {
  id: string;
  source: string;
  target: string;
  type: 'entity_transform' | 'field_mapping';
  transformationType?: 'direct' | 'lookup' | 'expression' | 'custom_function';
  transformationLogic?: string;
  sourceFieldName?: string;
  targetFieldName?: string;
}

export interface FieldLineageEntry {
  message_type: string;
  field_path: string;
  variations: {
    bronze?: { table: string; field: string; path?: string };
    silver?: { table: string; field: string };
    gold?: { table: string; field: string };
    analytics?: { table: string; field: string };
  };
  transformations: {
    bronze_to_silver?: TransformRule;
    silver_to_gold?: TransformRule;
    gold_to_analytics?: TransformRule;
  };
}

export interface TransformRule {
  type: 'direct' | 'lookup' | 'expression' | 'custom_function';
  logic?: string;
  lookup_table?: string;
  expression?: string;
}
