/**
 * Batch Tracking Table Component
 * Displays batch processing metrics across all zones
 */
import React, { useState, useMemo } from 'react';
import { Box, Chip, IconButton, Tooltip, Typography } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridColumnGroupingModel,
  GridPaginationModel,
} from '@mui/x-data-grid';
import {
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { pipelineApi } from '../../api/client';
import type { BatchTrackingExtended, PaginatedResponse } from '../../types';
import { colors } from '../../styles/design-system';
import { DateRange, dateRangeToHoursBack } from '../dashboard/DateRangeFilter';

interface BatchTrackingTableProps {
  dateRange: DateRange;
  onViewBatch?: (batchId: string) => void;
}

// Status color mapping
const statusColors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  COMPLETED: 'success',
  PROCESSING: 'info',
  PENDING: 'warning',
  FAILED: 'error',
  PARTIAL: 'warning',
};

// Zone header styles
const zoneHeaderStyles = {
  bronze: {
    backgroundColor: colors.zones.bronze.light,
    color: colors.zones.bronze.dark,
  },
  silver: {
    backgroundColor: colors.zones.silver.light,
    color: colors.zones.silver.dark,
  },
  gold: {
    backgroundColor: colors.zones.gold.light,
    color: colors.zones.gold.dark,
  },
  analytical: {
    backgroundColor: colors.zones.analytical.light,
    color: colors.zones.analytical.dark,
  },
};

