/**
 * Monitoring Dashboard Page
 * Comprehensive pipeline monitoring showing:
 * - Full pipeline flow (Input > NiFi > Routing > Celery > Bronze > Silver > Gold > Analytics)
 * - NiFi status and processors
 * - Celery workers and tasks
 * - Message type breakdown and metrics
 * - Throughput over time
 * - Batch tracking
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Chip,
  Alert,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountTree as NiFiIcon,
  Memory as CeleryIcon,
  TrendingUp as MetricsIcon,
} from '@mui/icons-material';

import { pipelineApi, exceptionApi } from '../api/client';
import { colors } from '../styles/design-system';

// Dashboard Components
import FullPipelineFlow from '../components/dashboard/FullPipelineFlow';
import NiFiStatusCard from '../components/dashboard/NiFiStatusCard';
import CeleryStatusCard from '../components/dashboard/CeleryStatusCard';
import MessageTypeMetrics from '../components/dashboard/MessageTypeMetrics';
import ThroughputChart from '../components/dashboard/ThroughputChart';
import PipelineFlowDiagram from '../components/dashboard/PipelineFlowDiagram';
import DateRangeFilter, { DateRange, getDateRangeForPreset } from '../components/dashboard/DateRangeFilter';
import BatchTrackingTable from '../components/batch/BatchTrackingTable';
import BatchDetailDialog from '../components/batch/BatchDetailDialog';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ paddingTop: 16 }}>
    {value === index && children}
  </div>
);

const MonitoringDashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dateRange, setDateRange] = useState<DateRange>(getDateRangeForPreset('today'));
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null);
  const [selectedMessageType, setSelectedMessageType] = useState<string | null>(null);

  // Fetch pipeline overview for health status
  const { data: overview } = useQuery({
    queryKey: ['pipelineOverview'],
    queryFn: () => pipelineApi.getOverview(),
    refetchInterval: 15000,
  });

  // Fetch exception summary for alerts
  const { data: exceptionSummary } = useQuery({
    queryKey: ['exceptionSummary'],
    queryFn: () => exceptionApi.getSummary(undefined, 24),
    refetchInterval: 30000,
  });

  // Fetch pipeline stats
  const { data: pipelineStats } = useQuery({
    queryKey: ['pipelineStats'],
    queryFn: () => pipelineApi.getPipelineStats(),
    refetchInterval: 30000,
  });

  const handleComponentClick = (component: string) => {
    if (component.startsWith('msgtype:')) {
      setSelectedMessageType(component.replace('msgtype:', ''));
      setActiveTab(2); // Switch to Message Types tab
    } else if (component === 'nifi') {
      setActiveTab(1);
    } else if (component === 'celery') {
      setActiveTab(1);
    }
  };

  const getOverallHealthColor = () => {
    switch (overview?.overall_health) {
      case 'healthy': return colors.success.main;
      case 'degraded': return colors.warning.main;
      case 'critical':
      case 'unhealthy': return colors.error.main;
      default: return colors.grey[500];
    }
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h4" fontWeight={700}>
              Pipeline Monitoring
            </Typography>
            <Chip
              label={overview?.overall_health?.toUpperCase() || 'LOADING'}
              sx={{
                backgroundColor: `${getOverallHealthColor()}20`,
                color: getOverallHealthColor(),
                fontWeight: 600,
              }}
            />
          </Box>
          <Typography variant="body1" color="text.secondary">
            Real-time monitoring of the GPS CDM data processing pipeline
          </Typography>
        </Box>
        <DateRangeFilter value={dateRange} onChange={setDateRange} />
      </Box>

      {/* Critical Alerts */}
      {exceptionSummary && exceptionSummary.critical_count > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <strong>{exceptionSummary.critical_count} critical exceptions</strong> require immediate attention.
          {' '}Total active exceptions: {exceptionSummary.total}
        </Alert>
      )}

      {overview?.overall_health === 'critical' && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <strong>Pipeline Health Critical:</strong> Multiple components are unavailable.
          Check NiFi and Celery worker status.
        </Alert>
      )}

      {overview?.overall_health === 'degraded' && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <strong>Pipeline Degraded:</strong> Some components may not be functioning optimally.
        </Alert>
      )}

      {/* Full Pipeline Flow - Always visible at top */}
      <Box sx={{ mb: 3 }}>
        <FullPipelineFlow onComponentClick={handleComponentClick} />
      </Box>

      {/* Tabbed Content */}
      <Paper elevation={1} sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          sx={{ borderBottom: `1px solid ${colors.grey[200]}`, px: 2 }}
        >
          <Tab icon={<DashboardIcon />} label="Overview" iconPosition="start" />
          <Tab icon={<NiFiIcon />} label="Infrastructure" iconPosition="start" />
          <Tab icon={<MetricsIcon />} label="Message Types" iconPosition="start" />
          <Tab icon={<CeleryIcon />} label="Throughput" iconPosition="start" />
        </Tabs>

        <Box sx={{ p: 2 }}>
          {/* Overview Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              {/* Medallion Flow Diagram */}
              <Grid size={{ xs: 12 }}>
                <Paper elevation={0} sx={{ p: 2, backgroundColor: colors.grey[50], borderRadius: 2 }}>
                  <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                    Medallion Architecture Flow
                  </Typography>
                  <PipelineFlowDiagram
                    bronze={pipelineStats?.bronze || { total: 0, processed: 0, failed: 0, pending: 0 }}
                    silver={pipelineStats?.silver || { total: 0, processed: 0, failed: 0, pending: 0, dqPassed: 0, dqFailed: 0 }}
                    gold={pipelineStats?.gold || { total: 0, processed: 0, failed: 0, pending: 0 }}
                    analytical={pipelineStats?.analytical}
                  />
                </Paper>
              </Grid>

              {/* NiFi and Celery Summary */}
              <Grid size={{ xs: 12, md: 6 }}>
                <NiFiStatusCard compact />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <CeleryStatusCard compact />
              </Grid>

              {/* Recent Batches */}
              <Grid size={{ xs: 12 }}>
                <BatchTrackingTable
                  dateRange={dateRange}
                  onViewBatch={(batchId) => setSelectedBatchId(batchId)}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Infrastructure Tab */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, lg: 6 }}>
                <NiFiStatusCard />
              </Grid>
              <Grid size={{ xs: 12, lg: 6 }}>
                <CeleryStatusCard />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Message Types Tab */}
          <TabPanel value={activeTab} index={2}>
            <MessageTypeMetrics
              hoursBack={dateRange.preset === 'today' ? 24 : dateRange.preset === 'last7days' ? 168 : dateRange.preset === 'last30days' ? 720 : 24}
              onSelectMessageType={setSelectedMessageType}
            />
          </TabPanel>

          {/* Throughput Tab */}
          <TabPanel value={activeTab} index={3}>
            <ThroughputChart
              defaultHoursBack={dateRange.preset === 'today' ? 24 : dateRange.preset === 'last7days' ? 168 : dateRange.preset === 'last30days' ? 720 : 24}
            />
          </TabPanel>
        </Box>
      </Paper>

      {/* Batch Detail Dialog */}
      <BatchDetailDialog
        open={!!selectedBatchId}
        batchId={selectedBatchId}
        onClose={() => setSelectedBatchId(null)}
      />
    </Box>
  );
};

export default MonitoringDashboardPage;
