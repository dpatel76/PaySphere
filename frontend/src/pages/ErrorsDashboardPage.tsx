/**
 * GPS CDM - Processing Errors Dashboard
 *
 * Admin dashboard for managing processing errors across Bronze, Silver, and Gold zones.
 * Supports filtering, bulk actions, retry scheduling, and analytics.
 * Real-time updates via WebSocket.
 */
import React, { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { useWebSocket } from '../hooks/useWebSocket';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  IconButton,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Collapse,
  Tooltip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Replay as RetryIcon,
  CheckCircle as ResolveIcon,
  Cancel as SkipIcon,
  Delete as AbandonIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Timeline as TrendIcon,
  Circle as CircleIcon,
} from '@mui/icons-material';
import {
  errorsApi,
  ProcessingError,
  ErrorStats,
  ErrorTrend,
} from '../api/client';

// Zone colors
const ZONE_COLORS: Record<string, string> = {
  BRONZE: '#cd7f32',
  SILVER: '#c0c0c0',
  GOLD: '#ffd700',
};

// Status colors
const STATUS_COLORS: Record<string, 'error' | 'warning' | 'info' | 'success' | 'default'> = {
  PENDING: 'warning',
  RETRYING: 'info',
  RESOLVED: 'success',
  SKIPPED: 'default',
  ABANDONED: 'error',
};

