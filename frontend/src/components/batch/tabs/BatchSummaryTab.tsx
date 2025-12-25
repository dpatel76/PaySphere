/**
 * Batch Summary Tab
 * Displays key metrics, timing, and status for a batch
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  LinearProgress,
  Chip,
  Divider,
} from '@mui/material';
import {
  AccessTime as TimeIcon,
  Storage as StorageIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import type { BatchDetail, ZoneMetrics } from '../../../types';
import { colors } from '../../../styles/design-system';

interface BatchSummaryTabProps {
  batchDetail: BatchDetail;
}

// Zone progress card component
const ZoneProgressCard: React.FC<{
  zone: string;
  metrics: ZoneMetrics;
  zoneColor: { main: string; light: string; dark: string };
}> = ({ zone, metrics, zoneColor }) => {
  const successRate = metrics.input_records > 0
    ? (metrics.processed_records / metrics.input_records) * 100
    : 0;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: zoneColor.main,
            }}
          />
          <Typography variant="subtitle1" fontWeight={600} sx={{ textTransform: 'capitalize' }}>
            {zone}
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              Progress
            </Typography>
            <Typography variant="body2" fontWeight={500}>
              {successRate.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={successRate}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: zoneColor.light,
              '& .MuiLinearProgress-bar': {
                backgroundColor: zoneColor.main,
                borderRadius: 4,
              },
            }}
          />
        </Box>

        <Grid container spacing={1}>
          <Grid size={{ xs: 4 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight={700}>
                {metrics.input_records.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Input
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" fontWeight={700} color="success.main">
                {metrics.processed_records.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Processed
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography
                variant="h6"
                fontWeight={700}
                color={metrics.exceptions > 0 ? 'error.main' : 'text.secondary'}
              >
                {metrics.exceptions}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Exceptions
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {metrics.dq_score !== undefined && (
          <Box sx={{ mt: 2, pt: 2, borderTop: `1px solid ${colors.grey[200]}` }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                DQ Score
              </Typography>
              <Chip
                label={`${(metrics.dq_score * 100).toFixed(1)}%`}
                size="small"
                color={metrics.dq_score >= 0.9 ? 'success' : metrics.dq_score >= 0.7 ? 'warning' : 'error'}
              />
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

const BatchSummaryTab: React.FC<BatchSummaryTabProps> = ({ batchDetail }) => {
  const formatDuration = (seconds?: number): string => {
    if (!seconds) return 'In Progress';
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const formatDateTime = (dateStr: string): string => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const totalInputRecords = batchDetail.metrics.bronze.input_records;
  const totalProcessed = batchDetail.metrics.gold.processed_records;
  const totalExceptions =
    batchDetail.metrics.bronze.exceptions +
    batchDetail.metrics.silver.exceptions +
    batchDetail.metrics.gold.exceptions +
    batchDetail.metrics.analytics.exceptions;

  return (
    <Box>
      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <StorageIcon sx={{ color: colors.primary.main }} />
                <Typography variant="body2" color="text.secondary">
                  Source System
                </Typography>
              </Box>
              <Typography variant="h6" fontWeight={600}>
                {batchDetail.source_system}
              </Typography>
              <Chip
                label={batchDetail.message_type}
                size="small"
                sx={{ mt: 1, backgroundColor: colors.primary.light + '30' }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SpeedIcon sx={{ color: colors.info.main }} />
                <Typography variant="body2" color="text.secondary">
                  Total Records
                </Typography>
              </Box>
              <Typography variant="h6" fontWeight={600}>
                {totalInputRecords.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {totalProcessed.toLocaleString()} promoted to Gold
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TimeIcon sx={{ color: colors.warning.main }} />
                <Typography variant="body2" color="text.secondary">
                  Duration
                </Typography>
              </Box>
              <Typography variant="h6" fontWeight={600}>
                {formatDuration(batchDetail.duration_seconds)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Started {formatDateTime(batchDetail.created_at)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {totalExceptions > 0 ? (
                  <ErrorIcon sx={{ color: colors.error.main }} />
                ) : (
                  <SuccessIcon sx={{ color: colors.success.main }} />
                )}
                <Typography variant="body2" color="text.secondary">
                  Exceptions
                </Typography>
              </Box>
              <Typography
                variant="h6"
                fontWeight={600}
                color={totalExceptions > 0 ? 'error.main' : 'success.main'}
              >
                {totalExceptions}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {totalExceptions === 0 ? 'No issues detected' : 'Requires attention'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Zone Progress Cards */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
        Processing by Zone
      </Typography>
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ZoneProgressCard
            zone="bronze"
            metrics={batchDetail.metrics.bronze}
            zoneColor={colors.zones.bronze}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ZoneProgressCard
            zone="silver"
            metrics={batchDetail.metrics.silver}
            zoneColor={colors.zones.silver}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ZoneProgressCard
            zone="gold"
            metrics={batchDetail.metrics.gold}
            zoneColor={colors.zones.gold}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <ZoneProgressCard
            zone="analytics"
            metrics={batchDetail.metrics.analytics}
            zoneColor={colors.zones.analytical}
          />
        </Grid>
      </Grid>

      {/* Timing Details */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
          Processing Timeline
        </Typography>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {Object.entries(batchDetail.timing).map(([key, value]) => (
                value && (
                  <Box
                    key={key}
                    sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                  >
                    <Typography
                      variant="body2"
                      sx={{ textTransform: 'capitalize' }}
                      color="text.secondary"
                    >
                      {key.replace(/_/g, ' ')}
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatDateTime(value)}
                    </Typography>
                  </Box>
                )
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default BatchSummaryTab;
