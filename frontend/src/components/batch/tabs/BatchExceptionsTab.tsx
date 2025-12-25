/**
 * Batch Exceptions Tab
 * Displays exceptions for a batch with acknowledge/resolve/retry actions
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridPaginationModel,
} from '@mui/x-data-grid';
import {
  Visibility as ViewIcon,
  Check as AcknowledgeIcon,
  Done as ResolveIcon,
  Replay as RetryIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { exceptionApi } from '../../../api/client';
import type { ProcessingException } from '../../../types';
import { colors } from '../../../styles/design-system';

interface BatchExceptionsTabProps {
  batchId: string;
}

// Severity color mapping
const severityColors: Record<string, 'error' | 'warning' | 'info'> = {
  CRITICAL: 'error',
  ERROR: 'warning',
  WARNING: 'info',
};

// Status color mapping
const statusColors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  NEW: 'error',
  ACKNOWLEDGED: 'warning',
  IN_PROGRESS: 'info',
  RESOLVED: 'success',
  IGNORED: 'default',
};

const BatchExceptionsTab: React.FC<BatchExceptionsTabProps> = ({ batchId }) => {
  const queryClient = useQueryClient();
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 25,
  });
  const [selectedException, setSelectedException] = useState<ProcessingException | null>(null);
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');

  // Fetch exceptions for batch
  const { data, isLoading, error } = useQuery({
    queryKey: ['batchExceptions', batchId, paginationModel],
    queryFn: async () => {
      const exceptions = await exceptionApi.getExceptions({
        batch_id: batchId,
        limit: paginationModel.pageSize,
        offset: paginationModel.page * paginationModel.pageSize,
      });
      return {
        items: exceptions,
        total: exceptions.length,
      };
    },
    enabled: !!batchId,
  });

  // Acknowledge mutation
  const acknowledgeMutation = useMutation({
    mutationFn: (exceptionId: string) => exceptionApi.acknowledgeException(exceptionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batchExceptions', batchId] });
    },
  });

  // Resolve mutation
  const resolveMutation = useMutation({
    mutationFn: ({ exceptionId, notes }: { exceptionId: string; notes: string }) =>
      exceptionApi.resolveException(exceptionId, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batchExceptions', batchId] });
      setResolveDialogOpen(false);
      setSelectedException(null);
      setResolutionNotes('');
    },
  });

  // Retry mutation
  const retryMutation = useMutation({
    mutationFn: (exceptionId: string) => exceptionApi.retryException(exceptionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batchExceptions', batchId] });
    },
  });

  const handleAcknowledge = (exception: ProcessingException) => {
    acknowledgeMutation.mutate(exception.exception_id);
  };

  const handleResolveClick = (exception: ProcessingException) => {
    setSelectedException(exception);
    setResolveDialogOpen(true);
  };

  const handleResolveConfirm = () => {
    if (selectedException) {
      resolveMutation.mutate({
        exceptionId: selectedException.exception_id,
        notes: resolutionNotes,
      });
    }
  };

  const handleRetry = (exception: ProcessingException) => {
    retryMutation.mutate(exception.exception_id);
  };

  const columns: GridColDef[] = [
    {
      field: 'exception_id',
      headerName: 'Exception ID',
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 11 }}>
            {params.value?.substring(0, 10)}...
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'severity',
      headerName: 'Severity',
      width: 90,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          color={severityColors[params.value] || 'default'}
          sx={{ fontSize: 10, fontWeight: 600 }}
        />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 110,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          color={statusColors[params.value] || 'default'}
          sx={{ fontSize: 10 }}
        />
      ),
    },
    {
      field: 'source_layer',
      headerName: 'Layer',
      width: 80,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          variant="outlined"
          sx={{
            fontSize: 10,
            borderColor: colors.zones[params.value as keyof typeof colors.zones]?.main || colors.grey[400],
            color: colors.zones[params.value as keyof typeof colors.zones]?.dark || colors.grey[700],
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
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography
            variant="body2"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'retry_count',
      headerName: 'Retries',
      width: 80,
      align: 'center',
      headerAlign: 'center',
      renderCell: (params: GridRenderCellParams) => (
        <Typography variant="body2">
          {params.value}/{params.row.max_retries}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 140,
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
      width: 140,
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams<ProcessingException>) => {
        const exception = params.row;
        const isNew = exception.status === 'NEW';
        const canResolve = ['NEW', 'ACKNOWLEDGED', 'IN_PROGRESS'].includes(exception.status);
        const canRetry = exception.can_retry && exception.retry_count < exception.max_retries;

        return (
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="View Details">
              <IconButton size="small" onClick={() => setSelectedException(exception)}>
                <ViewIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            {isNew && (
              <Tooltip title="Acknowledge">
                <IconButton
                  size="small"
                  onClick={() => handleAcknowledge(exception)}
                  disabled={acknowledgeMutation.isPending}
                >
                  <AcknowledgeIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {canResolve && (
              <Tooltip title="Resolve">
                <IconButton
                  size="small"
                  onClick={() => handleResolveClick(exception)}
                  color="success"
                >
                  <ResolveIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {canRetry && (
              <Tooltip title="Retry">
                <IconButton
                  size="small"
                  onClick={() => handleRetry(exception)}
                  disabled={retryMutation.isPending}
                  color="primary"
                >
                  <RetryIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        );
      },
    },
  ];

  if (error) {
    return (
      <Alert severity="error">
        Failed to load exceptions: {(error as Error).message}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Summary Stats */}
      {data && data.items.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          {['CRITICAL', 'ERROR', 'WARNING'].map((severity) => {
            const count = data.items.filter((e) => e.severity === severity).length;
            if (count === 0) return null;
            return (
              <Chip
                key={severity}
                label={`${severity}: ${count}`}
                size="small"
                color={severityColors[severity]}
              />
            );
          })}
          {['NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED'].map((status) => {
            const count = data.items.filter((e) => e.status === status).length;
            if (count === 0) return null;
            return (
              <Chip
                key={status}
                label={`${status}: ${count}`}
                size="small"
                variant="outlined"
                color={statusColors[status]}
              />
            );
          })}
        </Box>
      )}

      {/* Exceptions DataGrid */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <DataGrid
          rows={data?.items || []}
          columns={columns}
          getRowId={(row) => row.exception_id}
          paginationModel={paginationModel}
          onPaginationModelChange={setPaginationModel}
          pageSizeOptions={[10, 25, 50]}
          rowCount={data?.total || 0}
          paginationMode="client"
          disableRowSelectionOnClick
          autoHeight
          sx={{
            border: 'none',
            '& .MuiDataGrid-columnHeaders': {
              backgroundColor: colors.grey[50],
              borderBottom: `2px solid ${colors.grey[200]}`,
            },
            '& .MuiDataGrid-cell': {
              borderBottom: `1px solid ${colors.grey[100]}`,
            },
            '& .MuiDataGrid-row:hover': {
              backgroundColor: colors.grey[50],
            },
            '& .MuiDataGrid-columnHeaderTitle': {
              fontWeight: 600,
              fontSize: 12,
            },
          }}
        />
      )}

      {/* Empty State */}
      {!isLoading && (!data?.items || data.items.length === 0) && (
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No exceptions found for this batch
          </Typography>
        </Box>
      )}

      {/* Exception Detail Dialog */}
      <Dialog
        open={!!selectedException && !resolveDialogOpen}
        onClose={() => setSelectedException(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedException && (
          <>
            <DialogTitle sx={{ pb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="h6" fontWeight={600}>
                    Exception Details
                  </Typography>
                  <Chip
                    label={selectedException.severity}
                    size="small"
                    color={severityColors[selectedException.severity]}
                  />
                  <Chip
                    label={selectedException.status}
                    size="small"
                    color={statusColors[selectedException.status]}
                  />
                </Box>
                <IconButton onClick={() => setSelectedException(null)} size="small">
                  <CloseIcon />
                </IconButton>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Exception ID
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {selectedException.exception_id}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Source Layer
                    </Typography>
                    <Typography variant="body2">
                      {selectedException.source_layer} / {selectedException.source_table}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Exception Type
                    </Typography>
                    <Typography variant="body2">{selectedException.exception_type}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Record ID
                    </Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {selectedException.source_record_id}
                    </Typography>
                  </Box>
                </Box>

                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Message
                  </Typography>
                  <Typography variant="body2">{selectedException.exception_message}</Typography>
                </Box>

                {selectedException.exception_details && (
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Details
                    </Typography>
                    <Box
                      component="pre"
                      sx={{
                        mt: 0.5,
                        p: 1,
                        backgroundColor: colors.grey[100],
                        borderRadius: 1,
                        fontSize: 11,
                        fontFamily: 'monospace',
                        overflow: 'auto',
                        maxHeight: 200,
                      }}
                    >
                      {JSON.stringify(selectedException.exception_details, null, 2)}
                    </Box>
                  </Box>
                )}

                {selectedException.resolution_notes && (
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Resolution Notes
                    </Typography>
                    <Typography variant="body2">{selectedException.resolution_notes}</Typography>
                    {selectedException.resolved_by && (
                      <Typography variant="caption" color="text.secondary">
                        Resolved by {selectedException.resolved_by} at{' '}
                        {selectedException.resolved_at &&
                          new Date(selectedException.resolved_at).toLocaleString()}
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            </DialogContent>
          </>
        )}
      </Dialog>

      {/* Resolve Dialog */}
      <Dialog
        open={resolveDialogOpen}
        onClose={() => {
          setResolveDialogOpen(false);
          setResolutionNotes('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Resolve Exception</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Resolution Notes"
            fullWidth
            multiline
            rows={4}
            value={resolutionNotes}
            onChange={(e) => setResolutionNotes(e.target.value)}
            placeholder="Describe how this exception was resolved..."
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setResolveDialogOpen(false);
              setResolutionNotes('');
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleResolveConfirm}
            variant="contained"
            color="success"
            disabled={resolveMutation.isPending}
          >
            {resolveMutation.isPending ? 'Resolving...' : 'Resolve'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BatchExceptionsTab;