const BatchTrackingTable: React.FC<BatchTrackingTableProps> = ({
  dateRange,
  onViewBatch,
}) => {
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 25,
  });

  // Fetch batches with pagination
  const { data, isLoading, refetch } = useQuery<PaginatedResponse<BatchTrackingExtended>>({
    queryKey: ['batchesExtended', dateRange, paginationModel],
    queryFn: async () => {
      const hoursBack = dateRangeToHoursBack(dateRange);
      const response = await pipelineApi.getBatches({
        hours_back: hoursBack,
        limit: paginationModel.pageSize,
      });

      // Transform response to extended format
      // The backend should return extended format, but for now we'll transform
      const items: BatchTrackingExtended[] = response.map((batch) => ({
        ...batch,
        created_at: batch.started_at,
        bronze_input: batch.bronze_records || 0,
        bronze_processed: batch.bronze_records || 0,
        bronze_exceptions: 0,
        silver_input: batch.bronze_records || 0,
        silver_processed: batch.silver_records || 0,
        silver_exceptions: 0,
        gold_input: batch.silver_records || 0,
        gold_processed: batch.gold_records || 0,
        gold_exceptions: 0,
        analytics_input: batch.gold_records || 0,
        analytics_processed: 0,
        analytics_exceptions: 0,
      }));

      return {
        items,
        total: items.length,
        page: paginationModel.page + 1,
        page_size: paginationModel.pageSize,
        total_pages: 1,
      };
    },
    refetchInterval: 30000,
  });

  // Column definitions
  const columns: GridColDef[] = useMemo(() => [
    {
      field: 'created_at',
      headerName: 'Date',
      width: 150,
      valueFormatter: (value: string) =>
        new Date(value).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        }),
    },
    {
      field: 'batch_id',
      headerName: 'Batch ID',
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 12 }}>
            {params.value?.substring(0, 8)}...
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'source_system',
      headerName: 'Source',
      width: 100,
    },
    {
      field: 'message_type',
      headerName: 'Type',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          sx={{
            backgroundColor: colors.primary.light + '30',
            color: colors.primary.dark,
            fontWeight: 500,
            fontSize: 11,
          }}
        />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          color={statusColors[params.value] || 'default'}
          sx={{ fontWeight: 600, fontSize: 11 }}
        />
      ),
    },
    // Bronze columns
    {
      field: 'bronze_input',
      headerName: 'Input',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'bronze_processed',
      headerName: 'Proc',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'bronze_exceptions',
      headerName: 'Exc',
      width: 60,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
      renderCell: (params: GridRenderCellParams) => (
        <Typography
          variant="body2"
          color={params.value > 0 ? 'error' : 'text.secondary'}
          fontWeight={params.value > 0 ? 600 : 400}
        >
          {params.value}
        </Typography>
      ),
    },
    // Silver columns
    {
      field: 'silver_input',
      headerName: 'Input',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'silver_processed',
      headerName: 'Proc',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'silver_exceptions',
      headerName: 'Exc',
      width: 60,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
      renderCell: (params: GridRenderCellParams) => (
        <Typography
          variant="body2"
          color={params.value > 0 ? 'error' : 'text.secondary'}
          fontWeight={params.value > 0 ? 600 : 400}
        >
          {params.value}
        </Typography>
      ),
    },
    // Gold columns
    {
      field: 'gold_input',
      headerName: 'Input',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'gold_processed',
      headerName: 'Proc',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'gold_exceptions',
      headerName: 'Exc',
      width: 60,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
      renderCell: (params: GridRenderCellParams) => (
        <Typography
          variant="body2"
          color={params.value > 0 ? 'error' : 'text.secondary'}
          fontWeight={params.value > 0 ? 600 : 400}
        >
          {params.value}
        </Typography>
      ),
    },
    // Analytics columns
    {
      field: 'analytics_input',
      headerName: 'Input',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'analytics_processed',
      headerName: 'Proc',
      width: 70,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
    },
    {
      field: 'analytics_exceptions',
      headerName: 'Exc',
      width: 60,
      type: 'number',
      align: 'right',
      headerAlign: 'right',
      renderCell: (params: GridRenderCellParams) => (
        <Typography
          variant="body2"
          color={params.value > 0 ? 'error' : 'text.secondary'}
          fontWeight={params.value > 0 ? 600 : 400}
        >
          {params.value}
        </Typography>
      ),
    },
    // Actions
    {
      field: 'actions',
      headerName: 'Actions',
      width: 80,
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => onViewBatch?.(params.row.batch_id)}
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ], [onViewBatch]);

  // Column grouping for zone headers
  const columnGroupingModel: GridColumnGroupingModel = useMemo(() => [
    {
      groupId: 'bronze',
      headerName: 'Bronze',
      headerAlign: 'center' as const,
      children: [
        { field: 'bronze_input' },
        { field: 'bronze_processed' },
        { field: 'bronze_exceptions' },
      ],
      renderHeaderGroup: () => (
        <Box
          sx={{
            ...zoneHeaderStyles.bronze,
            px: 2,
            py: 0.5,
            borderRadius: 1,
            fontWeight: 600,
          }}
        >
          Bronze
        </Box>
      ),
    },
    {
      groupId: 'silver',
      headerName: 'Silver',
      headerAlign: 'center' as const,
      children: [
        { field: 'silver_input' },
        { field: 'silver_processed' },
        { field: 'silver_exceptions' },
      ],
      renderHeaderGroup: () => (
        <Box
          sx={{
            ...zoneHeaderStyles.silver,
            px: 2,
            py: 0.5,
            borderRadius: 1,
            fontWeight: 600,
          }}
        >
          Silver
        </Box>
      ),
    },
    {
      groupId: 'gold',
      headerName: 'Gold',
      headerAlign: 'center' as const,
      children: [
        { field: 'gold_input' },
        { field: 'gold_processed' },
        { field: 'gold_exceptions' },
      ],
      renderHeaderGroup: () => (
        <Box
          sx={{
            ...zoneHeaderStyles.gold,
            px: 2,
            py: 0.5,
            borderRadius: 1,
            fontWeight: 600,
          }}
        >
          Gold
        </Box>
      ),
    },
    {
      groupId: 'analytics',
      headerName: 'Analytics',
      headerAlign: 'center' as const,
      children: [
        { field: 'analytics_input' },
        { field: 'analytics_processed' },
        { field: 'analytics_exceptions' },
      ],
      renderHeaderGroup: () => (
        <Box
          sx={{
            ...zoneHeaderStyles.analytical,
            px: 2,
            py: 0.5,
            borderRadius: 1,
            fontWeight: 600,
          }}
        >
          Analytics
        </Box>
      ),
    },
  ], []);

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header with Refresh */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={600}>
          Batch Processing History
        </Typography>
        <IconButton onClick={() => refetch()} size="small">
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Data Grid */}
      <DataGrid
        rows={data?.items || []}
        columns={columns}
        columnGroupingModel={columnGroupingModel}
        getRowId={(row) => row.batch_id}
        loading={isLoading}
        paginationModel={paginationModel}
        onPaginationModelChange={setPaginationModel}
        pageSizeOptions={[10, 25, 50]}
        rowCount={data?.total || 0}
        paginationMode="client"
        disableRowSelectionOnClick
        autoHeight
        sx={{
          border: 'none',
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: colors.grey[50],
            borderBottom: `2px solid ${colors.grey[200]}`,
          },
          '& .MuiDataGrid-cell': {
            borderBottom: `1px solid ${colors.grey[100]}`,
          },
          '& .MuiDataGrid-row:hover': {
            backgroundColor: colors.grey[50],
          },
          '& .MuiDataGrid-columnHeaderTitle': {
            fontWeight: 600,
            fontSize: 12,
          },
        }}
        initialState={{
          sorting: {
            sortModel: [{ field: 'created_at', sort: 'desc' }],
          },
        }}
      />
    </Box>
  );
};

export default BatchTrackingTable;
