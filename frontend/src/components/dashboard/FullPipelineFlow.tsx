/**
 * Full Pipeline Flow Component
 * Complete visualization of the data pipeline from input to analytics
 * Shows: Input Files > NiFi > Message Routing > Flower/Celery > Bronze > Silver > Gold > Analytics
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Tooltip,
  Paper,
  Grid,
  Divider,
} from '@mui/material';
import {
  ArrowForward as ArrowIcon,
  CloudUpload as InputIcon,
  AccountTree as NiFiIcon,
  Hub as RouterIcon,
  Memory as CeleryIcon,
  Storage as BronzeIcon,
  FilterAlt as SilverIcon,
  Star as GoldIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { pipelineApi } from '../../api/client';
import { colors } from '../../styles/design-system';

interface FullPipelineFlowProps {
  onComponentClick?: (component: string) => void;
}

const FullPipelineFlow: React.FC<FullPipelineFlowProps> = ({ onComponentClick }) => {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['pipelineOverview'],
    queryFn: () => pipelineApi.getOverview(),
    refetchInterval: 15000,
  });

  const { data: stats } = useQuery({
    queryKey: ['pipelineStats'],
    queryFn: () => pipelineApi.getPipelineStats(),
    refetchInterval: 30000,
  });

  const components = overview?.components || {};
  const batchStats = overview?.batch_stats || {};
  const messageTypes = overview?.message_types || [];

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'running':
      case 'connected':
      case 'healthy':
        return <HealthyIcon sx={{ fontSize: 16, color: colors.success.main }} />;
      case 'degraded':
      case 'no_workers':
        return <WarningIcon sx={{ fontSize: 16, color: colors.warning.main }} />;
      default:
        return <ErrorIcon sx={{ fontSize: 16, color: colors.error.main }} />;
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'running':
      case 'connected':
      case 'healthy':
        return colors.success.main;
      case 'degraded':
      case 'no_workers':
        return colors.warning.main;
      default:
        return colors.error.main;
    }
  };

  // Component Box renderer
  const ComponentBox: React.FC<{
    icon: React.ReactNode;
    label: string;
    status?: string;
    metrics?: { label: string; value: number | string }[];
    color: string;
    onClick?: () => void;
    width?: number;
  }> = ({ icon, label, status, metrics, color, onClick, width = 140 }) => (
    <Paper
      elevation={2}
      onClick={onClick}
      sx={{
        p: 1.5,
        minWidth: width,
        cursor: onClick ? 'pointer' : 'default',
        border: `2px solid ${color}`,
        borderRadius: 2,
        transition: 'all 0.2s ease',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: `0 4px 12px ${color}40`,
        } : {},
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Box sx={{ color }}>{icon}</Box>
        <Typography variant="subtitle2" fontWeight={600}>
          {label}
        </Typography>
        {status && getHealthIcon(status)}
      </Box>
      {metrics && metrics.map((m, i) => (
        <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.25 }}>
          <Typography variant="caption" color="text.secondary">{m.label}</Typography>
          <Typography variant="caption" fontWeight={600}>{m.value}</Typography>
        </Box>
      ))}
    </Paper>
  );

  // Arrow with count
  const FlowArrow: React.FC<{ count?: number; label?: string }> = ({ count, label }) => (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mx: 0.5 }}>
      <ArrowIcon sx={{ fontSize: 24, color: colors.grey[400] }} />
      {(count !== undefined || label) && (
        <Chip
          size="small"
          label={count?.toLocaleString() || label}
          sx={{ height: 18, fontSize: 10, mt: 0.25 }}
        />
      )}
    </Box>
  );

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
            Full Pipeline Flow
          </Typography>
          <LinearProgress />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        {/* Header with overall health */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6" fontWeight={600}>
            Full Pipeline Flow
          </Typography>
          <Chip
            icon={getHealthIcon(overview?.overall_health || 'unknown')}
            label={overview?.overall_health?.toUpperCase() || 'UNKNOWN'}
            sx={{
              backgroundColor: `${getHealthColor(overview?.overall_health)}20`,
              color: getHealthColor(overview?.overall_health),
              fontWeight: 600,
            }}
          />
        </Box>

        {/* Main Pipeline Flow */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            overflowX: 'auto',
            pb: 2,
            px: 1,
          }}
        >
          {/* Input Files */}
          <ComponentBox
            icon={<InputIcon />}
            label="Input Files"
            color={colors.grey[600]}
            metrics={[
              { label: 'Today', value: batchStats.total_batches_24h || 0 },
            ]}
            onClick={() => onComponentClick?.('input')}
          />

          <FlowArrow />

          {/* NiFi */}
          <ComponentBox
            icon={<NiFiIcon />}
            label="NiFi"
            status={components.nifi?.status}
            color={colors.info.main}
            metrics={[
              { label: 'Files In', value: components.nifi?.flow_files_in || 0 },
              { label: 'Queued', value: components.nifi?.queued_count || 0 },
              { label: 'Processors', value: components.nifi?.running_processors || 0 },
            ]}
            onClick={() => onComponentClick?.('nifi')}
          />

          <FlowArrow />

          {/* Message Type Router */}
          <ComponentBox
            icon={<RouterIcon />}
            label="Message Router"
            color={colors.secondary.main}
            metrics={[
              { label: 'Types', value: messageTypes.length },
            ]}
            onClick={() => onComponentClick?.('router')}
            width={120}
          />

          <FlowArrow />

          {/* Celery */}
          <ComponentBox
            icon={<CeleryIcon />}
            label="Celery"
            status={components.celery?.status}
            color={colors.primary.main}
            metrics={[
              { label: 'Workers', value: components.celery?.worker_count || 0 },
              { label: 'Active', value: components.celery?.active_tasks || 0 },
              { label: 'Queued', value: components.celery?.queue_depth || 0 },
            ]}
            onClick={() => onComponentClick?.('celery')}
          />

          <FlowArrow count={batchStats.total_records} />

          {/* Bronze */}
          <ComponentBox
            icon={<BronzeIcon />}
            label="Bronze"
            color={colors.zones.bronze.main}
            metrics={[
              { label: 'Total', value: stats?.bronze?.total || 0 },
              { label: 'Processed', value: stats?.bronze?.processed || 0 },
              { label: 'Failed', value: stats?.bronze?.failed || 0 },
            ]}
            onClick={() => onComponentClick?.('bronze')}
          />

          <FlowArrow count={stats?.silver?.total} />

          {/* Silver */}
          <ComponentBox
            icon={<SilverIcon />}
            label="Silver"
            color={colors.zones.silver.dark}
            metrics={[
              { label: 'Total', value: stats?.silver?.total || 0 },
              { label: 'DQ Pass', value: stats?.silver?.dq_passed || 0 },
              { label: 'DQ Fail', value: stats?.silver?.dq_failed || 0 },
            ]}
            onClick={() => onComponentClick?.('silver')}
          />

          <FlowArrow count={stats?.gold?.total} />

          {/* Gold */}
          <ComponentBox
            icon={<GoldIcon />}
            label="Gold (CDM)"
            color={colors.zones.gold.dark}
            metrics={[
              { label: 'Total', value: stats?.gold?.total || 0 },
              { label: 'Processed', value: stats?.gold?.processed || 0 },
            ]}
            onClick={() => onComponentClick?.('gold')}
          />

          <FlowArrow count={stats?.analytical?.total} />

          {/* Analytics */}
          <ComponentBox
            icon={<AnalyticsIcon />}
            label="Analytics"
            color={colors.zones.analytical.main}
            metrics={[
              { label: 'Total', value: stats?.analytical?.total || 0 },
            ]}
            onClick={() => onComponentClick?.('analytics')}
            width={110}
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Message Type Breakdown */}
        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1.5 }}>
          Message Type Distribution (24h)
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {messageTypes.length > 0 ? (
            messageTypes.map((mt: any) => (
              <Tooltip key={mt.type} title={`${mt.count} batches`}>
                <Chip
                  label={`${mt.type}: ${mt.count}`}
                  size="small"
                  sx={{
                    backgroundColor: colors.primary.main + '15',
                    fontWeight: 500,
                  }}
                  onClick={() => onComponentClick?.(`msgtype:${mt.type}`)}
                />
              </Tooltip>
            ))
          ) : (
            <Typography variant="body2" color="text.secondary">
              No message data in the last 24 hours
            </Typography>
          )}
        </Box>

        {/* Queue Status */}
        {overview?.queues && Object.keys(overview.queues).length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1.5 }}>
              Celery Queue Depths
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {Object.entries(overview.queues).map(([queue, depth]: [string, any]) => (
                <Chip
                  key={queue}
                  label={`${queue}: ${depth}`}
                  size="small"
                  color={depth > 10 ? 'warning' : 'default'}
                  variant={depth > 0 ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
          </>
        )}

        {/* Summary Stats Row */}
        <Divider sx={{ my: 2 }} />
        <Grid container spacing={2}>
          <Grid size={{ xs: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.primary.main}>
                {batchStats.total_batches_24h || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">Batches (24h)</Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.success.main}>
                {batchStats.completed || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">Completed</Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.info.main}>
                {batchStats.processing || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">Processing</Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.error.main}>
                {batchStats.failed || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">Failed</Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.zones.bronze.main}>
                {(batchStats.total_records || 0).toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">Records In</Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.zones.gold.dark}>
                {(batchStats.records_to_gold || 0).toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">To Gold</Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default FullPipelineFlow;
