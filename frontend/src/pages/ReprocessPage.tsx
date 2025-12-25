/**
 * Reprocess Page
 * UI for reprocessing failed records, batches, or DQ failures
 */
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  TextField,
  Paper,
  Chip,
  Alert,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Refresh as ReprocessIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
} from '@mui/icons-material';
import { reprocessApi } from '../api/client';
import { colors } from '../styles/design-system';

interface ReprocessResult {
  record_id?: string;
  batch_id?: string;
  status: 'success' | 'failed' | 'pending';
  message: string;
  records_processed?: number;
  records_failed?: number;
}

const ReprocessPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [reprocessType, setReprocessType] = useState<'record' | 'batch' | 'dq_failures'>('record');
  const [recordId, setRecordId] = useState('');
  const [batchId, setBatchId] = useState('');
  const [targetLayer, setTargetLayer] = useState('bronze');
  const [dqRuleFilter, setDqRuleFilter] = useState('');
  const [results, setResults] = useState<ReprocessResult[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  // Reprocess single record
  const reprocessRecordMutation = useMutation({
    mutationFn: ({ recordId, layer }: { recordId: string; layer: string }) =>
      reprocessApi.reprocessRecord(recordId, layer),
    onSuccess: (data) => {
      setResults(prev => [{
        record_id: recordId,
        status: 'success' as const,
        message: `Record ${recordId} reprocessed successfully`,
      }, ...prev]);
      queryClient.invalidateQueries({ queryKey: ['exceptions'] });
    },
    onError: (error: any) => {
      setResults(prev => [{
        record_id: recordId,
        status: 'failed' as const,
        message: error.message || 'Reprocessing failed',
      }, ...prev]);
    },
  });

  // Reprocess batch
  const reprocessBatchMutation = useMutation({
    mutationFn: ({ batchId, layer }: { batchId: string; layer: string }) =>
      reprocessApi.reprocessBatch(batchId, layer),
    onSuccess: () => {
      setResults(prev => [{
        batch_id: batchId,
        status: 'success' as const,
        message: `Batch ${batchId} reprocessed successfully`,
      }, ...prev]);
      queryClient.invalidateQueries({ queryKey: ['exceptions'] });
    },
    onError: (error: any) => {
      setResults(prev => [{
        batch_id: batchId,
        status: 'failed' as const,
        message: error.message || 'Batch reprocessing failed',
      }, ...prev]);
    },
  });

  // Reprocess DQ failures
  const reprocessDQMutation = useMutation({
    mutationFn: ({ batchId }: { batchId?: string }) =>
      reprocessApi.reprocessDQFailures(batchId),
    onSuccess: () => {
      setResults(prev => [{
        status: 'success' as const,
        message: `DQ failures reprocessed successfully`,
      }, ...prev]);
      queryClient.invalidateQueries({ queryKey: ['dqFailures'] });
    },
    onError: (error: any) => {
      setResults(prev => [{
        status: 'failed' as const,
        message: error.message || 'DQ reprocessing failed',
      }, ...prev]);
    },
  });

  const handleReprocess = async () => {
    setIsProcessing(true);
    try {
      switch (reprocessType) {
        case 'record':
          if (recordId) {
            await reprocessRecordMutation.mutateAsync({ recordId, layer: targetLayer });
          }
          break;
        case 'batch':
          if (batchId) {
            await reprocessBatchMutation.mutateAsync({ batchId, layer: targetLayer });
          }
          break;
        case 'dq_failures':
          await reprocessDQMutation.mutateAsync({
            batchId: batchId || undefined,
          });
          break;
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <SuccessIcon sx={{ color: colors.success.main }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: colors.error.main }} />;
      default:
        return <PendingIcon sx={{ color: colors.warning.main }} />;
    }
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Reprocess
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Reprocess failed records, batches, or data quality failures
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left: Reprocess Form */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Reprocess Configuration
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Reprocess Type</InputLabel>
                <Select
                  value={reprocessType}
                  label="Reprocess Type"
                  onChange={(e) => setReprocessType(e.target.value as any)}
                  disabled={isProcessing}
                >
                  <MenuItem value="record">Single Record</MenuItem>
                  <MenuItem value="batch">Entire Batch</MenuItem>
                  <MenuItem value="dq_failures">DQ Failures</MenuItem>
                </Select>
              </FormControl>

              {reprocessType === 'record' && (
                <TextField
                  fullWidth
                  label="Record ID"
                  value={recordId}
                  onChange={(e) => setRecordId(e.target.value)}
                  placeholder="Enter record ID to reprocess"
                  disabled={isProcessing}
                  sx={{ mb: 2 }}
                />
              )}

              {(reprocessType === 'batch' || reprocessType === 'dq_failures') && (
                <TextField
                  fullWidth
                  label="Batch ID"
                  value={batchId}
                  onChange={(e) => setBatchId(e.target.value)}
                  placeholder={reprocessType === 'dq_failures' ? 'Optional: Filter by batch' : 'Enter batch ID'}
                  disabled={isProcessing}
                  sx={{ mb: 2 }}
                />
              )}

              {reprocessType !== 'dq_failures' && (
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Target Layer</InputLabel>
                  <Select
                    value={targetLayer}
                    label="Target Layer"
                    onChange={(e) => setTargetLayer(e.target.value)}
                    disabled={isProcessing}
                  >
                    <MenuItem value="bronze">Bronze</MenuItem>
                    <MenuItem value="silver">Silver</MenuItem>
                    <MenuItem value="gold">Gold</MenuItem>
                  </Select>
                </FormControl>
              )}

              {reprocessType === 'dq_failures' && (
                <TextField
                  fullWidth
                  label="DQ Rule Filter"
                  value={dqRuleFilter}
                  onChange={(e) => setDqRuleFilter(e.target.value)}
                  placeholder="Optional: Filter by rule name"
                  disabled={isProcessing}
                  sx={{ mb: 2 }}
                />
              )}

              {isProcessing && <LinearProgress sx={{ mb: 2 }} />}

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={<ReprocessIcon />}
                onClick={handleReprocess}
                disabled={
                  isProcessing ||
                  (reprocessType === 'record' && !recordId) ||
                  (reprocessType === 'batch' && !batchId)
                }
              >
                {isProcessing ? 'Processing...' : 'Start Reprocessing'}
              </Button>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Quick Actions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={1}>
                <Grid size={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      setReprocessType('dq_failures');
                      setDqRuleFilter('completeness');
                    }}
                  >
                    Completeness Failures
                  </Button>
                </Grid>
                <Grid size={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      setReprocessType('dq_failures');
                      setDqRuleFilter('validity');
                    }}
                  >
                    Validity Failures
                  </Button>
                </Grid>
                <Grid size={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    color="warning"
                    onClick={() => {
                      setReprocessType('batch');
                      setTargetLayer('silver');
                    }}
                  >
                    Reprocess Silver
                  </Button>
                </Grid>
                <Grid size={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    color="secondary"
                    onClick={() => {
                      setReprocessType('batch');
                      setTargetLayer('gold');
                    }}
                  >
                    Reprocess Gold
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Right: Results */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight={600}>
                  Reprocessing Results
                </Typography>
                {results.length > 0 && (
                  <Button size="small" onClick={() => setResults([])}>
                    Clear
                  </Button>
                )}
              </Box>
              <Divider sx={{ mb: 2 }} />

              {results.length === 0 ? (
                <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: colors.grey[50] }}>
                  <Typography color="text.secondary">
                    No reprocessing results yet. Start a reprocess operation to see results here.
                  </Typography>
                </Paper>
              ) : (
                <List>
                  {results.map((result, index) => (
                    <ListItem
                      key={index}
                      sx={{
                        border: `1px solid ${colors.grey[200]}`,
                        borderRadius: 1,
                        mb: 1,
                        backgroundColor: result.status === 'success'
                          ? `${colors.success.main}08`
                          : result.status === 'failed'
                          ? `${colors.error.main}08`
                          : 'transparent',
                      }}
                    >
                      <ListItemIcon>
                        {getStatusIcon(result.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" fontWeight={500}>
                              {result.message}
                            </Typography>
                            <Chip
                              label={result.status.toUpperCase()}
                              size="small"
                              color={
                                result.status === 'success' ? 'success' :
                                result.status === 'failed' ? 'error' : 'warning'
                              }
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {result.record_id && (
                              <Typography variant="caption" display="block">
                                Record ID: {result.record_id}
                              </Typography>
                            )}
                            {result.batch_id && (
                              <Typography variant="caption" display="block">
                                Batch ID: {result.batch_id}
                              </Typography>
                            )}
                            {result.records_processed !== undefined && (
                              <Typography variant="caption" display="block">
                                Processed: {result.records_processed} | Failed: {result.records_failed || 0}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>

          {/* Instructions */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2" fontWeight={500} gutterBottom>
              Reprocessing Guide
            </Typography>
            <Typography variant="body2">
              • <strong>Single Record:</strong> Reprocess a specific record by ID from the selected layer<br />
              • <strong>Entire Batch:</strong> Reprocess all records in a batch from the selected layer<br />
              • <strong>DQ Failures:</strong> Reprocess records that failed data quality validation
            </Typography>
          </Alert>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ReprocessPage;
