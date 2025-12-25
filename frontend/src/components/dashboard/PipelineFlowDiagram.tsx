/**
 * Pipeline Flow Diagram Component
 * Visual representation of Bronze -> Silver -> Gold -> Analytical flow
 */
import React from 'react';
import { Box, Paper, Typography, Chip, LinearProgress, Tooltip } from '@mui/material';
import {
  ArrowForward as ArrowIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
} from '@mui/icons-material';
import { colors, pipelineConfig } from '../../styles/design-system';

interface LayerStats {
  total: number;
  processed: number;
  failed: number;
  pending: number;
  dqPassed?: number;
  dqFailed?: number;
}

interface PipelineFlowDiagramProps {
  bronze: LayerStats;
  silver: LayerStats;
  gold: LayerStats;
  analytical?: LayerStats;
  onLayerClick?: (layer: string) => void;
}

const LayerCard: React.FC<{
  layer: 'bronze' | 'silver' | 'gold' | 'analytical';
  stats: LayerStats;
  onClick?: () => void;
}> = ({ layer, stats, onClick }) => {
  const layerColor = colors.zones[layer];
  const successRate = stats.total > 0 ? ((stats.processed / stats.total) * 100).toFixed(1) : 0;

  return (
    <Paper
      elevation={2}
      onClick={onClick}
      sx={{
        p: 2,
        minWidth: 180,
        cursor: onClick ? 'pointer' : 'default',
        border: `2px solid ${layerColor.main}`,
        borderRadius: 2,
        transition: 'all 0.2s ease',
        '&:hover': onClick ? {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${layerColor.main}40`,
        } : {},
      }}
    >
      {/* Layer Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
        <Box
          sx={{
            width: 12,
            height: 12,
            borderRadius: '50%',
            backgroundColor: layerColor.main,
            mr: 1,
          }}
        />
        <Typography variant="h6" sx={{ fontWeight: 600, color: layerColor.dark }}>
          {pipelineConfig.layerNames[layer]}
        </Typography>
      </Box>

      {/* Stats */}
      <Box sx={{ mb: 1.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" color="text.secondary">Total</Typography>
          <Typography variant="body2" fontWeight={600}>{stats.total.toLocaleString()}</Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" color="text.secondary">Processed</Typography>
          <Typography variant="body2" fontWeight={600} color="success.main">
            {stats.processed.toLocaleString()}
          </Typography>
        </Box>
        {stats.failed > 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">Failed</Typography>
            <Typography variant="body2" fontWeight={600} color="error.main">
              {stats.failed.toLocaleString()}
            </Typography>
          </Box>
        )}
        {stats.pending > 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">Pending</Typography>
            <Typography variant="body2" fontWeight={600} color="warning.main">
              {stats.pending.toLocaleString()}
            </Typography>
          </Box>
        )}
      </Box>

      {/* DQ Stats for Silver */}
      {stats.dqPassed !== undefined && (
        <Box sx={{ mb: 1.5, pt: 1, borderTop: `1px solid ${colors.grey[200]}` }}>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
            Data Quality
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Chip
              size="small"
              icon={<SuccessIcon sx={{ fontSize: 14 }} />}
              label={stats.dqPassed}
              color="success"
              variant="outlined"
              sx={{ fontSize: 11 }}
            />
            <Chip
              size="small"
              icon={<ErrorIcon sx={{ fontSize: 14 }} />}
              label={stats.dqFailed}
              color="error"
              variant="outlined"
              sx={{ fontSize: 11 }}
            />
          </Box>
        </Box>
      )}

      {/* Progress Bar */}
      <Box>
        <LinearProgress
          variant="determinate"
          value={Number(successRate)}
          sx={{
            height: 6,
            borderRadius: 3,
            backgroundColor: colors.grey[200],
            '& .MuiLinearProgress-bar': {
              backgroundColor: layerColor.main,
              borderRadius: 3,
            },
          }}
        />
        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
          {successRate}% processed
        </Typography>
      </Box>
    </Paper>
  );
};

const FlowArrow: React.FC<{ success: number; failed: number }> = ({ success, failed }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      mx: 2,
    }}
  >
    <ArrowIcon sx={{ fontSize: 32, color: colors.primary.main }} />
    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
      <Tooltip title={`${success} promoted`}>
        <Chip
          size="small"
          label={success}
          color="success"
          sx={{ height: 20, fontSize: 10 }}
        />
      </Tooltip>
      {failed > 0 && (
        <Tooltip title={`${failed} failed`}>
          <Chip
            size="small"
            label={failed}
            color="error"
            sx={{ height: 20, fontSize: 10 }}
          />
        </Tooltip>
      )}
    </Box>
  </Box>
);

const PipelineFlowDiagram: React.FC<PipelineFlowDiagramProps> = ({
  bronze,
  silver,
  gold,
  analytical,
  onLayerClick,
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
        overflowX: 'auto',
      }}
    >
      <LayerCard
        layer="bronze"
        stats={bronze}
        onClick={onLayerClick ? () => onLayerClick('bronze') : undefined}
      />
      <FlowArrow success={silver.processed} failed={bronze.failed} />
      <LayerCard
        layer="silver"
        stats={silver}
        onClick={onLayerClick ? () => onLayerClick('silver') : undefined}
      />
      <FlowArrow success={gold.processed} failed={silver.failed} />
      <LayerCard
        layer="gold"
        stats={gold}
        onClick={onLayerClick ? () => onLayerClick('gold') : undefined}
      />
      {analytical && (
        <>
          <FlowArrow success={analytical.processed} failed={gold.failed} />
          <LayerCard
            layer="analytical"
            stats={analytical}
            onClick={onLayerClick ? () => onLayerClick('analytical') : undefined}
          />
        </>
      )}
    </Box>
  );
};

export default PipelineFlowDiagram;
