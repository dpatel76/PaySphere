/**
 * Batch Detail Dialog
 * Shows detailed information about a batch with tabs for summary, records, and exceptions
 */
import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  IconButton,
  Typography,
  Tabs,
  Tab,
  Chip,
  CircularProgress,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { pipelineApi } from '../../api/client';
import type { BatchDetail } from '../../types';
import { colors } from '../../styles/design-system';
import BatchSummaryTab from './tabs/BatchSummaryTab';
import BatchRecordsTab from './tabs/BatchRecordsTab';
import BatchExceptionsTab from './tabs/BatchExceptionsTab';

interface BatchDetailDialogProps {
  open: boolean;
  batchId: string | null;
  onClose: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      sx={{ py: 2 }}
    >
      {value === index && children}
    </Box>
  );
};

// Status color mapping
const statusColors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  COMPLETED: 'success',
  PROCESSING: 'info',
  PENDING: 'warning',
  FAILED: 'error',
  PARTIAL: 'warning',
};

const BatchDetailDialog: React.FC<BatchDetailDialogProps> = ({
  open,
  batchId,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState(0);

  // Fetch batch details
  const { data: batchDetail, isLoading } = useQuery<BatchDetail>({
    queryKey: ['batchDetail', batchId],
    queryFn: async () => {
      if (!batchId) throw new Error('No batch ID');
      const batch = await pipelineApi.getBatch(batchId);

      // Transform to BatchDetail format
      return {
        batch_id: batch.batch_id,
        source_system: batch.source_system,
        message_type: batch.message_type,
        status: batch.status,
        created_at: batch.started_at,
        completed_at: batch.completed_at,
        duration_seconds: batch.completed_at
          ? Math.round((new Date(batch.completed_at).getTime() - new Date(batch.started_at).getTime()) / 1000)
          : undefined,
        metrics: {
          bronze: {
            input_records: batch.bronze_records || 0,
            processed_records: batch.bronze_records || 0,
            failed_records: 0,
            pending_records: 0,
            exceptions: 0,
          },
          silver: {
            input_records: batch.bronze_records || 0,
            processed_records: batch.silver_records || 0,
            failed_records: batch.failed_records || 0,
            pending_records: 0,
            exceptions: 0,
            dq_passed: batch.silver_records || 0,
            dq_failed: 0,
            dq_score: batch.dq_score,
          },
          gold: {
            input_records: batch.silver_records || 0,
            processed_records: batch.gold_records || 0,
            failed_records: 0,
            pending_records: 0,
            exceptions: 0,
          },
          analytics: {
            input_records: batch.gold_records || 0,
            processed_records: 0,
            failed_records: 0,
            pending_records: 0,
            exceptions: 0,
          },
        },
        timing: {
          ingestion_start: batch.started_at,
          bronze_complete: batch.started_at,
          silver_complete: batch.completed_at,
          gold_complete: batch.completed_at,
        },
      };
    },
    enabled: !!batchId && open,
  });

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Batch Details
            </Typography>
            {batchDetail && (
              <>
                <Typography
                  variant="body2"
                  sx={{ fontFamily: 'monospace', color: 'text.secondary' }}
                >
                  {batchDetail.batch_id}
                </Typography>
                <Chip
                  label={batchDetail.status}
                  size="small"
                  color={statusColors[batchDetail.status] || 'default'}
                  sx={{ fontWeight: 600 }}
                />
              </>
            )}
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 0 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : batchDetail ? (
          <>
            {/* Tabs */}
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              sx={{
                borderBottom: `1px solid ${colors.grey[200]}`,
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 500,
                },
              }}
            >
              <Tab label="Summary" />
              <Tab label="Records" />
              <Tab label="Exceptions" />
            </Tabs>

            {/* Tab Panels */}
            <TabPanel value={activeTab} index={0}>
              <BatchSummaryTab batchDetail={batchDetail} />
            </TabPanel>
            <TabPanel value={activeTab} index={1}>
              <BatchRecordsTab batchId={batchDetail.batch_id} messageType={batchDetail.message_type} />
            </TabPanel>
            <TabPanel value={activeTab} index={2}>
              <BatchExceptionsTab batchId={batchDetail.batch_id} />
            </TabPanel>
          </>
        ) : (
          <Box sx={{ py: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">
              No batch data available
            </Typography>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default BatchDetailDialog;
