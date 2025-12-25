/**
 * Batch Records Tab
 * Displays paginated records for a batch with layer selector
 */
import React, { useState, useMemo } from 'react';
import {
  Box,
  ToggleButtonGroup,
  ToggleButton,
  Typography,
  Chip,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridPaginationModel,
} from '@mui/x-data-grid';
import { useQuery } from '@tanstack/react-query';
import { pipelineApi } from '../../../api/client';
import { colors } from '../../../styles/design-system';

interface BatchRecordsTabProps {
  batchId: string;
  messageType: string;
}

type LayerType = 'bronze' | 'silver' | 'gold';

// Status color mapping
const statusColors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  PROCESSED: 'success',
  PROMOTED: 'success',
  PENDING: 'warning',
  FAILED: 'error',
  VALIDATED: 'info',
  DQ_PASSED: 'success',
  DQ_FAILED: 'error',
};

const BatchRecordsTab: React.FC<BatchRecordsTabProps> = ({ batchId, messageType }) => {
  const [selectedLayer, setSelectedLayer] = useState<LayerType>('bronze');
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 25,
  });

  // Fetch records for selected layer
  const { data, isLoading } = useQuery({
    queryKey: ['batchRecords', batchId, selectedLayer, paginationModel],
    queryFn: async () => {
      const records = await pipelineApi.getBatchRecords(
        batchId,
        selectedLayer,
        paginationModel.pageSize,
        paginationModel.page * paginationModel.pageSize
      );
      return {
        items: records,
        total: records.length, // Backend should return total count
      };
    },
    enabled: !!batchId,
  });

  const handleLayerChange = (
    _event: React.MouseEvent<HTMLElement>,
    newLayer: LayerType | null
  ) => {
    if (newLayer) {
      setSelectedLayer(newLayer);
      setPaginationModel({ ...paginationModel, page: 0 });
    }
  };

  // Dynamic columns based on layer
  const columns: GridColDef[] = useMemo(() => {
    const baseColumns: GridColDef[] = [];

    if (selectedLayer === 'bronze') {
      baseColumns.push(
        {
          field: 'raw_id',
          headerName: 'Raw ID',
          width: 140,
          renderCell: (params: GridRenderCellParams) => (
            <Tooltip title={params.value}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                {params.value?.substring(0, 12)}...
              </Typography>
            </Tooltip>
          ),
        },
        {
          field: 'message_type',
          headerName: 'Message Type',
          width: 120,
        },
        {
          field: 'message_format',
          headerName: 'Format',
          width: 80,
        },
        {
          field: 'source_system',
          headerName: 'Source',
          width: 100,
        },
        {
          field: 'processing_status',
          headerName: 'Status',
          width: 120,
          renderCell: (params: GridRenderCellParams) => (
            <Chip
              label={params.value}
              size="small"
              color={statusColors[params.value] || 'default'}
              sx={{ fontSize: 11 }}
            />
          ),
        },
        {
          field: 'ingested_at',
          headerName: 'Ingested At',
          width: 160,
          valueFormatter: (value: string) =>
            value ? new Date(value).toLocaleString() : '-',
        }
      );
    } else if (selectedLayer === 'silver') {
      baseColumns.push(
        {
          field: 'stg_id',
          headerName: 'Staging ID',
          width: 140,
          renderCell: (params: GridRenderCellParams) => (
            <Tooltip title={params.value}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                {params.value?.substring(0, 12)}...
              </Typography>
            </Tooltip>
          ),
        },
        {
          field: 'msg_id',
          headerName: 'Message ID',
          width: 120,
        },
        {
          field: 'instructed_amount',
          headerName: 'Amount',
          width: 120,
          type: 'number',
          align: 'right',
          headerAlign: 'right',
          valueFormatter: (value: number) =>
            value ? value.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '-',
        },
        {
          field: 'instructed_currency',
          headerName: 'Ccy',
          width: 60,
        },
        {
          field: 'debtor_name',
          headerName: 'Debtor',
          width: 150,
        },
        {
          field: 'creditor_name',
          headerName: 'Creditor',
          width: 150,
        },
        {
          field: 'dq_status',
          headerName: 'DQ Status',
          width: 100,
          renderCell: (params: GridRenderCellParams) => (
            <Chip
              label={params.value}
              size="small"
              color={statusColors[params.value] || 'default'}
              sx={{ fontSize: 11 }}
            />
          ),
        },
        {
          field: 'dq_score',
          headerName: 'DQ Score',
          width: 90,
          type: 'number',
          align: 'right',
          headerAlign: 'right',
          renderCell: (params: GridRenderCellParams) => {
            const score = params.value as number | undefined;
            if (score === undefined) return '-';
            const color = score >= 0.9 ? 'success' : score >= 0.7 ? 'warning' : 'error';
            return (
              <Chip
                label={`${(score * 100).toFixed(0)}%`}
                size="small"
                color={color}
                sx={{ fontSize: 11 }}
              />
            );
          },
        }
      );
    } else if (selectedLayer === 'gold') {
      baseColumns.push(
        {
          field: 'instruction_id',
          headerName: 'Instruction ID',
          width: 140,
          renderCell: (params: GridRenderCellParams) => (
            <Tooltip title={params.value}>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                {params.value?.substring(0, 12)}...
              </Typography>
            </Tooltip>
          ),
        },
        {
          field: 'payment_id',
          headerName: 'Payment ID',
          width: 130,
        },
        {
          field: 'payment_type',
          headerName: 'Type',
          width: 100,
        },
        {
          field: 'instructed_amount',
          headerName: 'Amount',
          width: 120,
          type: 'number',
          align: 'right',
          headerAlign: 'right',
          valueFormatter: (value: number) =>
            value ? value.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '-',
        },
        {
          field: 'instructed_currency',
          headerName: 'Ccy',
          width: 60,
        },
        {
          field: 'source_message_type',
          headerName: 'Source Type',
          width: 110,
        },
        {
          field: 'dq_status',
          headerName: 'DQ Status',
          width: 100,
          renderCell: (params: GridRenderCellParams) => (
            <Chip
              label={params.value}
              size="small"
              color={statusColors[params.value] || 'default'}
              sx={{ fontSize: 11 }}
            />
          ),
        },
        {
          field: 'reconciliation_status',
          headerName: 'Recon Status',
          width: 110,
          renderCell: (params: GridRenderCellParams) => (
            <Chip
              label={params.value || 'N/A'}
              size="small"
              color={params.value === 'MATCHED' ? 'success' : params.value === 'MISMATCHED' ? 'error' : 'default'}
              sx={{ fontSize: 11 }}
            />
          ),
        },
        {
          field: 'created_at',
          headerName: 'Created At',
          width: 160,
          valueFormatter: (value: string) =>
            value ? new Date(value).toLocaleString() : '-',
        }
      );
    }

    return baseColumns;
  }, [selectedLayer]);

  // Get row ID based on layer
  const getRowId = (row: Record<string, unknown>): string => {
    if (selectedLayer === 'bronze') return row.raw_id as string;
    if (selectedLayer === 'silver') return row.stg_id as string;
    return row.instruction_id as string;
  };

  return (
    <Box>
      {/* Layer Selector */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Layer:
        </Typography>
        <ToggleButtonGroup
          value={selectedLayer}
          exclusive
          onChange={handleLayerChange}
          size="small"
        >
          <ToggleButton
            value="bronze"
            sx={{
              '&.Mui-selected': {
                backgroundColor: colors.zones.bronze.light,
                color: colors.zones.bronze.dark,
                '&:hover': {
                  backgroundColor: colors.zones.bronze.light,
                },
              },
            }}
          >
            Bronze
          </ToggleButton>
          <ToggleButton
            value="silver"
            sx={{
              '&.Mui-selected': {
                backgroundColor: colors.zones.silver.light,
                color: colors.zones.silver.dark,
                '&:hover': {
                  backgroundColor: colors.zones.silver.light,
                },
              },
            }}
          >
            Silver
          </ToggleButton>
          <ToggleButton
            value="gold"
            sx={{
              '&.Mui-selected': {
                backgroundColor: colors.zones.gold.light,
                color: colors.zones.gold.dark,
                '&:hover': {
                  backgroundColor: colors.zones.gold.light,
                },
              },
            }}
          >
            Gold
          </ToggleButton>
        </ToggleButtonGroup>
        <Chip
          label={messageType}
          size="small"
          sx={{
            ml: 'auto',
            backgroundColor: colors.primary.light + '30',
            fontWeight: 500,
          }}
        />
      </Box>

      {/* Records DataGrid */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <DataGrid
          rows={data?.items || []}
          columns={columns}
          getRowId={getRowId}
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
        />
      )}

      {/* Empty State */}
      {!isLoading && (!data?.items || data.items.length === 0) && (
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No records found in {selectedLayer} layer for this batch
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default BatchRecordsTab;
