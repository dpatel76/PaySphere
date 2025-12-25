/**
 * Exception Handling Dashboard Page
 * View, acknowledge, resolve, and reprocess exceptions
 */
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Tabs,
  Tab,
  Tooltip,
  Paper,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import {
  Visibility as ViewIcon,
  Check as AcknowledgeIcon,
  Done as ResolveIcon,
  Refresh as RetryIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { exceptionApi, reprocessApi } from '../api/client';
import { ProcessingException, ExceptionSummary } from '../types';
import { colors } from '../styles/design-system';

const severityColors: Record<string, string> = {
  CRITICAL: colors.error.main,
  ERROR: colors.warning.main,
  WARNING: colors.info.main,
};

const statusColors: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error'> = {
  NEW: 'error',
  ACKNOWLEDGED: 'warning',
  IN_PROGRESS: 'primary',
  RESOLVED: 'success',
  IGNORED: 'default',
};

const ExceptionsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState(0);
  const [filters, setFilters] = useState({
    layer: '',
    severity: '',
    status: '',
    exception_type: '',
  });
  const [selectedException, setSelectedException] = useState<ProcessingException | null>(null);
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [resolutionAction, setResolutionAction] = useState('');

  // Fetch exception summary
  const { data: summary } = useQuery({
    queryKey: ['exceptionSummary'],
    queryFn: () => exceptionApi.getSummary(undefined, 24),
    refetchInterval: 30000,
  });

  // Fetch exceptions list
  const { data: exceptions, isLoading } = useQuery({
    queryKey: ['exceptions', filters],
    queryFn: () => exceptionApi.getExceptions({
      ...filters,
      limit: 100,
    }),
  });

  // Acknowledge mutation
  const acknowledgeMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) =>
      exceptionApi.acknowledge(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exceptions'] });
      queryClient.invalidateQueries({ queryKey: ['exceptionSummary'] });
    },
  });

  // Resolve mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, action, notes }: { id: string; action: string; notes: string }) =>
      exceptionApi.resolve(id, {
        resolution_action: action,
        notes,
        resolved_by: 'current_user', // Replace with actual user
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exceptions'] });
      queryClient.invalidateQueries({ queryKey: ['exceptionSummary'] });
      setResolveDialogOpen(false);
      setSelectedException(null);
    },
  });

  // Retry mutation
  const retryMutation = useMutation({
    mutationFn: (id: string) => exceptionApi.scheduleRetry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exceptions'] });
    },
  });

  const handleResolve = () => {
    if (selectedException && resolutionAction && resolutionNotes) {
      resolveMutation.mutate({
        id: selectedException.exception_id,
        action: resolutionAction,
        notes: resolutionNotes,
      });
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'severity',
      headerName: 'Severity',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          sx={{
            backgroundColor: severityColors[params.value as string],
            color: 'white',
            fontWeight: 600,
            fontSize: 11,
          }}
        />
      ),
    },
    {
      field: 'source_layer',
      headerName: 'Layer',
      width: 90,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          variant="outlined"
          sx={{
            borderColor: colors.zones[params.value as keyof typeof colors.zones]?.main,
            color: colors.zones[params.value as keyof typeof colors.zones]?.dark,
          }}
        />
      ),
    },
    {
      field: 'exception_type',
      headerName: 'Type',
      width: 140,
    },
    {
      field: 'exception_message',
      headerName: 'Message',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          color={statusColors[params.value as string] || 'default'}
        />
      ),
    },
    {
      field: 'retry_count',
      headerName: 'Retries',
      width: 80,
      renderCell: (params: GridRenderCellParams) => (
        <Typography variant="body2">
          {params.value}/{params.row.max_retries}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 150,
      valueFormatter: (value: string) =>
        new Date(value).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        }),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="View Details">
            <IconButton size="small" onClick={() => setSelectedException(params.row)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status === 'NEW' && (
            <Tooltip title="Acknowledge">
              <IconButton
                size="small"
                onClick={() => acknowledgeMutation.mutate({
                  id: params.row.exception_id,
                  notes: 'Acknowledged from dashboard',
                })}
              >
                <AcknowledgeIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          {params.row.status !== 'RESOLVED' && params.row.status !== 'IGNORED' && (
            <Tooltip title="Resolve">
              <IconButton
                size="small"
                onClick={() => {
                  setSelectedException(params.row);
                  setResolveDialogOpen(true);
                }}
              >
                <ResolveIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          {params.row.can_retry && params.row.retry_count < params.row.max_retries && (
            <Tooltip title="Schedule Retry">
              <IconButton
                size="small"
                onClick={() => retryMutation.mutate(params.row.exception_id)}
              >
                <RetryIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      ),
    },
  ];

  // Filter by tab
  const filteredExceptions = React.useMemo(() => {
    if (!exceptions) return [];
    switch (selectedTab) {
      case 0: // All
        return exceptions;
      case 1: // New
        return exceptions.filter(e => e.status === 'NEW');
      case 2: // Critical
        return exceptions.filter(e => e.severity === 'CRITICAL');
      case 3: // Retryable
        return exceptions.filter(e => e.can_retry && e.retry_count < e.max_retries);
      default:
        return exceptions;
    }
  }, [exceptions, selectedTab]);

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Exception Handling
        </Typography>
        <Typography variant="body1" color="text.secondary">
          View, acknowledge, and resolve processing exceptions across the pipeline
        </Typography>
      </Box>

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.error.main}` }}>
              <Typography variant="h4" fontWeight={700} color="error.main">
                {summary.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">Total Exceptions</Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.warning.main}` }}>
              <Typography variant="h4" fontWeight={700} color="warning.main">
                {summary.new_count}
              </Typography>
              <Typography variant="body2" color="text.secondary">New / Unhandled</Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.error.dark}` }}>
              <Typography variant="h4" fontWeight={700} color="error.dark">
                {summary.critical_count}
              </Typography>
              <Typography variant="body2" color="text.secondary">Critical</Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.success.main}` }}>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {summary.resolved_count}
              </Typography>
              <Typography variant="body2" color="text.secondary">Resolved</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Filters & Tabs */}
      <Card sx={{ mb: 2 }}>
        <Tabs
          value={selectedTab}
          onChange={(_, v) => setSelectedTab(v)}
          sx={{ borderBottom: `1px solid ${colors.grey[200]}` }}
        >
          <Tab label={`All (${exceptions?.length || 0})`} />
          <Tab label={`New (${exceptions?.filter(e => e.status === 'NEW').length || 0})`} />
          <Tab label={`Critical (${exceptions?.filter(e => e.severity === 'CRITICAL').length || 0})`} />
          <Tab label={`Retryable (${exceptions?.filter(e => e.can_retry).length || 0})`} />
        </Tabs>
        <Box sx={{ p: 2, display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Layer</InputLabel>
            <Select
              value={filters.layer}
              label="Layer"
              onChange={(e) => setFilters(f => ({ ...f, layer: e.target.value }))}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="bronze">Bronze</MenuItem>
              <MenuItem value="silver">Silver</MenuItem>
              <MenuItem value="gold">Gold</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Severity</InputLabel>
            <Select
              value={filters.severity}
              label="Severity"
              onChange={(e) => setFilters(f => ({ ...f, severity: e.target.value }))}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="CRITICAL">Critical</MenuItem>
              <MenuItem value="ERROR">Error</MenuItem>
              <MenuItem value="WARNING">Warning</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={filters.exception_type}
              label="Type"
              onChange={(e) => setFilters(f => ({ ...f, exception_type: e.target.value }))}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="PARSE_ERROR">Parse Error</MenuItem>
              <MenuItem value="VALIDATION_ERROR">Validation Error</MenuItem>
              <MenuItem value="TRANSFORM_ERROR">Transform Error</MenuItem>
              <MenuItem value="DQ_FAILURE">DQ Failure</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Card>

      {/* Exceptions Grid */}
      <Card>
        <DataGrid
          rows={filteredExceptions}
          columns={columns}
          getRowId={(row) => row.exception_id}
          loading={isLoading}
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } },
            sorting: { sortModel: [{ field: 'created_at', sort: 'desc' }] },
          }}
          sx={{ minHeight: 500, border: 'none' }}
          disableRowSelectionOnClick
        />
      </Card>

      {/* Resolve Dialog */}
      <Dialog open={resolveDialogOpen} onClose={() => setResolveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Resolve Exception</DialogTitle>
        <DialogContent>
          {selectedException && (
            <Box sx={{ mt: 1 }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>{selectedException.exception_type}</strong>: {selectedException.exception_message}
                </Typography>
              </Alert>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Resolution Action</InputLabel>
                <Select
                  value={resolutionAction}
                  label="Resolution Action"
                  onChange={(e) => setResolutionAction(e.target.value)}
                >
                  <MenuItem value="FIXED">Fixed - Record corrected</MenuItem>
                  <MenuItem value="IGNORED">Ignored - Known issue</MenuItem>
                  <MenuItem value="REPROCESSED">Reprocessed - Retry successful</MenuItem>
                  <MenuItem value="ESCALATED">Escalated - Needs investigation</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Resolution Notes"
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResolveDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleResolve}
            disabled={!resolutionAction || !resolutionNotes}
          >
            Resolve
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog
        open={!!selectedException && !resolveDialogOpen}
        onClose={() => setSelectedException(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Exception Details</DialogTitle>
        <DialogContent>
          {selectedException && (
            <Box sx={{ mt: 1 }}>
              <Grid container spacing={2}>
                <Grid size={6}>
                  <Typography variant="caption" color="text.secondary">Exception ID</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {selectedException.exception_id}
                  </Typography>
                </Grid>
                <Grid size={6}>
                  <Typography variant="caption" color="text.secondary">Record ID</Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {selectedException.source_record_id}
                  </Typography>
                </Grid>
                <Grid size={12}>
                  <Typography variant="caption" color="text.secondary">Message</Typography>
                  <Typography variant="body2">{selectedException.exception_message}</Typography>
                </Grid>
                {selectedException.exception_details && (
                  <Grid size={12}>
                    <Typography variant="caption" color="text.secondary">Details</Typography>
                    <Paper sx={{ p: 1, mt: 0.5, backgroundColor: colors.grey[100] }}>
                      <pre style={{ margin: 0, fontSize: 12, overflow: 'auto' }}>
                        {JSON.stringify(selectedException.exception_details, null, 2)}
                      </pre>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedException(null)}>Close</Button>
          <Button
            variant="outlined"
            onClick={() => {
              setResolveDialogOpen(true);
            }}
          >
            Resolve
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExceptionsPage;