// Stats Card Component
const StatsCard: React.FC<{
  title: string;
  value: number | string;
  color?: string;
  icon?: React.ReactNode;
  subtitle?: string;
}> = ({ title, value, color, icon, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography variant="caption" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h4" sx={{ color: color || 'text.primary' }}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        {icon && <Box sx={{ opacity: 0.3 }}>{icon}</Box>}
      </Box>
    </CardContent>
  </Card>
);

// Error Detail Dialog
const ErrorDetailDialog: React.FC<{
  error: ProcessingError | null;
  open: boolean;
  onClose: () => void;
  onRetry: (errorId: string) => void;
  onResolve: (errorId: string, notes: string) => void;
  onSkip: (errorId: string, reason: string) => void;
}> = ({ error, open, onClose, onRetry, onResolve, onSkip }) => {
  const [resolveNotes, setResolveNotes] = useState('');
  const [skipReason, setSkipReason] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  const { data: history } = useQuery({
    queryKey: ['errorHistory', error?.error_id],
    queryFn: () => errorsApi.getErrorHistory(error!.error_id),
    enabled: !!error && activeTab === 2,
  });

  if (!error) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <ErrorIcon color="error" />
          <Typography variant="h6">Error Details</Typography>
          <Chip
            label={error.zone}
            size="small"
            sx={{ bgcolor: ZONE_COLORS[error.zone], color: 'white' }}
          />
          <Chip
            label={error.status}
            size="small"
            color={STATUS_COLORS[error.status]}
          />
        </Box>
      </DialogTitle>
      <DialogContent dividers>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
          <Tab label="Details" />
          <Tab label="Stack Trace" />
          <Tab label="History" />
          <Tab label="Original Content" />
        </Tabs>

        {activeTab === 0 && (
          <Grid container spacing={2}>
            <Grid size={6}>
              <Typography variant="subtitle2" color="text.secondary">Error ID</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{error.error_id}</Typography>
            </Grid>
            <Grid size={6}>
              <Typography variant="subtitle2" color="text.secondary">Batch ID</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{error.batch_id}</Typography>
            </Grid>
            <Grid size={6}>
              <Typography variant="subtitle2" color="text.secondary">Message Type</Typography>
              <Typography variant="body2">{error.message_type}</Typography>
            </Grid>
            <Grid size={6}>
              <Typography variant="subtitle2" color="text.secondary">Error Code</Typography>
              <Chip label={error.error_code || 'UNKNOWN'} size="small" />
            </Grid>
            <Grid size={12}>
              <Typography variant="subtitle2" color="text.secondary">Error Message</Typography>
              <Paper sx={{ p: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
                <Typography variant="body2">{error.error_message}</Typography>
              </Paper>
            </Grid>
            <Grid size={4}>
              <Typography variant="subtitle2" color="text.secondary">Retry Count</Typography>
              <Typography variant="body2">{error.retry_count} / {error.max_retries}</Typography>
            </Grid>
            <Grid size={4}>
              <Typography variant="subtitle2" color="text.secondary">Created At</Typography>
              <Typography variant="body2">{new Date(error.created_at).toLocaleString()}</Typography>
            </Grid>
            <Grid size={4}>
              <Typography variant="subtitle2" color="text.secondary">Last Retry</Typography>
              <Typography variant="body2">
                {error.last_retry_at ? new Date(error.last_retry_at).toLocaleString() : 'Never'}
              </Typography>
            </Grid>
            {error.raw_id && (
              <Grid size={6}>
                <Typography variant="subtitle2" color="text.secondary">Raw ID (Bronze)</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{error.raw_id}</Typography>
              </Grid>
            )}
            {error.stg_id && (
              <Grid size={6}>
                <Typography variant="subtitle2" color="text.secondary">Stg ID (Silver)</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>{error.stg_id}</Typography>
              </Grid>
            )}
          </Grid>
        )}

        {activeTab === 1 && (
          <Paper sx={{ p: 2, bgcolor: 'grey.900', maxHeight: 400, overflow: 'auto' }}>
            <Typography
              variant="body2"
              component="pre"
              sx={{ fontFamily: 'monospace', color: 'grey.300', whiteSpace: 'pre-wrap' }}
            >
              {error.error_stack_trace || 'No stack trace available'}
            </Typography>
          </Paper>
        )}

        {activeTab === 2 && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Action</TableCell>
                  <TableCell>Previous Status</TableCell>
                  <TableCell>New Status</TableCell>
                  <TableCell>By</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Notes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {history?.map((h: any) => (
                  <TableRow key={h.history_id}>
                    <TableCell>{h.action}</TableCell>
                    <TableCell>{h.previous_status}</TableCell>
                    <TableCell>{h.new_status}</TableCell>
                    <TableCell>{h.action_by || 'SYSTEM'}</TableCell>
                    <TableCell>{new Date(h.created_at).toLocaleString()}</TableCell>
                    <TableCell>{h.action_notes}</TableCell>
                  </TableRow>
                ))}
                {(!history || history.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">No history available</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {activeTab === 3 && (
          <Paper sx={{ p: 2, bgcolor: 'grey.100', maxHeight: 400, overflow: 'auto' }}>
            <Typography
              variant="body2"
              component="pre"
              sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}
            >
              {error.original_content
                ? JSON.stringify(JSON.parse(error.original_content), null, 2)
                : 'No original content available'}
            </Typography>
          </Paper>
        )}

        {error.status === 'PENDING' || error.status === 'RETRYING' ? (
          <Box sx={{ mt: 3 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle1" gutterBottom>Actions</Typography>
            <Grid container spacing={2}>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Resolution Notes (for Resolve)"
                  value={resolveNotes}
                  onChange={(e) => setResolveNotes(e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Skip Reason"
                  value={skipReason}
                  onChange={(e) => setSkipReason(e.target.value)}
                  size="small"
                />
              </Grid>
            </Grid>
          </Box>
        ) : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        {(error.status === 'PENDING' || error.status === 'RETRYING') && (
          <>
            <Button
              startIcon={<RetryIcon />}
              onClick={() => onRetry(error.error_id)}
              disabled={error.retry_count >= error.max_retries}
            >
              Retry
            </Button>
            <Button
              startIcon={<SkipIcon />}
              onClick={() => onSkip(error.error_id, skipReason || 'Skipped by user')}
              color="warning"
            >
              Skip
            </Button>
            <Button
              startIcon={<ResolveIcon />}
              onClick={() => onResolve(error.error_id, resolveNotes || 'Manually resolved')}
              color="success"
            >
              Resolve
            </Button>
          </>
        )}
      </DialogActions>
    </Dialog>
  );
};

// Main Component
const ErrorsDashboardPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  // State
  const [filters, setFilters] = useState({
    zone: '',
    status: '',
    message_type: '',
    error_code: '',
    search: '',
    page: 1,
    page_size: 25,
  });
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [selectedError, setSelectedError] = useState<ProcessingError | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // WebSocket for real-time updates
  const { stats: wsStats, isConnected, lastUpdate, error: wsError } = useWebSocket({
    autoConnect: true,
    onMessage: (message) => {
      // Invalidate queries when we receive WebSocket updates
      if (message.type === 'stats_update') {
        queryClient.invalidateQueries({ queryKey: ['errorStats'] });
        // Only refetch errors list if there are new pending errors
        if (message.data.errors?.recent_5min > 0) {
          queryClient.invalidateQueries({ queryKey: ['errors'] });
        }
      }
    },
  });

  // Queries
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['errorStats'],
    queryFn: () => errorsApi.getStats(),
    refetchInterval: isConnected ? 60000 : 30000, // Slower polling when WebSocket connected
  });

  const { data: errorsData, isLoading: errorsLoading, refetch } = useQuery({
    queryKey: ['errors', filters],
    queryFn: () => errorsApi.getErrors(filters),
    refetchInterval: 30000,
  });

  const { data: trend } = useQuery({
    queryKey: ['errorTrend'],
    queryFn: () => errorsApi.getTrend(24, 60),
  });

  // Mutations
  const retryMutation = useMutation({
    mutationFn: (errorId: string) => errorsApi.retryError(errorId),
    onSuccess: () => {
      enqueueSnackbar('Error scheduled for retry', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['errors'] });
      queryClient.invalidateQueries({ queryKey: ['errorStats'] });
    },
    onError: () => enqueueSnackbar('Failed to schedule retry', { variant: 'error' }),
  });

  const resolveMutation = useMutation({
    mutationFn: ({ errorId, notes }: { errorId: string; notes: string }) =>
      errorsApi.resolveError(errorId, notes, 'admin'),
    onSuccess: () => {
      enqueueSnackbar('Error marked as resolved', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['errors'] });
      queryClient.invalidateQueries({ queryKey: ['errorStats'] });
      setSelectedError(null);
    },
    onError: () => enqueueSnackbar('Failed to resolve error', { variant: 'error' }),
  });

  const skipMutation = useMutation({
    mutationFn: ({ errorId, reason }: { errorId: string; reason: string }) =>
      errorsApi.skipError(errorId, reason),
    onSuccess: () => {
      enqueueSnackbar('Error skipped', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['errors'] });
      queryClient.invalidateQueries({ queryKey: ['errorStats'] });
      setSelectedError(null);
    },
    onError: () => enqueueSnackbar('Failed to skip error', { variant: 'error' }),
  });

  const bulkMutation = useMutation({
    mutationFn: ({ action, ids }: { action: 'retry' | 'skip' | 'resolve' | 'abandon'; ids: string[] }) =>
      errorsApi.bulkAction(ids, action, 'Bulk action'),
    onSuccess: (data) => {
      enqueueSnackbar(`${data.success_count} errors ${data.action}ed`, { variant: 'success' });
      setSelectedIds([]);
      queryClient.invalidateQueries({ queryKey: ['errors'] });
      queryClient.invalidateQueries({ queryKey: ['errorStats'] });
    },
    onError: () => enqueueSnackbar('Bulk action failed', { variant: 'error' }),
  });

  // Handlers
  const handleSelectAll = useCallback((checked: boolean) => {
    if (checked && errorsData?.items) {
      setSelectedIds(errorsData.items.map((e) => e.error_id));
    } else {
      setSelectedIds([]);
    }
  }, [errorsData]);

  const handleSelect = useCallback((errorId: string, checked: boolean) => {
    if (checked) {
      setSelectedIds((prev) => [...prev, errorId]);
    } else {
      setSelectedIds((prev) => prev.filter((id) => id !== errorId));
    }
  }, []);

  const handlePageChange = (_: unknown, newPage: number) => {
    setFilters((prev) => ({ ...prev, page: newPage + 1 }));
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters((prev) => ({ ...prev, page_size: parseInt(event.target.value, 10), page: 1 }));
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="h4">Processing Errors Dashboard</Typography>
          {/* WebSocket Status Indicator */}
          <Tooltip title={isConnected ? `Live updates active${lastUpdate ? ` - Last update: ${lastUpdate.toLocaleTimeString()}` : ''}` : wsError || 'Connecting...'}>
            <Chip
              icon={<CircleIcon sx={{ fontSize: 12, color: isConnected ? 'success.main' : 'warning.main' }} />}
              label={isConnected ? 'Live' : 'Connecting'}
              size="small"
              variant="outlined"
              color={isConnected ? 'success' : 'warning'}
            />
          </Tooltip>
          {/* Real-time pending count from WebSocket */}
          {wsStats && (
            <Chip
              label={`${wsStats.errors.total_pending} pending (live)`}
              size="small"
              color={wsStats.errors.total_pending > 0 ? 'warning' : 'success'}
            />
          )}
        </Box>
        <Box>
          <IconButton onClick={() => refetch()}>
            <RefreshIcon />
          </IconButton>
          <Button
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
            variant={showFilters ? 'contained' : 'outlined'}
            size="small"
            sx={{ ml: 1 }}
          >
            Filters
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      {statsLoading ? (
        <LinearProgress sx={{ mb: 3 }} />
      ) : stats ? (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <StatsCard
              title="Total Errors"
              value={stats.total_errors}
              icon={<ErrorIcon sx={{ fontSize: 40 }} />}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <StatsCard
              title="Pending"
              value={stats.pending_count}
              color="orange"
              icon={<WarningIcon sx={{ fontSize: 40 }} />}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <StatsCard
              title="Retrying"
              value={stats.retrying_count}
              color="blue"
              icon={<RetryIcon sx={{ fontSize: 40 }} />}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <StatsCard
              title="Resolved"
              value={stats.resolved_count}
              color="green"
              icon={<ResolveIcon sx={{ fontSize: 40 }} />}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <StatsCard
              title="Last Hour"
              value={stats.errors_last_hour}
              subtitle="New errors"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 2 }}>
            <StatsCard
              title="Last 24h"
              value={stats.errors_last_24h}
              subtitle="Total errors"
            />
          </Grid>
        </Grid>
      ) : null}

      {/* Zone Breakdown */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {['BRONZE', 'SILVER', 'GOLD'].map((zone) => (
            <Grid size={4} key={zone}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Chip
                    label={zone}
                    sx={{ bgcolor: ZONE_COLORS[zone], color: 'white', mb: 1 }}
                  />
                  <Typography variant="h5">{stats.by_zone[zone] || 0}</Typography>
                  <Typography variant="caption" color="text.secondary">errors</Typography>
                  {/* Real-time throughput from WebSocket */}
                  {wsStats && (
                    <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
                      {zone === 'BRONZE' && `${wsStats.throughput.bronze_last_hour} records/hr`}
                      {zone === 'SILVER' && `${wsStats.throughput.silver_last_hour} records/hr`}
                      {zone === 'GOLD' && `${wsStats.throughput.gold_last_hour} records/hr`}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Filters */}
      <Collapse in={showFilters}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <FormControl fullWidth size="small">
                <InputLabel>Zone</InputLabel>
                <Select
                  value={filters.zone}
                  label="Zone"
                  onChange={(e) => setFilters((prev) => ({ ...prev, zone: e.target.value, page: 1 }))}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="BRONZE">Bronze</MenuItem>
                  <MenuItem value="SILVER">Silver</MenuItem>
                  <MenuItem value="GOLD">Gold</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  label="Status"
                  onChange={(e) => setFilters((prev) => ({ ...prev, status: e.target.value, page: 1 }))}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="PENDING">Pending</MenuItem>
                  <MenuItem value="RETRYING">Retrying</MenuItem>
                  <MenuItem value="RESOLVED">Resolved</MenuItem>
                  <MenuItem value="SKIPPED">Skipped</MenuItem>
                  <MenuItem value="ABANDONED">Abandoned</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 2 }}>
              <TextField
                fullWidth
                size="small"
                label="Message Type"
                value={filters.message_type}
                onChange={(e) => setFilters((prev) => ({ ...prev, message_type: e.target.value, page: 1 }))}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                size="small"
                label="Search"
                placeholder="Search error messages..."
                value={filters.search}
                onChange={(e) => setFilters((prev) => ({ ...prev, search: e.target.value, page: 1 }))}
                InputProps={{ startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} /> }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Button
                variant="outlined"
                onClick={() => setFilters({
                  zone: '',
                  status: '',
                  message_type: '',
                  error_code: '',
                  search: '',
                  page: 1,
                  page_size: 25,
                })}
                fullWidth
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Collapse>

      {/* Bulk Actions */}
      {selectedIds.length > 0 && (
        <Alert
          severity="info"
          sx={{ mb: 2 }}
          action={
            <Box>
              <Button
                size="small"
                startIcon={<RetryIcon />}
                onClick={() => bulkMutation.mutate({ action: 'retry', ids: selectedIds })}
                disabled={bulkMutation.isPending}
              >
                Retry All
              </Button>
              <Button
                size="small"
                startIcon={<SkipIcon />}
                onClick={() => bulkMutation.mutate({ action: 'skip', ids: selectedIds })}
                disabled={bulkMutation.isPending}
                sx={{ ml: 1 }}
              >
                Skip All
              </Button>
              <Button
                size="small"
                startIcon={<ResolveIcon />}
                onClick={() => bulkMutation.mutate({ action: 'resolve', ids: selectedIds })}
                disabled={bulkMutation.isPending}
                sx={{ ml: 1 }}
              >
                Resolve All
              </Button>
            </Box>
          }
        >
          {selectedIds.length} error(s) selected
        </Alert>
      )}

      {/* Errors Table */}
      <Paper>
        {errorsLoading && <LinearProgress />}
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedIds.length > 0 && selectedIds.length === errorsData?.items?.length}
                    indeterminate={selectedIds.length > 0 && selectedIds.length < (errorsData?.items?.length || 0)}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                </TableCell>
                <TableCell>Zone</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Message Type</TableCell>
                <TableCell>Error Code</TableCell>
                <TableCell>Error Message</TableCell>
                <TableCell>Retries</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {errorsData?.items?.map((error) => (
                <TableRow
                  key={error.error_id}
                  hover
                  selected={selectedIds.includes(error.error_id)}
                  sx={{ cursor: 'pointer' }}
                  onClick={() => setSelectedError(error)}
                >
                  <TableCell padding="checkbox" onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedIds.includes(error.error_id)}
                      onChange={(e) => handleSelect(error.error_id, e.target.checked)}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={error.zone}
                      size="small"
                      sx={{ bgcolor: ZONE_COLORS[error.zone], color: 'white' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={error.status}
                      size="small"
                      color={STATUS_COLORS[error.status]}
                    />
                  </TableCell>
                  <TableCell>{error.message_type}</TableCell>
                  <TableCell>
                    <Chip label={error.error_code || 'UNKNOWN'} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell sx={{ maxWidth: 300 }}>
                    <Tooltip title={error.error_message}>
                      <Typography variant="body2" noWrap>
                        {error.error_message}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    {error.retry_count} / {error.max_retries}
                  </TableCell>
                  <TableCell>
                    {new Date(error.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    {(error.status === 'PENDING' || error.status === 'RETRYING') && (
                      <>
                        <Tooltip title="Retry">
                          <IconButton
                            size="small"
                            onClick={() => retryMutation.mutate(error.error_id)}
                            disabled={error.retry_count >= error.max_retries}
                          >
                            <RetryIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Skip">
                          <IconButton
                            size="small"
                            onClick={() => skipMutation.mutate({
                              errorId: error.error_id,
                              reason: 'Skipped from table view',
                            })}
                          >
                            <SkipIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {errorsData?.items?.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <InfoIcon sx={{ fontSize: 40, opacity: 0.3 }} />
                    <Typography color="text.secondary">No errors found</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={errorsData?.total || 0}
          page={(errorsData?.page || 1) - 1}
          rowsPerPage={errorsData?.page_size || 25}
          rowsPerPageOptions={[10, 25, 50, 100]}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
        />
      </Paper>

      {/* Error Detail Dialog */}
      <ErrorDetailDialog
        error={selectedError}
        open={!!selectedError}
        onClose={() => setSelectedError(null)}
        onRetry={(errorId) => retryMutation.mutate(errorId)}
        onResolve={(errorId, notes) => resolveMutation.mutate({ errorId, notes })}
        onSkip={(errorId, reason) => skipMutation.mutate({ errorId, reason })}
      />
    </Box>
  );
};

export default ErrorsDashboardPage;
