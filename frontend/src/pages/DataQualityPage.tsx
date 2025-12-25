/**
 * Data Quality Dashboard Page
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  Paper,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import {
  CheckCircle as PassedIcon,
  Cancel as FailedIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { dqApi } from '../api/client';
import { colors } from '../styles/design-system';

const DataQualityPage: React.FC = () => {
  const [batchFilter, setBatchFilter] = useState('');
  const [layerFilter, setLayerFilter] = useState('');

  // Fetch DQ metrics
  const { data: metrics, isLoading: loadingMetrics } = useQuery({
    queryKey: ['dqMetrics', batchFilter, layerFilter],
    queryFn: () => dqApi.getSummary(batchFilter || undefined, layerFilter || undefined),
  });

  // Fetch DQ rules
  const { data: rules } = useQuery({
    queryKey: ['dqRules', layerFilter],
    queryFn: () => dqApi.getRules(layerFilter || undefined),
  });

  // Fetch failures
  const { data: failures, isLoading: loadingFailures } = useQuery({
    queryKey: ['dqFailures', batchFilter, layerFilter],
    queryFn: () => dqApi.getFailures({
      batch_id: batchFilter || undefined,
      layer: layerFilter || undefined,
      limit: 50,
    }),
  });

  // Calculate summary stats
  const summaryStats = React.useMemo(() => {
    if (!metrics || metrics.length === 0) return null;

    const totalRecords = metrics.reduce((sum, m) => sum + m.total_records, 0);
    const passedRecords = metrics.reduce((sum, m) => sum + m.passed_records, 0);
    const failedRecords = metrics.reduce((sum, m) => sum + m.failed_records, 0);
    const avgScore = metrics.reduce((sum, m) => sum + (m.overall_score || 0), 0) / metrics.length;

    return {
      totalRecords,
      passedRecords,
      failedRecords,
      passRate: totalRecords > 0 ? (passedRecords / totalRecords * 100) : 0,
      avgScore,
    };
  }, [metrics]);

  const pieData = summaryStats ? [
    { name: 'Passed', value: summaryStats.passedRecords, color: colors.success.main },
    { name: 'Failed', value: summaryStats.failedRecords, color: colors.error.main },
  ] : [];

  const dimensionData = metrics?.[0] ? [
    { name: 'Completeness', score: metrics[0].completeness_score || 0 },
    { name: 'Validity', score: metrics[0].validity_score || 0 },
    { name: 'Accuracy', score: metrics[0].accuracy_score || 0 },
  ] : [];

  const rulesColumns: GridColDef[] = [
    { field: 'rule_name', headerName: 'Rule Name', flex: 1 },
    { field: 'rule_type', headerName: 'Type', width: 120 },
    { field: 'layer', headerName: 'Layer', width: 100 },
    { field: 'field_name', headerName: 'Field', width: 150 },
    {
      field: 'is_blocking',
      headerName: 'Blocking',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Yes' : 'No'}
          size="small"
          color={params.value ? 'error' : 'default'}
        />
      ),
    },
    { field: 'weight', headerName: 'Weight', width: 80 },
  ];

  const failuresColumns: GridColDef[] = [
    { field: 'record_id', headerName: 'Record ID', width: 150 },
    { field: 'rule_name', headerName: 'Rule', flex: 1 },
    { field: 'layer', headerName: 'Layer', width: 100 },
    {
      field: 'passed',
      headerName: 'Status',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        params.value ? (
          <Chip label="Passed" size="small" color="success" />
        ) : (
          <Chip label="Failed" size="small" color="error" />
        )
      ),
    },
    { field: 'actual_value', headerName: 'Actual', width: 150 },
    { field: 'error_message', headerName: 'Error', flex: 1 },
  ];

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Data Quality
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor data quality metrics and validation results across the pipeline
        </Typography>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Layer</InputLabel>
            <Select
              value={layerFilter}
              label="Layer"
              onChange={(e) => setLayerFilter(e.target.value)}
            >
              <MenuItem value="">All Layers</MenuItem>
              <MenuItem value="bronze">Bronze</MenuItem>
              <MenuItem value="silver">Silver</MenuItem>
              <MenuItem value="gold">Gold</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Card>

      {/* Summary Stats */}
      {summaryStats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid size={{ xs: 6, md: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.primary.main}` }}>
              <Typography variant="h4" fontWeight={700}>
                {summaryStats.totalRecords.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">Total Validated</Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 6, md: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.success.main}` }}>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {summaryStats.passRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">Pass Rate</Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 6, md: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.info.main}` }}>
              <Typography variant="h4" fontWeight={700} color="info.main">
                {summaryStats.avgScore.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">Avg DQ Score</Typography>
            </Paper>
          </Grid>
          <Grid size={{ xs: 6, md: 3 }}>
            <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${colors.error.main}` }}>
              <Typography variant="h4" fontWeight={700} color="error.main">
                {summaryStats.failedRecords.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">Failed Records</Typography>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Pass/Fail Distribution
              </Typography>
              <Box sx={{ height: 250 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Dimension Scores
              </Typography>
              <Box sx={{ height: 250 }}>
                <ResponsiveContainer>
                  <BarChart data={dimensionData}>
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="score" fill={colors.primary.main} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* DQ Rules */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Data Quality Rules
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <DataGrid
            rows={rules || []}
            columns={rulesColumns}
            getRowId={(row) => row.rule_id}
            pageSizeOptions={[10, 25]}
            initialState={{
              pagination: { paginationModel: { pageSize: 10 } },
            }}
            sx={{ minHeight: 300, border: 'none' }}
            disableRowSelectionOnClick
          />
        </CardContent>
      </Card>

      {/* Recent Failures */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Recent Validation Failures
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <DataGrid
            rows={failures || []}
            columns={failuresColumns}
            getRowId={(row) => row.dq_result_id}
            loading={loadingFailures}
            pageSizeOptions={[10, 25, 50]}
            initialState={{
              pagination: { paginationModel: { pageSize: 25 } },
            }}
            sx={{ minHeight: 400, border: 'none' }}
            disableRowSelectionOnClick
          />
        </CardContent>
      </Card>
    </Box>
  );
};

export default DataQualityPage;
