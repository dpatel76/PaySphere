/**
 * GPS CDM API Client
 */
import axios from 'axios';
import type {
  ProcessingException,
  ExceptionSummary,
  DQMetrics,
  DQRule,
  DQResult,
  ReconciliationRun,
  ReconciliationMismatch,
  FieldLineage,
  LineageGraph,
  ReprocessResult,
  BatchReprocessResult,
  BatchTracking,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const TOKEN_STORAGE_KEY = 'gps_cdm_tokens';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const storedTokens = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (storedTokens) {
      const tokens = JSON.parse(storedTokens);
      if (tokens.access_token) {
        config.headers.Authorization = `Bearer ${tokens.access_token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear stored tokens
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem('gps_cdm_user');
      // Redirect to login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// =====================
// Exception API
// =====================
export const exceptionApi = {
  getSummary: async (batchId?: string, hoursBack: number = 24): Promise<ExceptionSummary> => {
    const params = new URLSearchParams();
    if (batchId) params.append('batch_id', batchId);
    params.append('hours_back', hoursBack.toString());
    const { data } = await api.get(`/exceptions/summary?${params}`);
    return data;
  },

  getExceptions: async (filters: {
    batch_id?: string;
    layer?: string;
    exception_type?: string;
    severity?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<ProcessingException[]> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) params.append(key, value.toString());
    });
    const { data } = await api.get(`/exceptions?${params}`);
    return data;
  },

  getException: async (exceptionId: string): Promise<ProcessingException> => {
    const { data } = await api.get(`/exceptions/${exceptionId}`);
    return data;
  },

  acknowledge: async (exceptionId: string, notes: string): Promise<void> => {
    await api.post(`/exceptions/${exceptionId}/acknowledge`, { notes });
  },

  resolve: async (exceptionId: string, resolution: {
    resolution_action: string;
    notes: string;
    resolved_by: string;
  }): Promise<void> => {
    await api.post(`/exceptions/${exceptionId}/resolve`, resolution);
  },

  scheduleRetry: async (exceptionId: string): Promise<void> => {
    await api.post(`/exceptions/${exceptionId}/retry`);
  },

  // Simplified action methods
  acknowledgeException: async (exceptionId: string): Promise<void> => {
    await api.post(`/exceptions/${exceptionId}/acknowledge`, { notes: 'Acknowledged' });
  },

  resolveException: async (exceptionId: string, notes: string): Promise<void> => {
    await api.post(`/exceptions/${exceptionId}/resolve`, {
      resolution_action: 'RESOLVED',
      notes,
      resolved_by: 'system',
    });
  },

  retryException: async (exceptionId: string): Promise<void> => {
    await api.post(`/exceptions/${exceptionId}/retry`);
  },
};

// =====================
// Data Quality API
// =====================
export const dqApi = {
  getSummary: async (batchId?: string, layer?: string): Promise<DQMetrics[]> => {
    const params = new URLSearchParams();
    if (batchId) params.append('batch_id', batchId);
    if (layer) params.append('layer', layer);
    const { data } = await api.get(`/dq/summary?${params}`);
    return data;
  },

  getFailures: async (filters: {
    batch_id?: string;
    layer?: string;
    table_name?: string;
    limit?: number;
  }): Promise<DQResult[]> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) params.append(key, value.toString());
    });
    const { data } = await api.get(`/dq/failures?${params}`);
    return data;
  },

  getRules: async (layer?: string, tableName?: string): Promise<DQRule[]> => {
    const params = new URLSearchParams();
    if (layer) params.append('layer', layer);
    if (tableName) params.append('table_name', tableName);
    const { data } = await api.get(`/dq/rules?${params}`);
    return data;
  },

  validateRecord: async (layer: string, table: string, recordId: string, batchId: string): Promise<any> => {
    const { data } = await api.post(`/dq/validate/${layer}/${table}/${recordId}?batch_id=${batchId}`);
    return data;
  },

  validateBatch: async (batchId: string, layer: string = 'silver', tableName: string = 'stg_pain001'): Promise<any> => {
    const { data } = await api.post(`/dq/validate-batch/${batchId}`, { layer, table_name: tableName });
    return data;
  },
};

// =====================
// Reconciliation API
// =====================
export const reconApi = {
  getSummary: async (batchId?: string, hoursBack: number = 24): Promise<any> => {
    const params = new URLSearchParams();
    if (batchId) params.append('batch_id', batchId);
    params.append('hours_back', hoursBack.toString());
    const { data } = await api.get(`/recon/summary?${params}`);
    return data;
  },

  getMismatches: async (filters: {
    batch_id?: string;
    status?: string;
    investigation_status?: string;
    limit?: number;
  }): Promise<ReconciliationMismatch[]> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) params.append(key, value.toString());
    });
    const { data } = await api.get(`/recon/mismatches?${params}`);
    return data;
  },

  getOrphans: async (direction: 'bronze' | 'gold', batchId?: string): Promise<any[]> => {
    const params = new URLSearchParams({ direction });
    if (batchId) params.append('batch_id', batchId);
    const { data } = await api.get(`/recon/orphans?${params}`);
    return data;
  },

  runReconciliation: async (batchId: string, initiatedBy?: string): Promise<ReconciliationRun> => {
    const params = initiatedBy ? `?initiated_by=${initiatedBy}` : '';
    const { data } = await api.post(`/recon/run/${batchId}${params}`);
    return data;
  },

  investigate: async (reconId: string, notes: string, investigatedBy: string): Promise<void> => {
    await api.post(`/recon/${reconId}/investigate`, { notes, investigated_by: investigatedBy });
  },

  resolve: async (reconId: string, action: string, notes: string, resolvedBy: string): Promise<void> => {
    await api.post(`/recon/${reconId}/resolve`, { action, notes, resolved_by: resolvedBy });
  },

  getHistory: async (batchId?: string, limit: number = 20): Promise<ReconciliationRun[]> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (batchId) params.append('batch_id', batchId);
    const { data } = await api.get(`/recon/history?${params}`);
    return data;
  },
};

// =====================
// Reprocess API
// =====================
export const reprocessApi = {
  reprocessRecord: async (layer: string, recordId: string, force: boolean = false): Promise<ReprocessResult> => {
    const { data } = await api.post('/reprocess/record', { layer, record_id: recordId, force });
    return data;
  },

  reprocessBatch: async (batchId: string, layer?: string, limit: number = 100): Promise<BatchReprocessResult> => {
    const { data } = await api.post(`/reprocess/batch/${batchId}`, { layer, limit });
    return data;
  },

  reprocessDQFailures: async (batchId?: string, limit: number = 100): Promise<BatchReprocessResult> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (batchId) params.append('batch_id', batchId);
    const { data } = await api.post(`/reprocess/dq-failures?${params}`);
    return data;
  },

  reprocessExceptions: async (batchId?: string, exceptionType?: string, limit: number = 100): Promise<BatchReprocessResult> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (batchId) params.append('batch_id', batchId);
    if (exceptionType) params.append('exception_type', exceptionType);
    const { data } = await api.post(`/reprocess/exceptions?${params}`);
    return data;
  },

  updateRecord: async (layer: string, table: string, recordId: string, updates: Record<string, any>, reprocess: boolean = true): Promise<any> => {
    const { data } = await api.put(`/reprocess/record/${layer}/${table}/${recordId}?reprocess=${reprocess}`, updates);
    return data;
  },

  getStuckRecords: async (batchId?: string, limit: number = 100): Promise<any> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (batchId) params.append('batch_id', batchId);
    const { data } = await api.get(`/reprocess/stuck-records?${params}`);
    return data;
  },
};

// =====================
// Lineage API
// =====================
export const lineageApi = {
  getMessageTypeLineage: async (messageType: string): Promise<any> => {
    const { data } = await api.get(`/lineage/message-type/${messageType}`);
    return data;
  },

  getFieldLineage: async (messageType: string, filters?: {
    field_name?: string;
    layer?: string;
    data_type?: string;
  }): Promise<FieldLineage[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params.append(key, value);
      });
    }
    const { data } = await api.get(`/lineage/message-type/${messageType}/fields?${params}`);
    return data;
  },

  getBackwardLineageFromEntity: async (entityTable: string, fieldName?: string): Promise<any> => {
    const params = fieldName ? `?field_name=${fieldName}` : '';
    const { data } = await api.get(`/lineage/backward/entity/${entityTable}${params}`);
    return data;
  },

  getBackwardLineageFromReport: async (reportType: string, fieldName?: string): Promise<any> => {
    const params = fieldName ? `?field_name=${fieldName}` : '';
    const { data } = await api.get(`/lineage/backward/report/${reportType}${params}`);
    return data;
  },

  getLineageGraph: async (messageType: string): Promise<LineageGraph> => {
    const { data } = await api.get(`/lineage/graph/${messageType}`);
    return data;
  },

  getSupportedMessageTypes: async (): Promise<{ supported_types: any[]; count: number }> => {
    const { data } = await api.get('/lineage/supported-message-types');
    return data;
  },

  getSupportedReports: async (): Promise<{ reports: any[] }> => {
    const { data } = await api.get('/lineage/supported-reports');
    return data;
  },

  getCDMEntities: async (): Promise<{ entities: any[] }> => {
    const { data } = await api.get('/lineage/cdm-entities');
    return data;
  },
};

// =====================
// Pipeline API
// =====================
export const pipelineApi = {
  getBatches: async (filters?: {
    status?: string;
    message_type?: string;
    hours_back?: number;
    limit?: number;
    page?: number;
    page_size?: number;
  }): Promise<{ items: BatchTracking[]; total: number; page: number; page_size: number; total_pages: number } | BatchTracking[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params.append(key, value.toString());
      });
    }
    const { data } = await api.get(`/pipeline/batches?${params}`);
    return data;
  },

  getBatch: async (batchId: string): Promise<BatchTracking> => {
    const { data } = await api.get(`/pipeline/batches/${batchId}`);
    return data;
  },

  getPipelineStats: async (batchId?: string): Promise<any> => {
    const params = batchId ? `?batch_id=${batchId}` : '';
    const { data } = await api.get(`/pipeline/stats${params}`);
    return data;
  },

  getBatchRecords: async (
    batchId: string,
    layer: 'bronze' | 'silver' | 'gold',
    limit: number = 25,
    offset: number = 0
  ): Promise<any[]> => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    const { data } = await api.get(`/pipeline/batches/${batchId}/records/${layer}?${params}`);
    return data;
  },

  // Get full record details
  getRecordDetails: async (
    layer: 'bronze' | 'silver' | 'gold',
    recordId: string
  ): Promise<any> => {
    const { data } = await api.get(`/pipeline/records/${layer}/${recordId}`);
    return data;
  },

  // Get cross-zone record lineage
  getRecordLineage: async (
    layer: 'bronze' | 'silver' | 'gold',
    recordId: string
  ): Promise<{
    bronze: any;
    silver: any;
    gold: any;
    bronze_parsed?: Record<string, any>;  // Extractor-parsed Bronze fields
    bronze_silver_equivalent?: Record<string, any>;  // Bronze parsed as Silver fields
    gold_entities?: {
      debtor_party?: Record<string, any>;
      debtor_account?: Record<string, any>;
      debtor_agent?: Record<string, any>;
      creditor_party?: Record<string, any>;
      creditor_account?: Record<string, any>;
      creditor_agent?: Record<string, any>;
      intermediary_agent1?: Record<string, any>;
      intermediary_agent2?: Record<string, any>;
      ultimate_debtor?: Record<string, any>;
      ultimate_creditor?: Record<string, any>;
    };
    gold_extension?: Record<string, any>;  // Format-specific extension data
    field_mappings: any[];
  }> => {
    const { data } = await api.get(`/pipeline/records/${layer}/${recordId}/lineage`);
    return data;
  },

  // Pipeline Overview
  getOverview: async (): Promise<any> => {
    const { data } = await api.get('/pipeline/overview');
    return data;
  },

  // NiFi Status
  getNifiStatus: async (): Promise<any> => {
    const { data } = await api.get('/pipeline/nifi/status');
    return data;
  },

  getNifiConnections: async (): Promise<any> => {
    const { data } = await api.get('/pipeline/nifi/connections');
    return data;
  },

  // Celery/Flower Status
  getCeleryWorkers: async (): Promise<any> => {
    const { data } = await api.get('/pipeline/celery/workers');
    return data;
  },

  getCeleryTasks: async (state?: string, limit: number = 50): Promise<any> => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (state) params.append('state', state);
    const { data } = await api.get(`/pipeline/celery/tasks?${params}`);
    return data;
  },

  getCeleryQueues: async (): Promise<any> => {
    const { data } = await api.get('/pipeline/celery/queues');
    return data;
  },

  // Message Type Stats
  getMessageTypeStats: async (hoursBack: number = 24): Promise<any> => {
    const { data } = await api.get(`/pipeline/message-types/stats?hours_back=${hoursBack}`);
    return data;
  },

  getMessageTypeFlow: async (messageType: string, hoursBack: number = 24): Promise<any> => {
    const { data } = await api.get(`/pipeline/message-types/${messageType}/flow?hours_back=${hoursBack}`);
    return data;
  },

  // Throughput
  getThroughput: async (hoursBack: number = 24, intervalMinutes: number = 60): Promise<any> => {
    const { data } = await api.get(`/pipeline/throughput?hours_back=${hoursBack}&interval_minutes=${intervalMinutes}`);
    return data;
  },

  // Field Mappings - get Bronze→Silver→Gold mappings from database
  getFieldMappings: async (messageType: string): Promise<{
    message_type: string;
    bronze_to_silver: {
      silver_column: string;
      bronze_path: string;
      data_type: string;
      is_required: boolean;
      default_value: string | null;
    }[];
    silver_to_gold: {
      gold_table: string;
      gold_column: string;
      silver_column: string;
      entity_role: string | null;
      data_type: string;
      is_required: boolean;
      default_value: string | null;
    }[];
  }> => {
    const { data } = await api.get(`/pipeline/mappings/${messageType}`);
    return data;
  },
};

// =====================
// Graph API (Neo4j Knowledge Graph)
// =====================
export const graphApi = {
  getBatchLineage: async (batchId: string): Promise<any> => {
    const { data } = await api.get(`/graph/batches/${batchId}/lineage`);
    return data;
  },

  getSchemaLineage: async (messageType: string): Promise<any> => {
    const { data } = await api.get(`/graph/schema/${messageType}`);
    return data;
  },

  getFieldLineage: async (messageType: string, fieldName: string): Promise<any> => {
    const { data } = await api.get(`/graph/schema/${messageType}/field/${fieldName}`);
    return data;
  },

  getBottlenecks: async (hoursBack: number = 24): Promise<any[]> => {
    const { data } = await api.get(`/graph/bottlenecks?hours_back=${hoursBack}`);
    return data;
  },

  getDQTrends: async (messageType: string, daysBack: number = 7): Promise<any[]> => {
    const { data } = await api.get(`/graph/dq-trends?message_type=${messageType}&days_back=${daysBack}`);
    return data;
  },

  triggerSync: async (): Promise<any> => {
    const { data } = await api.post('/graph/sync/trigger');
    return data;
  },

  getHealth: async (): Promise<any> => {
    const { data } = await api.get('/graph/health');
    return data;
  },
};

// =====================
// Schema API
// =====================
export const schemaApi = {
  getMessageTypes: async (): Promise<any[]> => {
    const { data } = await api.get('/schema/message-types');
    return data;
  },

  getMessageTypeSchema: async (messageType: string): Promise<any> => {
    const { data } = await api.get(`/schema/message-types/${messageType}`);
    return data;
  },

  getTableDisplayConfig: async (
    layer: string,
    tableName: string,
    messageType?: string
  ): Promise<any> => {
    const params = messageType ? `?message_type=${messageType}` : '';
    const { data } = await api.get(`/schema/tables/${layer}/${tableName}${params}`);
    return data;
  },

  getFieldLineage: async (messageType: string, fieldName: string): Promise<any> => {
    const { data } = await api.get(`/schema/field-lineage/${messageType}/${fieldName}`);
    return data;
  },

  getValidations: async (messageType: string): Promise<any> => {
    const { data } = await api.get(`/schema/validations/${messageType}`);
    return data;
  },
};

// =====================
// Processing Errors API
// =====================
export interface ProcessingError {
  error_id: string;
  batch_id: string;
  chunk_index?: number;
  total_chunks?: number;
  zone: 'BRONZE' | 'SILVER' | 'GOLD';
  raw_id?: string;
  stg_id?: string;
  content_hash?: string;
  message_type: string;
  message_id?: string;
  error_code?: string;
  error_message: string;
  error_stack_trace?: string;
  original_content?: string;
  status: 'PENDING' | 'RETRYING' | 'RESOLVED' | 'SKIPPED' | 'ABANDONED';
  retry_count: number;
  max_retries: number;
  last_retry_at?: string;
  next_retry_at?: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ErrorListResponse {
  items: ProcessingError[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ErrorStats {
  total_errors: number;
  by_zone: Record<string, number>;
  by_status: Record<string, number>;
  by_message_type: Record<string, number>;
  by_error_code: Record<string, number>;
  pending_count: number;
  retrying_count: number;
  resolved_count: number;
  abandoned_count: number;
  avg_retry_count: number;
  errors_last_hour: number;
  errors_last_24h: number;
  oldest_pending?: string;
  newest_error?: string;
}

export interface ErrorTrend {
  timestamps: string[];
  counts: number[];
  by_zone: Record<string, number[]>;
}

export interface ErrorCode {
  error_code: string;
  error_category: string;
  description?: string;
  is_retryable: boolean;
  suggested_action?: string;
}

export interface BulkActionResponse {
  action: string;
  requested_count: number;
  success_count: number;
  failed_ids: string[];
}

export const errorsApi = {
  getErrors: async (filters: {
    zone?: string;
    status?: string;
    message_type?: string;
    error_code?: string;
    batch_id?: string;
    date_from?: string;
    date_to?: string;
    search?: string;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_desc?: boolean;
  }): Promise<ErrorListResponse> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });
    const { data } = await api.get(`/errors?${params}`);
    return data;
  },

  getError: async (errorId: string): Promise<ProcessingError> => {
    const { data } = await api.get(`/errors/${errorId}`);
    return data;
  },

  getErrorHistory: async (errorId: string): Promise<any[]> => {
    const { data } = await api.get(`/errors/${errorId}/history`);
    return data;
  },

  getStats: async (zone?: string, hoursBack: number = 24): Promise<ErrorStats> => {
    const params = new URLSearchParams({ hours_back: hoursBack.toString() });
    if (zone) params.append('zone', zone);
    const { data } = await api.get(`/errors/stats?${params}`);
    return data;
  },

  getTrend: async (hoursBack: number = 24, intervalMinutes: number = 60): Promise<ErrorTrend> => {
    const { data } = await api.get(`/errors/trend?hours_back=${hoursBack}&interval_minutes=${intervalMinutes}`);
    return data;
  },

  retryError: async (errorId: string, delayMinutes: number = 5): Promise<any> => {
    const { data } = await api.post(`/errors/${errorId}/retry`, { delay_minutes: delayMinutes });
    return data;
  },

  skipError: async (errorId: string, reason: string): Promise<any> => {
    const { data } = await api.post(`/errors/${errorId}/skip`, { reason });
    return data;
  },

  resolveError: async (errorId: string, notes: string, resolvedBy: string): Promise<any> => {
    const { data } = await api.post(`/errors/${errorId}/resolve`, {
      resolution_notes: notes,
      resolved_by: resolvedBy,
    });
    return data;
  },

  abandonError: async (errorId: string, reason: string): Promise<any> => {
    const { data } = await api.post(`/errors/${errorId}/abandon`, { reason });
    return data;
  },

  bulkAction: async (
    errorIds: string[],
    action: 'retry' | 'skip' | 'resolve' | 'abandon',
    notes?: string,
    resolvedBy?: string
  ): Promise<BulkActionResponse> => {
    const { data } = await api.post('/errors/bulk', {
      error_ids: errorIds,
      action,
      notes,
      resolved_by: resolvedBy,
    });
    return data;
  },

  retryAllPending: async (
    zone?: string,
    messageType?: string,
    maxCount: number = 100
  ): Promise<any> => {
    const params = new URLSearchParams({ max_count: maxCount.toString() });
    if (zone) params.append('zone', zone);
    if (messageType) params.append('message_type', messageType);
    const { data } = await api.post(`/errors/bulk/retry-all-pending?${params}`);
    return data;
  },

  getErrorCodes: async (): Promise<ErrorCode[]> => {
    const { data } = await api.get('/errors/codes/list');
    return data;
  },

  getErrorCode: async (errorCode: string): Promise<ErrorCode> => {
    const { data } = await api.get(`/errors/codes/${errorCode}`);
    return data;
  },
};

// =====================
// Mappings Documentation API
// =====================
export interface MessageFormatSummary {
  format_id: string;
  format_name: string;
  format_category: string;
  standard_name: string | null;
  country: string | null;
  governing_body: string | null;
  bronze_table: string;
  silver_table: string;
  total_standard_fields: number;
  mapped_to_silver: number;
  mapped_to_gold: number;
  silver_coverage_pct: number | null;
  gold_coverage_pct: number | null;
  unmapped_fields: number;
  is_active: boolean;
}

export interface StandardField {
  standard_field_id: number;
  format_id: string;
  field_name: string;
  field_path: string;
  field_tag: string | null;
  field_description: string | null;
  data_type: string;
  min_length: number | null;
  max_length: number | null;
  allowed_values: string | null;
  is_mandatory: boolean;
  field_category: string | null;
  is_active: boolean;
}

export interface MappingDocumentationRow {
  // Standard/Format Info
  standard_name: string | null;
  country: string | null;
  message_format: string;
  message_format_description: string;
  format_category: string;

  // Standard Field Info
  standard_field_id: number | null;
  standard_field_name: string | null;
  standard_field_description: string | null;
  standard_field_data_type: string | null;
  standard_field_allowed_values: string | null;
  standard_field_path: string | null;
  standard_field_tag: string | null;
  standard_field_mandatory: boolean | null;
  field_category: string | null;

  // Bronze Info
  bronze_table: string | null;
  bronze_column: string | null;

  // Silver Mapping Info
  silver_mapping_id: number | null;
  silver_table: string | null;
  silver_column: string | null;
  silver_data_type: string | null;
  silver_max_length: number | null;
  silver_source_path: string | null;
  silver_transform: string | null;
  is_mapped_to_silver: boolean;

  // Gold Mapping Info
  gold_mapping_id: number | null;
  gold_table: string | null;
  gold_column: string | null;
  gold_data_type: string | null;
  gold_entity_role: string | null;
  gold_purpose_code: string | null;
  gold_source_expression: string | null;
  is_mapped_to_gold: boolean;

  // Metadata
  is_active: boolean | null;
  last_updated: string | null;
}

export interface CoverageStats {
  format_id: string;
  format_name: string;
  total_standard_fields: number;
  mandatory_fields: number;
  mapped_to_silver: number;
  mapped_to_gold: number;
  silver_coverage_pct: number | null;
  gold_coverage_pct: number | null;
  unmapped_fields: number;
}

export interface UnmappedField {
  format_id: string;
  format_name: string;
  field_name: string;
  field_path: string;
  field_description: string | null;
  data_type: string | null;
  is_mandatory: boolean | null;
  field_category: string | null;
  gap_type: string;
}

export interface SilverMapping {
  mapping_id: number;
  format_id: string;
  target_column: string;
  source_path: string;
  data_type: string;
  max_length: number | null;
  is_required: boolean;
  default_value: string | null;
  transform_function: string | null;
  transform_expression: string | null;
  ordinal_position: number;
  standard_field_id: number | null;
  field_description: string | null;
  is_user_modified: boolean;
  is_active: boolean;
}

export interface GoldMapping {
  mapping_id: number;
  format_id: string;
  gold_table: string;
  gold_column: string;
  source_expression: string;
  entity_role: string | null;
  data_type: string;
  is_required: boolean;
  default_value: string | null;
  transform_expression: string | null;
  ordinal_position: number;
  purpose_code: string | null;
  field_description: string | null;
  is_user_modified: boolean;
  is_active: boolean;
}

export interface FieldCategory {
  field_category: string;
  field_count: number;
}

export const mappingsApi = {
  // Message Formats
  getFormats: async (filters?: {
    category?: string;
    country?: string;
    active_only?: boolean;
  }): Promise<MessageFormatSummary[]> => {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.country) params.append('country', filters.country);
    if (filters?.active_only !== undefined) params.append('active_only', filters.active_only.toString());
    const { data } = await api.get(`/mappings/formats?${params}`);
    return data;
  },

  getFormat: async (formatId: string): Promise<MessageFormatSummary> => {
    const { data } = await api.get(`/mappings/formats/${formatId}`);
    return data;
  },

  // Mappings Documentation
  getDocumentation: async (
    formatId: string,
    filters?: {
      field_category?: string;
      mapped_only?: boolean;
      unmapped_only?: boolean;
    }
  ): Promise<MappingDocumentationRow[]> => {
    const params = new URLSearchParams();
    if (filters?.field_category) params.append('field_category', filters.field_category);
    if (filters?.mapped_only) params.append('mapped_only', 'true');
    if (filters?.unmapped_only) params.append('unmapped_only', 'true');
    const { data } = await api.get(`/mappings/documentation/${formatId}?${params}`);
    return data;
  },

  getCoverage: async (formatId?: string): Promise<CoverageStats[]> => {
    const params = formatId ? `?format_id=${formatId}` : '';
    const { data } = await api.get(`/mappings/coverage${params}`);
    return data;
  },

  getUnmapped: async (filters?: {
    format_id?: string;
    gap_type?: string;
    mandatory_only?: boolean;
  }): Promise<UnmappedField[]> => {
    const params = new URLSearchParams();
    if (filters?.format_id) params.append('format_id', filters.format_id);
    if (filters?.gap_type) params.append('gap_type', filters.gap_type);
    if (filters?.mandatory_only) params.append('mandatory_only', 'true');
    const { data } = await api.get(`/mappings/unmapped?${params}`);
    return data;
  },

  // Field Categories
  getFieldCategories: async (formatId: string): Promise<FieldCategory[]> => {
    const { data } = await api.get(`/mappings/field-categories/${formatId}`);
    return data;
  },

  // Standard Fields CRUD
  getStandardFields: async (
    formatId: string,
    filters?: { category?: string; active_only?: boolean }
  ): Promise<StandardField[]> => {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.active_only !== undefined) params.append('active_only', filters.active_only.toString());
    const { data } = await api.get(`/mappings/standard-fields/${formatId}?${params}`);
    return data;
  },

  createStandardField: async (field: Omit<StandardField, 'standard_field_id' | 'is_active'>): Promise<StandardField> => {
    const { data } = await api.post('/mappings/standard-fields', field);
    return data;
  },

  updateStandardField: async (
    fieldId: number,
    updates: Partial<StandardField>,
    updatedBy?: string
  ): Promise<StandardField> => {
    const params = updatedBy ? `?updated_by=${updatedBy}` : '';
    const { data } = await api.put(`/mappings/standard-fields/${fieldId}${params}`, updates);
    return data;
  },

  deleteStandardField: async (fieldId: number, softDelete = true): Promise<void> => {
    await api.delete(`/mappings/standard-fields/${fieldId}?soft_delete=${softDelete}`);
  },

  // Silver Mappings CRUD
  getSilverMappings: async (formatId: string, activeOnly = true): Promise<SilverMapping[]> => {
    const { data } = await api.get(`/mappings/silver-mappings/${formatId}?active_only=${activeOnly}`);
    return data;
  },

  createSilverMapping: async (mapping: Omit<SilverMapping, 'mapping_id' | 'is_user_modified' | 'is_active'>): Promise<SilverMapping> => {
    const { data } = await api.post('/mappings/silver-mappings', mapping);
    return data;
  },

  updateSilverMapping: async (
    mappingId: number,
    updates: Partial<SilverMapping>,
    updatedBy?: string
  ): Promise<SilverMapping> => {
    const params = updatedBy ? `?updated_by=${updatedBy}` : '';
    const { data } = await api.put(`/mappings/silver-mappings/${mappingId}${params}`, updates);
    return data;
  },

  deleteSilverMapping: async (mappingId: number, softDelete = true): Promise<void> => {
    await api.delete(`/mappings/silver-mappings/${mappingId}?soft_delete=${softDelete}`);
  },

  // Gold Mappings CRUD
  getGoldMappings: async (
    formatId: string,
    filters?: { gold_table?: string; entity_role?: string; active_only?: boolean }
  ): Promise<GoldMapping[]> => {
    const params = new URLSearchParams();
    if (filters?.gold_table) params.append('gold_table', filters.gold_table);
    if (filters?.entity_role) params.append('entity_role', filters.entity_role);
    if (filters?.active_only !== undefined) params.append('active_only', filters.active_only.toString());
    const { data } = await api.get(`/mappings/gold-mappings/${formatId}?${params}`);
    return data;
  },

  createGoldMapping: async (mapping: Omit<GoldMapping, 'mapping_id' | 'is_user_modified' | 'is_active'>): Promise<GoldMapping> => {
    const { data } = await api.post('/mappings/gold-mappings', mapping);
    return data;
  },

  updateGoldMapping: async (
    mappingId: number,
    updates: Partial<GoldMapping>,
    updatedBy?: string
  ): Promise<GoldMapping> => {
    const params = updatedBy ? `?updated_by=${updatedBy}` : '';
    const { data } = await api.put(`/mappings/gold-mappings/${mappingId}${params}`, updates);
    return data;
  },

  deleteGoldMapping: async (mappingId: number, softDelete = true): Promise<void> => {
    await api.delete(`/mappings/gold-mappings/${mappingId}?soft_delete=${softDelete}`);
  },

  // Export
  exportMappings: async (formatId: string, formatType: 'json' | 'csv' = 'json'): Promise<{
    format: string;
    data: MappingDocumentationRow[] | string;
    row_count: number;
  }> => {
    const { data } = await api.get(`/mappings/export/${formatId}?format_type=${formatType}`);
    return data;
  },
};

export default api;
