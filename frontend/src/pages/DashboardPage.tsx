/**
 * Pipeline Dashboard Page
 * Main overview of the data pipeline with flow visualization
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
  CircularProgress,
  Alert,
  Paper,
  Divider,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Schedule as PendingIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { exceptionApi, dqApi, reconApi, pipelineApi } from '../api/client';
import PipelineFlowDiagram from '../components/dashboard/PipelineFlowDiagram';
import DateRangeFilter, { DateRange, getDateRangeForPreset } from '../components/dashboard/DateRangeFilter';
import BatchTrackingTable from '../components/batch/BatchTrackingTable';
import BatchDetailDialog from '../components/batch/BatchDetailDialog';
import { colors } from '../styles/design-system';

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, icon, color, trend }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight={700} sx={{ color }}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            p: 1,
            borderRadius: 2,
            backgroundColor: `${color}20`,
          }}
        >
          {React.cloneElement(icon as React.ReactElement<any>, { sx: { color, fontSize: 28 } })}
        </Box>
      </Box>
      {trend && (
        <Box sx={{ mt: 1, display: 'flex', alignItems: 'center' }}>
          <TrendingIcon
            sx={{
              fontSize: 16,
              color: trend.direction === 'up' ? colors.success.main : colors.error.main,
              transform: trend.direction === 'down' ? 'rotate(180deg)' : 'none',
            }}
          />
          <Typography
            variant="caption"
            sx={{
              ml: 0.5,
              color: trend.direction === 'up' ? colors.success.main : colors.error.main,
            }}
          >
            {trend.value}% from last hour
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

const DashboardPage: React.FC = () => {
  // Date range state - default to today
  const [dateRange, setDateRange] = useState<DateRange>(getDateRangeForPreset('today'));
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null);

  // Fetch exception summary
  const { data: exceptionSummary, isLoading: loadingExceptions } = useQuery({
    queryKey: ['exceptionSummary'],
    queryFn: () => exceptionApi.getSummary(undefined, 24),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch DQ metrics
  const { data: dqMetrics, isLoading: loadingDQ } = useQuery({
    queryKey: ['dqMetrics'],
    queryFn: () => dqApi.getSummary(),
    refetchInterval: 30000,
  });

  // Fetch reconciliation summary
  const { data: reconSummary, isLoading: loadingRecon } = useQuery({
    queryKey: ['reconSummary'],
    queryFn: () => reconApi.getSummary(undefined, 24),
    refetchInterval: 30000,
  });

  // Fetch pipeline stats from live API
  const { data: pipelineStatsData, isLoading: loadingPipeline } = useQuery({
    queryKey: ['pipelineStats'],
    queryFn: () => pipelineApi.getPipelineStats(),
    refetchInterval: 30000,
  });

  const isLoading = loadingExceptions || loadingDQ || loadingRecon || loadingPipeline;

  // Use live data with fallback to defaults
  const pipelineStats = pipelineStatsData || {
    bronze: { total: 0, processed: 0, failed: 0, pending: 0 },
    silver: { total: 0, processed: 0, failed: 0, pending: 0, dq_passed: 0, dq_failed: 0 },
    gold: { total: 0, processed: 0, failed: 0, pending: 0 },
    analytical: { total: 0, processed: 0, failed: 0, pending: 0 },
  };

  const handleLayerClick = (layer: string) => {
    console.log('Navigate to layer:', layer);
    // Navigate to layer-specific view
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Page Header with Date Filter */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Pipeline Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time overview of the GPS CDM data pipeline
          </Typography>
        </Box>
        <DateRangeFilter value={dateRange} onChange={setDateRange} />
      </Box>

      {/* Critical Alerts */}
      {exceptionSummary && exceptionSummary.critical_count > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <strong>{exceptionSummary.critical_count} critical exceptions</strong> require immediate attention
        </Alert>
      )}

      {/* Summary Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Total Records Processed"
            value={pipelineStats.bronze.processed}
            subtitle="Last 24 hours"
            icon={<SuccessIcon />}
            color={colors.success.main}
            trend={{ value: 12.5, direction: 'up' }}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Active Exceptions"
            value={exceptionSummary?.total || 0}
            subtitle={`${exceptionSummary?.new_count || 0} new`}
            icon={<WarningIcon />}
            color={colors.warning.main}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="DQ Pass Rate"
            value={dqMetrics && dqMetrics.length > 0
              ? `${((dqMetrics[0].passed_records / dqMetrics[0].total_records) * 100).toFixed(1)}%`
              : 'N/A'
            }
            subtitle="Silver layer"
            icon={<CheckCircle />}
            color={colors.primary.main}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Pending Processing"
            value={pipelineStats.bronze.pending + pipelineStats.silver.pending}
            subtitle="Awaiting promotion"
            icon={<PendingIcon />}
            color={colors.info.main}
          />
        </Grid>
      </Grid>

      {/* Pipeline Flow Visualization */}
      <Paper elevation={1} sx={{ mb: 4, p: 2 }}>
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2, px: 2 }}>
          Pipeline Flow
        </Typography>
        <PipelineFlowDiagram
          bronze={pipelineStats.bronze}
          silver={pipelineStats.silver}
          gold={pipelineStats.gold}
          analytical={pipelineStats.analytical}
          onLayerClick={handleLayerClick}
        />
      </Paper>

      {/* Batch Tracking Table */}
      <Paper elevation={1} sx={{ mb: 4, p: 2 }}>
        <BatchTrackingTable
          dateRange={dateRange}
          onViewBatch={(batchId) => {
            setSelectedBatchId(batchId);
          }}
        />
      </Paper>

      {/* Batch Detail Dialog */}
      <BatchDetailDialog
        open={!!selectedBatchId}
        batchId={selectedBatchId}
        onClose={() => setSelectedBatchId(null)}
      />

      {/* Bottom Section: Exceptions & DQ */}
      <Grid container spacing={3}>
        {/* Recent Exceptions */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Exception Summary (24h)
              </Typography>
              <Divider sx={{ my: 1.5 }} />
              {exceptionSummary ? (
                <Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    {Object.entries(exceptionSummary.by_severity || {}).map(([severity, count]) => (
                      <Chip
                        key={severity}
                        label={`${severity}: ${count}`}
                        size="small"
                        color={severity === 'CRITICAL' ? 'error' : severity === 'ERROR' ? 'warning' : 'default'}
                      />
                    ))}
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {Object.entries(exceptionSummary.by_layer || {}).map(([layer, count]) => (
                      <Chip
                        key={layer}
                        label={`${layer}: ${count}`}
                        size="small"
                        variant="outlined"
                        sx={{
                          borderColor: colors.zones[layer as keyof typeof colors.zones]?.main || colors.grey[400],
                          color: colors.zones[layer as keyof typeof colors.zones]?.dark || colors.grey[700],
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              ) : (
                <Typography color="text.secondary">No exception data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* DQ Summary */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Data Quality Summary
              </Typography>
              <Divider sx={{ my: 1.5 }} />
              {dqMetrics && dqMetrics.length > 0 ? (
                <Box>
                  {dqMetrics.slice(0, 3).map((metric, index) => (
                    <Box
                      key={index}
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        py: 1,
                        borderBottom: index < 2 ? `1px solid ${colors.grey[200]}` : 'none',
                      }}
                    >
                      <Box>
                        <Typography variant="body2" fontWeight={500}>
                          {metric.table_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {metric.layer} layer
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'right' }}>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          color={metric.overall_status === 'PASSED' ? 'success.main' : 'error.main'}
                        >
                          {metric.overall_score?.toFixed(1)}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {metric.passed_records}/{metric.total_records} passed
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary">No DQ metrics available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

// Fix missing import
const CheckCircle = SuccessIcon;

export default DashboardPage;
