/**
 * Throughput Chart Component
 * Shows pipeline throughput over time using Recharts
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
  ToggleButton,
  ToggleButtonGroup,
  Grid,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
  BarChart,
  Bar,
} from 'recharts';
import { pipelineApi } from '../../api/client';
import { colors } from '../../styles/design-system';

interface ThroughputChartProps {
  defaultHoursBack?: number;
}

const ThroughputChart: React.FC<ThroughputChartProps> = ({ defaultHoursBack = 24 }) => {
  const [hoursBack, setHoursBack] = useState(defaultHoursBack);
  const [chartType, setChartType] = useState<'area' | 'bar'>('area');

  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['throughput', hoursBack],
    queryFn: () => pipelineApi.getThroughput(hoursBack),
    refetchInterval: 60000, // Refresh every minute
  });

  const throughputData = (data?.throughput || []).map((item: any) => ({
    ...item,
    time: new Date(item.time_bucket).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    date: new Date(item.time_bucket).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    records_ingested: item.records_ingested || 0,
    records_promoted: item.records_promoted || 0,
    errors: item.errors || 0,
    latency: Math.round(item.avg_latency_seconds || 0),
  }));

  // Summary stats
  const totalIngested = throughputData.reduce((sum: number, d: any) => sum + d.records_ingested, 0);
  const totalPromoted = throughputData.reduce((sum: number, d: any) => sum + d.records_promoted, 0);
  const totalErrors = throughputData.reduce((sum: number, d: any) => sum + d.errors, 0);
  const avgLatency = throughputData.length > 0
    ? Math.round(throughputData.reduce((sum: number, d: any) => sum + d.latency, 0) / throughputData.length)
    : 0;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: 'white',
            p: 1.5,
            border: `1px solid ${colors.grey[200]}`,
            borderRadius: 1,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          }}
        >
          <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: entry.color }} />
              <Typography variant="caption">
                {entry.name}: {entry.value.toLocaleString()}
              </Typography>
            </Box>
          ))}
        </Box>
      );
    }
    return null;
  };

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingIcon sx={{ color: colors.primary.main }} />
            <Typography variant="h6" fontWeight={600}>
              Pipeline Throughput
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ToggleButtonGroup
              size="small"
              value={hoursBack}
              exclusive
              onChange={(_, value) => value && setHoursBack(value)}
            >
              <ToggleButton value={6}>6h</ToggleButton>
              <ToggleButton value={24}>24h</ToggleButton>
              <ToggleButton value={72}>3d</ToggleButton>
              <ToggleButton value={168}>7d</ToggleButton>
            </ToggleButtonGroup>
            <ToggleButtonGroup
              size="small"
              value={chartType}
              exclusive
              onChange={(_, value) => value && setChartType(value)}
            >
              <ToggleButton value="area">Area</ToggleButton>
              <ToggleButton value="bar">Bar</ToggleButton>
            </ToggleButtonGroup>
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={() => refetch()} disabled={isRefetching}>
                <RefreshIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Summary Stats */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: colors.zones.bronze.main + '10', borderRadius: 1 }}>
              <Typography variant="h6" fontWeight={700} sx={{ color: colors.zones.bronze.main }}>
                {totalIngested.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Records Ingested
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: colors.zones.gold.main + '10', borderRadius: 1 }}>
              <Typography variant="h6" fontWeight={700} sx={{ color: colors.zones.gold.dark }}>
                {totalPromoted.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                To Gold
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: colors.error.main + '10', borderRadius: 1 }}>
              <Typography variant="h6" fontWeight={700} sx={{ color: colors.error.main }}>
                {totalErrors.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Errors
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <Box sx={{ textAlign: 'center', p: 1, backgroundColor: colors.info.main + '10', borderRadius: 1 }}>
              <Typography variant="h6" fontWeight={700} sx={{ color: colors.info.main }}>
                {avgLatency}s
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Avg Latency
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {isLoading && <LinearProgress sx={{ mb: 2 }} />}

        {/* Chart */}
        <Box sx={{ height: 300, width: '100%' }}>
          {throughputData.length > 0 ? (
            <ResponsiveContainer>
              {chartType === 'area' ? (
                <AreaChart data={throughputData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.grey[200]} />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: colors.grey[300] }}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: colors.grey[300] }}
                    tickFormatter={(value) => value.toLocaleString()}
                  />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Legend
                    wrapperStyle={{ fontSize: 12 }}
                    iconType="circle"
                  />
                  <Area
                    type="monotone"
                    dataKey="records_ingested"
                    name="Ingested"
                    stroke={colors.zones.bronze.main}
                    fill={colors.zones.bronze.main}
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="records_promoted"
                    name="To Gold"
                    stroke={colors.zones.gold.dark}
                    fill={colors.zones.gold.main}
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="errors"
                    name="Errors"
                    stroke={colors.error.main}
                    fill={colors.error.light}
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                </AreaChart>
              ) : (
                <BarChart data={throughputData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.grey[200]} />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: colors.grey[300] }}
                  />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={{ stroke: colors.grey[300] }}
                    tickFormatter={(value) => value.toLocaleString()}
                  />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Legend
                    wrapperStyle={{ fontSize: 12 }}
                    iconType="circle"
                  />
                  <Bar dataKey="records_ingested" name="Ingested" fill={colors.zones.bronze.main} />
                  <Bar dataKey="records_promoted" name="To Gold" fill={colors.zones.gold.main} />
                  <Bar dataKey="errors" name="Errors" fill={colors.error.main} />
                </BarChart>
              )}
            </ResponsiveContainer>
          ) : (
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: colors.grey[50],
                borderRadius: 1,
              }}
            >
              <Typography variant="body2" color="text.secondary">
                No throughput data available for the selected time range
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ThroughputChart;
