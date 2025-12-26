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

export default api;
