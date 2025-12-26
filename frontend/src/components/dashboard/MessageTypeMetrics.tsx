/**
 * Message Type Metrics Component
 * Shows processing statistics broken down by message type with flow visualization
 */
import React, { useState } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Refresh as RefreshIcon,
  ArrowForward as FlowIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { pipelineApi } from '../../api/client';
import { colors } from '../../styles/design-system';

interface MessageTypeMetricsProps {
  hoursBack?: number;
  onSelectMessageType?: (messageType: string) => void;
}

const MessageTypeMetrics: React.FC<MessageTypeMetricsProps> = ({
  hoursBack = 24,
  onSelectMessageType,
}) => {
  const [expanded, setExpanded] = useState(true);
  const [selectedType, setSelectedType] = useState<string | null>(null);

  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['messageTypeStats', hoursBack],
    queryFn: () => pipelineApi.getMessageTypeStats(hoursBack),
    refetchInterval: 30000,
  });

  const { data: flowData, isLoading: loadingFlow } = useQuery({
    queryKey: ['messageTypeFlow', selectedType, hoursBack],
    queryFn: () => selectedType ? pipelineApi.getMessageTypeFlow(selectedType, hoursBack) : null,
    enabled: !!selectedType,
  });

  const messageTypes = data?.message_types || [];

  const handleSelectType = (type: string) => {
    setSelectedType(type === selectedType ? null : type);
    onSelectMessageType?.(type);
  };

  const getSuccessRate = (mt: any) => {
    const total = mt.total_bronze || 0;
    const gold = mt.total_gold || 0;
    return total > 0 ? ((gold / total) * 100).toFixed(1) : '0.0';
  };

  const getDQPassRate = (mt: any) => {
    const silver = mt.total_silver || 0;
    const passed = mt.dq_passed || 0;
    return silver > 0 ? ((passed / silver) * 100).toFixed(1) : '0.0';
  };

  // Get message type icon based on the type
  const getMessageTypeColor = (type: string) => {
    if (type?.toLowerCase().includes('pain')) return colors.zones.bronze.main;
    if (type?.toLowerCase().includes('pacs')) return colors.zones.silver.main;
    if (type?.toLowerCase().includes('mt')) return colors.zones.gold.main;
    if (type?.toLowerCase().includes('fed')) return colors.primary.main;
    if (type?.toLowerCase().includes('sepa')) return colors.secondary.main;
    return colors.grey[600];
  };

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingIcon sx={{ color: colors.primary.main }} />
            <Typography variant="h6" fontWeight={600}>
              Message Type Metrics
            </Typography>
            <Chip
              size="small"
              label={`${messageTypes.length} types`}
              variant="outlined"
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

        {isLoading && <LinearProgress sx={{ mb: 2 }} />}

        <Collapse in={expanded}>
          {/* Message Types Table */}
          <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ backgroundColor: colors.grey[50] }}>
                  <TableCell sx={{ fontWeight: 600 }}>Message Type</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Format</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Records</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Processed</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Failed</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>In Progress</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Success %</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 600 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {messageTypes.map((mt: any) => (
                  <TableRow
                    key={mt.message_type}
                    hover
                    selected={mt.message_type === selectedType}
                    onClick={() => handleSelectType(mt.message_type)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            backgroundColor: getMessageTypeColor(mt.message_type),
                          }}
                        />
                        <Typography variant="body2" fontWeight={500}>
                          {mt.message_type}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={mt.message_format || 'N/A'}
                        variant="outlined"
                        sx={{ fontSize: 10 }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600}>
                        {(mt.total_records || mt.total_bronze || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ color: colors.success.main }}>
                        {(mt.processed || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ color: (mt.failed || 0) > 0 ? colors.error.main : colors.grey[500] }}>
                        {(mt.failed || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ color: (mt.in_progress || 0) > 0 ? colors.info.main : colors.grey[500] }}>
                        {(mt.in_progress || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        size="small"
                        label={`${mt.success_rate || getSuccessRate(mt)}%`}
                        sx={{
                          backgroundColor: (mt.success_rate || parseFloat(getSuccessRate(mt))) >= 90
                            ? colors.success.light + '40'
                            : (mt.success_rate || parseFloat(getSuccessRate(mt))) >= 70
                              ? colors.warning.light + '40'
                              : colors.error.light + '40',
                          fontWeight: 500,
                          fontSize: 11,
                        }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      {(mt.failed || 0) > 0 ? (
                        <Tooltip title={`${mt.failed} failed records`}>
                          <ErrorIcon sx={{ fontSize: 18, color: colors.error.main }} />
                        </Tooltip>
                      ) : (mt.in_progress || 0) > 0 ? (
                        <Tooltip title={`${mt.in_progress} in progress`}>
                          <Box
                            sx={{
                              width: 18,
                              height: 18,
                              borderRadius: '50%',
                              backgroundColor: colors.info.main,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography variant="caption" sx={{ color: 'white', fontSize: 10 }}>
                              {mt.in_progress}
                            </Typography>
                          </Box>
                        </Tooltip>
                      ) : (
                        <SuccessIcon sx={{ fontSize: 18, color: colors.success.main }} />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {messageTypes.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={9} sx={{ textAlign: 'center', py: 3 }}>
                      <Typography variant="body2" color="text.secondary">
                        No message type data available for the selected time range
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Selected Message Type Flow Detail */}
          {selectedType && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
                {selectedType} Flow Detail
              </Typography>

              {loadingFlow ? (
                <LinearProgress />
              ) : flowData ? (
                <Box>
                  {/* Flow Visualization */}
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 2,
                      mb: 2,
                      p: 2,
                      backgroundColor: colors.grey[50],
                      borderRadius: 2,
                    }}
                  >
                    {/* Bronze */}
                    <Box sx={{ textAlign: 'center', minWidth: 100 }}>
                      <Box
                        sx={{
                          p: 2,
                          backgroundColor: colors.zones.bronze.main + '20',
                          borderRadius: 2,
                          border: `2px solid ${colors.zones.bronze.main}`,
                        }}
                      >
                        <Typography variant="h5" fontWeight={700} sx={{ color: colors.zones.bronze.main }}>
                          {flowData.summary?.bronze?.total || 0}
                        </Typography>
                        <Typography variant="caption">Bronze</Typography>
                      </Box>
                      {flowData.summary?.bronze?.failed > 0 && (
                        <Chip
                          size="small"
                          label={`${flowData.summary.bronze.failed} failed`}
                          color="error"
                          sx={{ mt: 0.5, fontSize: 10 }}
                        />
                      )}
                    </Box>

                    <FlowIcon sx={{ color: colors.grey[400], fontSize: 32 }} />

                    {/* Silver */}
                    <Box sx={{ textAlign: 'center', minWidth: 100 }}>
                      <Box
                        sx={{
                          p: 2,
                          backgroundColor: colors.zones.silver.main + '20',
                          borderRadius: 2,
                          border: `2px solid ${colors.zones.silver.main}`,
                        }}
                      >
                        <Typography variant="h5" fontWeight={700} sx={{ color: colors.zones.silver.dark }}>
                          {flowData.summary?.silver?.total || 0}
                        </Typography>
                        <Typography variant="caption">Silver</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, justifyContent: 'center' }}>
                        <Chip size="small" label={`${flowData.summary?.silver?.dq_passed || 0} pass`} color="success" sx={{ fontSize: 10 }} />
                        {flowData.summary?.silver?.dq_failed > 0 && (
                          <Chip size="small" label={`${flowData.summary.silver.dq_failed} fail`} color="error" sx={{ fontSize: 10 }} />
                        )}
                      </Box>
                    </Box>

                    <FlowIcon sx={{ color: colors.grey[400], fontSize: 32 }} />

                    {/* Gold */}
                    <Box sx={{ textAlign: 'center', minWidth: 100 }}>
                      <Box
                        sx={{
                          p: 2,
                          backgroundColor: colors.zones.gold.main + '20',
                          borderRadius: 2,
                          border: `2px solid ${colors.zones.gold.main}`,
                        }}
                      >
                        <Typography variant="h5" fontWeight={700} sx={{ color: colors.zones.gold.dark }}>
                          {flowData.summary?.gold?.total || 0}
                        </Typography>
                        <Typography variant="caption">Gold</Typography>
                      </Box>
                    </Box>
                  </Box>

                  {/* Rates */}
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 6 }}>
                      <Box sx={{ textAlign: 'center', p: 1, backgroundColor: colors.grey[50], borderRadius: 1 }}>
                        <Typography variant="h6" fontWeight={700} color={colors.success.main}>
                          {flowData.summary?.success_rate || 0}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Success Rate
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Box sx={{ textAlign: 'center', p: 1, backgroundColor: colors.grey[50], borderRadius: 1 }}>
                        <Typography variant="h6" fontWeight={700} color={colors.primary.main}>
                          {flowData.summary?.dq_pass_rate || 0}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          DQ Pass Rate
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              ) : null}
            </>
          )}
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default MessageTypeMetrics;
