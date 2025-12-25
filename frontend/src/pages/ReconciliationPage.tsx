/**
 * Reconciliation Dashboard Page
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
  Paper,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import {
  CheckCircle as MatchedIcon,
  Warning as MismatchIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { reconApi } from '../api/client';
import { colors } from '../styles/design-system';

const ReconciliationPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [batchFilter, setBatchFilter] = useState('');
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [selectedMismatch, setSelectedMismatch] = useState<any>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [resolutionAction, setResolutionAction] = useState('');

  // Fetch reconciliation summary
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['reconSummary'],
    queryFn: () => reconApi.getSummary(undefined, 24),
  });

  // Fetch mismatches
  const { data: mismatches, isLoading: loadingMismatches } = useQuery({
    queryKey: ['reconMismatches', batchFilter],
    queryFn: () => reconApi.getMismatches({ batch_id: batchFilter || undefined, limit: 100 }),
  });

  // Fetch history
  const { data: history } = useQuery({
    queryKey: ['reconHistory'],
    queryFn: () => reconApi.getHistory(undefined, 10),
  });

  // Resolve mutation
  const resolveMutation = useMutation({
    mutationFn: ({ id, action, notes }: { id: string; action: string; notes: string }) =>
      reconApi.resolve(id, action, notes, 'current_user'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reconMismatches'] });
      setResolveDialogOpen(false);
      setSelectedMismatch(null);
    },
  });

  const handleResolve = () => {
    if (selectedMismatch && resolutionAction && resolutionNotes) {
      resolveMutation.mutate({
        id: selectedMismatch.recon_id,
        action: resolutionAction,
        notes: resolutionNotes,
      });
    }
  };

  const pieData = summary ? [
    { name: 'Matched', value: summary.matched || 0, color: colors.success.main },
    { name: 'Mismatched', value: summary.mismatched || 0, color: colors.error.main },
    { name: 'Orphaned', value: summary.orphaned || 0, color: colors.warning.main },
  ] : [];

  const mismatchColumns: GridColDef[] = [
    { field: 'mismatch_type', headerName: 'Type', width: 150 },
    { field: 'bronze_raw_id', headerName: 'Bronze ID', width: 150 },
    { field: 'silver_stg_id', headerName: 'Silver ID', width: 150 },
    { field: 'gold_instruction_id', headerName: 'Gold ID', width: 150 },
    { field: 'field_name', headerName: 'Field', width: 120 },
    { field: 'source_value', headerName: 'Source Value', width: 150 },
    { field: 'target_value', headerName: 'Target Value', width: 150 },
    {
      field: 'investigation_status',
      headerName: 'Status',
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          color={
            params.value === 'RESOLVED' ? 'success' :
            params.value === 'INVESTIGATING' ? 'warning' : 'default'
          }
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Button
          size="small"
          variant="outlined"
          onClick={() => {
            setSelectedMismatch(params.row);
            setResolveDialogOpen(true);
          }}
          disabled={params.row.investigation_status === 'RESOLVED'}
        >
          Resolve
        </Button>
      ),
    },
  ];

  const historyColumns: GridColDef[] = [
    { field: 'recon_run_id', headerName: 'Run ID', width: 150 },
    { field: 'batch_id', headerName: 'Batch', width: 150 },
    { field: 'total_source_records', headerName: 'Source', width: 100 },
    { field: 'total_target_records', headerName: 'Target', width: 100 },
    { field: 'matched_count', headerName: 'Matched', width: 100 },
    { field: 'mismatched_count', headerName: 'Mismatched', width: 100 },
    {
      field: 'match_rate',
      headerName: 'Match Rate',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Typography
          variant="body2"
          color={params.value >= 95 ? 'success.main' : params.value >= 80 ? 'warning.main' : 'error.main'}
          fontWeight={600}
        >
          {params.value?.toFixed(1)}%
        </Typography>
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip label={params.value} size="small" color="success" />
      ),
    },
  ];

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Reconciliation
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Compare and reconcile data between Bronze source and Gold target
        </Typography>
      </Box>

      {/* Summary Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Reconciliation Summary
              </Typography>
              <Box sx={{ height: 200 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                      label
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 1 }}>
                {pieData.map((item) => (
                  <Box key={item.name} sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        backgroundColor: item.color,
                        mr: 0.5,
                      }}
                    />
                    <Typography variant="caption">{item.name}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 8 }}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="success.main">
                  {summary?.match_rate?.toFixed(1) || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">Match Rate</Typography>
              </Paper>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700}>
                  {summary?.total_runs || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">Recon Runs</Typography>
              </Paper>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="error.main">
                  {summary?.pending_investigation || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">Pending Investigation</Typography>
              </Paper>
            </Grid>
            <Grid size={{ xs: 6, sm: 3 }}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" fontWeight={700} color="warning.main">
                  {summary?.orphaned || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">Orphaned Records</Typography>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Mismatches */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Mismatches & Orphans
            </Typography>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Investigation Status</InputLabel>
              <Select defaultValue="" label="Investigation Status">
                <MenuItem value="">All</MenuItem>
                <MenuItem value="PENDING">Pending</MenuItem>
                <MenuItem value="INVESTIGATING">Investigating</MenuItem>
                <MenuItem value="RESOLVED">Resolved</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <DataGrid
            rows={mismatches || []}
            columns={mismatchColumns}
            getRowId={(row) => row.recon_id}
            loading={loadingMismatches}
            pageSizeOptions={[10, 25, 50]}
            initialState={{
              pagination: { paginationModel: { pageSize: 10 } },
            }}
            sx={{ minHeight: 400, border: 'none' }}
            disableRowSelectionOnClick
          />
        </CardContent>
      </Card>

      {/* Run History */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Reconciliation History
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <DataGrid
            rows={history || []}
            columns={historyColumns}
            getRowId={(row) => row.recon_run_id}
            pageSizeOptions={[5, 10]}
            initialState={{
              pagination: { paginationModel: { pageSize: 5 } },
            }}
            sx={{ minHeight: 300, border: 'none' }}
            disableRowSelectionOnClick
          />
        </CardContent>
      </Card>

      {/* Resolve Dialog */}
      <Dialog open={resolveDialogOpen} onClose={() => setResolveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Resolve Mismatch</DialogTitle>
        <DialogContent>
          {selectedMismatch && (
            <Box sx={{ mt: 1 }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Type:</strong> {selectedMismatch.mismatch_type}<br />
                  <strong>Field:</strong> {selectedMismatch.field_name || 'N/A'}<br />
                  <strong>Source:</strong> {selectedMismatch.source_value || 'N/A'} →{' '}
                  <strong>Target:</strong> {selectedMismatch.target_value || 'N/A'}
                </Typography>
              </Alert>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Resolution Action</InputLabel>
                <Select
                  value={resolutionAction}
                  label="Resolution Action"
                  onChange={(e) => setResolutionAction(e.target.value)}
                >
                  <MenuItem value="ACCEPTED">Accepted - Valid difference</MenuItem>
                  <MenuItem value="CORRECTED">Corrected - Data fixed</MenuItem>
                  <MenuItem value="REJECTED">Rejected - Invalid data</MenuItem>
                  <MenuItem value="REPROCESSED">Reprocessed - Re-run pipeline</MenuItem>
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
    </Box>
  );
};

export default ReconciliationPage;
