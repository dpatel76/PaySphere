/**
 * Record Viewer Component
 * JSON-driven record display that works for any message type
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Divider,
  Chip,
  Skeleton,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { schemaApi } from '../../api/client';
import type { FieldDisplayConfig } from '../../types';
import FieldRenderer from './FieldRenderer';
import { colors } from '../../styles/design-system';

interface RecordViewerProps {
  record: Record<string, unknown>;
  layer: 'bronze' | 'silver' | 'gold' | 'analytics';
  tableName: string;
  messageType?: string;
  compact?: boolean;
}

// Group fields by category
type LayerKey = 'bronze' | 'silver' | 'gold' | 'analytical';

function groupFields(fields: FieldDisplayConfig[]): Record<string, FieldDisplayConfig[]> {
  const groups: Record<string, FieldDisplayConfig[]> = {
    identifiers: [],
    amounts: [],
    parties: [],
    status: [],
    dates: [],
    other: [],
  };

  for (const field of fields) {
    const name = field.field_name.toLowerCase();

    if (name.includes('id') || name.includes('key') || name.includes('ref')) {
      groups.identifiers.push(field);
    } else if (name.includes('amount') || name.includes('sum') || name.includes('rate')) {
      groups.amounts.push(field);
    } else if (name.includes('debtor') || name.includes('creditor') || name.includes('party') || name.includes('name')) {
      groups.parties.push(field);
    } else if (name.includes('status') || name.includes('dq_') || name.includes('processing')) {
      groups.status.push(field);
    } else if (field.data_type === 'date' || field.data_type === 'timestamp' || name.includes('_at')) {
      groups.dates.push(field);
    } else {
      groups.other.push(field);
    }
  }

  return groups;
}

const RecordViewer: React.FC<RecordViewerProps> = ({
  record,
  layer,
  tableName,
  messageType,
  compact = false,
}) => {
  // Fetch display configuration
  const { data: displayConfig, isLoading } = useQuery({
    queryKey: ['tableDisplayConfig', layer, tableName, messageType],
    queryFn: () => schemaApi.getTableDisplayConfig(layer, tableName, messageType),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  if (isLoading) {
    return (
      <Box sx={{ p: 2 }}>
        <Skeleton variant="rectangular" height={200} />
      </Box>
    );
  }

  // If no config, render raw record
  if (!displayConfig) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Record Details
          </Typography>
          <Box
            component="pre"
            sx={{
              p: 2,
              backgroundColor: colors.grey[100],
              borderRadius: 1,
              overflow: 'auto',
              fontSize: 12,
              fontFamily: 'monospace',
            }}
          >
            {JSON.stringify(record, null, 2)}
          </Box>
        </CardContent>
      </Card>
    );
  }

  const { display_columns } = displayConfig;
  const groupedFields = groupFields(display_columns);

  if (compact) {
    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {display_columns.slice(0, 6).map((field: FieldDisplayConfig) => (
          <Box key={field.field_name} sx={{ minWidth: 120 }}>
            <Typography variant="caption" color="text.secondary">
              {field.display_name}
            </Typography>
            <FieldRenderer value={record[field.field_name]} config={field} />
          </Box>
        ))}
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              Record Details
            </Typography>
            <Chip
              label={layer}
              size="small"
              sx={{
                backgroundColor: colors.zones[layer === 'analytics' ? 'analytical' : layer as LayerKey]?.light || colors.grey[200],
                color: colors.zones[layer === 'analytics' ? 'analytical' : layer as LayerKey]?.dark || colors.grey[700],
                fontWeight: 500,
              }}
            />
          </Box>
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }} color="text.secondary">
            {tableName}
          </Typography>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Identifiers Section */}
        {groupedFields.identifiers.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Identifiers
            </Typography>
            <Grid container spacing={2}>
              {groupedFields.identifiers.map((field: FieldDisplayConfig) => (
                <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 4 }}>
                  <FieldItem field={field} value={record[field.field_name]} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Parties Section */}
        {groupedFields.parties.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Parties
            </Typography>
            <Grid container spacing={2}>
              {groupedFields.parties.map((field: FieldDisplayConfig) => (
                <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 4 }}>
                  <FieldItem field={field} value={record[field.field_name]} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Amounts Section */}
        {groupedFields.amounts.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Amounts
            </Typography>
            <Grid container spacing={2}>
              {groupedFields.amounts.map((field: FieldDisplayConfig) => (
                <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 3 }}>
                  <FieldItem field={field} value={record[field.field_name]} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Status Section */}
        {groupedFields.status.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Status
            </Typography>
            <Grid container spacing={2}>
              {groupedFields.status.map((field: FieldDisplayConfig) => (
                <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 3 }}>
                  <FieldItem field={field} value={record[field.field_name]} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Dates Section */}
        {groupedFields.dates.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Dates
            </Typography>
            <Grid container spacing={2}>
              {groupedFields.dates.map((field: FieldDisplayConfig) => (
                <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 3 }}>
                  <FieldItem field={field} value={record[field.field_name]} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Other Fields */}
        {groupedFields.other.length > 0 && (
          <Box>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Other Details
            </Typography>
            <Grid container spacing={2}>
              {groupedFields.other.map((field: FieldDisplayConfig) => (
                <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 4 }}>
                  <FieldItem field={field} value={record[field.field_name]} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

// Individual field display component
const FieldItem: React.FC<{
  field: FieldDisplayConfig;
  value: unknown;
}> = ({ field, value }) => (
  <Box>
    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
      {field.display_name}
    </Typography>
    <FieldRenderer value={value} config={field} />
  </Box>
);

export default RecordViewer;
