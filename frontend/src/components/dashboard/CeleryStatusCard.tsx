/**
 * Celery Worker Status Card Component
 * Displays Celery/Flower worker status and task metrics
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
  Badge,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Refresh as RefreshIcon,
  Memory as WorkerIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { pipelineApi } from '../../api/client';
import { colors } from '../../styles/design-system';

interface CeleryStatusCardProps {
  compact?: boolean;
}

const CeleryStatusCard: React.FC<CeleryStatusCardProps> = ({ compact = false }) => {
  const [expanded, setExpanded] = React.useState(!compact);

  const { data: workersData, isLoading: loadingWorkers, refetch: refetchWorkers } = useQuery({
    queryKey: ['celeryWorkers'],
    queryFn: () => pipelineApi.getCeleryWorkers(),
    refetchInterval: 10000,
  });

  const { data: queuesData, isLoading: loadingQueues } = useQuery({
    queryKey: ['celeryQueues'],
    queryFn: () => pipelineApi.getCeleryQueues(),
    refetchInterval: 10000,
  });

  const { data: tasksData } = useQuery({
    queryKey: ['celeryTasks'],
    queryFn: () => pipelineApi.getCeleryTasks(undefined, 20),
    refetchInterval: 15000,
  });

  const isLoading = loadingWorkers || loadingQueues;
  const workers = workersData?.workers || [];
  const queues = queuesData?.queues || {};
  const tasks = tasksData?.tasks || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return colors.success.main;
      case 'no_workers': return colors.warning.main;
      case 'unavailable': return colors.error.main;
      default: return colors.grey[500];
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <SuccessIcon sx={{ color: colors.success.main }} />;
      case 'no_workers': return <WarningIcon sx={{ color: colors.warning.main }} />;
      case 'unavailable': return <ErrorIcon sx={{ color: colors.error.main }} />;
      default: return <WarningIcon sx={{ color: colors.grey[500] }} />;
    }
  };

  const getTaskStateChip = (state: string) => {
    const stateConfig: Record<string, { color: string; label: string }> = {
      SUCCESS: { color: colors.success.main, label: 'Success' },
      FAILURE: { color: colors.error.main, label: 'Failed' },
      PENDING: { color: colors.grey[500], label: 'Pending' },
      STARTED: { color: colors.info.main, label: 'Running' },
      RETRY: { color: colors.warning.main, label: 'Retry' },
    };
    const config = stateConfig[state] || { color: colors.grey[500], label: state };
    return (
      <Chip
        size="small"
        label={config.label}
        sx={{
          backgroundColor: `${config.color}20`,
          color: config.color,
          fontSize: 10,
          height: 18,
        }}
      />
    );
  };

  const totalActiveTasks = workers.reduce((sum: number, w: any) => sum + (w.active_tasks || 0), 0);
  const totalQueueDepth = Object.values(queues).reduce((sum: number, val: any) => sum + (val || 0), 0);

  // Task stats
  const successTasks = tasks.filter((t: any) => t.state === 'SUCCESS').length;
  const failedTasks = tasks.filter((t: any) => t.state === 'FAILURE').length;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ pb: expanded ? 2 : 1 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getStatusIcon(workersData?.status)}
            <Typography variant="h6" fontWeight={600}>
              Celery Workers
            </Typography>
            <Chip
              size="small"
              label={workersData?.status || 'loading'}
              sx={{
                backgroundColor: `${getStatusColor(workersData?.status)}20`,
                color: getStatusColor(workersData?.status),
                fontWeight: 500,
              }}
            />
          </Box>
          <Box>
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={() => refetchWorkers()}>
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
                {workers.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Workers
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.info.main}>
                {totalActiveTasks}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.warning.main}>
                {totalQueueDepth}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Queued
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight={700} color={colors.success.main}>
                {successTasks}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Recent OK
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Expanded Details */}
        <Collapse in={expanded}>
          <Divider sx={{ my: 1.5 }} />

          {/* Workers List */}
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
            Workers ({workers.length})
          </Typography>
          <Box sx={{ maxHeight: 120, overflowY: 'auto', mb: 2 }}>
            {workers.map((worker: any, index: number) => (
              <Box
                key={worker.name || index}
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
                  <Badge
                    badgeContent={worker.active_tasks}
                    color="primary"
                    max={99}
                    sx={{ '& .MuiBadge-badge': { fontSize: 10, height: 16, minWidth: 16 } }}
                  >
                    <WorkerIcon sx={{ color: worker.status === 'online' ? colors.success.main : colors.grey[400], fontSize: 20 }} />
                  </Badge>
                  <Typography variant="body2" sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {worker.name?.split('@')[1] || worker.name}
                  </Typography>
                </Box>
                <Chip
                  size="small"
                  label={`${worker.concurrency} proc`}
                  variant="outlined"
                  sx={{ fontSize: 10, height: 20 }}
                />
              </Box>
            ))}
            {workers.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 1 }}>
                No workers connected
              </Typography>
            )}
          </Box>

          {/* Queue Depths */}
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
            Queue Depths
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {Object.entries(queues).map(([queue, depth]: [string, any]) => (
              <Chip
                key={queue}
                size="small"
                label={`${queue}: ${depth}`}
                sx={{
                  backgroundColor: depth > 0 ? colors.warning.light + '40' : colors.grey[100],
                  fontWeight: depth > 0 ? 600 : 400,
                }}
              />
            ))}
            {Object.keys(queues).length === 0 && (
              <Typography variant="body2" color="text.secondary">
                No queue data
              </Typography>
            )}
          </Box>

          {/* Recent Tasks */}
          <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
            Recent Tasks
          </Typography>
          <Box sx={{ maxHeight: 100, overflowY: 'auto' }}>
            {tasks.slice(0, 5).map((task: any) => (
              <Box
                key={task.task_id}
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
                <Typography variant="body2" sx={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {task.name}
                </Typography>
                {getTaskStateChip(task.state)}
              </Box>
            ))}
            {tasks.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 1 }}>
                No recent tasks
              </Typography>
            )}
          </Box>
        </Collapse>

        {/* Error display */}
        {workersData?.error && (
          <Box sx={{ mt: 1, p: 1, backgroundColor: colors.error.light + '20', borderRadius: 1 }}>
            <Typography variant="caption" color="error">
              {workersData.error}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CeleryStatusCard;
