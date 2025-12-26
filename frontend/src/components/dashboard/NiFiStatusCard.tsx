/**
 * NiFi Status Card Component
 * Displays NiFi flow orchestration status and processor metrics
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
  IconButton,
  Collapse,
  Divider,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Refresh as RefreshIcon,
  PlayArrow as RunningIcon,
  Stop as StoppedIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as HealthyIcon,
} from '@mui/icons-material';
import { pipelineApi } from '../../api/client';
import { colors } from '../../styles/design-system';

interface NiFiStatusCardProps {
  compact?: boolean;
}

const NiFiStatusCard: React.FC<NiFiStatusCardProps> = ({ compact = false }) => {
  const [expanded, setExpanded] = React.useState(!compact);

  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['nifiStatus'],
    queryFn: () => pipelineApi.getNifiStatus(),
    refetchInterval: 15000, // Refresh every 15 seconds
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return colors.success.main;
      case 'unavailable': return colors.error.main;
      case 'timeout': return colors.warning.main;
      default: return colors.grey[500];
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <HealthyIcon sx={{ color: colors.success.main }} />;
      case 'unavailable': return <ErrorIcon sx={{ color: colors.error.main }} />;
      case 'timeout': return <WarningIcon sx={{ color: colors.warning.main }} />;
      default: return <WarningIcon sx={{ color: colors.grey[500] }} />;
    }
  };

  const getProcessorStateIcon = (state: string) => {
    switch (state?.toUpperCase()) {
      case 'RUNNING': return <RunningIcon sx={{ fontSize: 16, color: colors.success.main }} />;
      case 'STOPPED': return <StoppedIcon sx={{ fontSize: 16, color: colors.grey[500] }} />;
      case 'DISABLED': return <StoppedIcon sx={{ fontSize: 16, color: colors.grey[400] }} />;
      default: return <WarningIcon sx={{ fontSize: 16, color: colors.warning.main }} />;
    }
  };

  const flowStatus = data?.flow_status || {};
  const processors = data?.processors || [];

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ pb: expanded ? 2 : 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getStatusIcon(data?.status)}
            <Typography variant="h6" fontWeight={600}>
              NiFi Flow
            </Typography>
            <Chip
              size="small"
              label={data?.status || 'loading'}
              sx={{
                backgroundColor: `${getStatusColor(data?.status)}20`,
                color: getStatusColor(data?.status),
                fontWeight: 500,
              }}
            />
          </Box>
          <Box>
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={() => refetch()} disabled={isRefetching}>
                <RefreshIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
            <IconButton size="small" onClick={() => setExpanded(!expanded)}>
              {expanded ? <CollapseIcon /> : <ExpandIcon />}
            </IconButton>
          </Box>
        </Box>

        {isLoading && <LinearProgress sx={{ mb: 1 }} />}

        {/* Summary Stats */}
        <Grid container spacing={2} sx={{ mb: expanded ? 2 : 0 }}>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.primary.main}>
                {flowStatus.flow_files_in || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Files In
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.success.main}>
                {flowStatus.running_count || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Running
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.warning.main}>
                {flowStatus.queued_count || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Queued
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.grey[600]}>
                {flowStatus.stopped_count || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Stopped
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Expanded Processor Details */}
        <Collapse in={expanded}>
          <Divider sx={{ my: 1.5 }} />
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
            Processors ({processors.length})
          </Typography>
          <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
            {processors.map((proc: any, index: number) => (
              <Box
                key={proc.id || index}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  py: 0.5,
                  px: 1,
                  borderRadius: 1,
                  '&:hover': { backgroundColor: colors.grey[50] },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getProcessorStateIcon(proc.state)}
                  <Typography variant="body2" sx={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {proc.name || proc.type}
                  </Typography>
                </Box>
                <Chip
                  size="small"
                  label={proc.type}
                  variant="outlined"
                  sx={{ fontSize: 10, height: 20 }}
                />
              </Box>
            ))}
            {processors.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                {data?.status === 'running' ? 'No processors found' : 'NiFi not available'}
              </Typography>
            )}
          </Box>
        </Collapse>

        {/* Error display */}
        {data?.error && (
          <Box sx={{ mt: 1, p: 1, backgroundColor: colors.error.light + '20', borderRadius: 1 }}>
            <Typography variant="caption" color="error">
              {data.error}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default NiFiStatusCard;
