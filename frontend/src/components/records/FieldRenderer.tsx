/**
 * Field Renderer Component
 * Renders field values based on their data type and render_type configuration
 */
import React from 'react';
import { Box, Chip, Tooltip, Typography, Link } from '@mui/material';
import type { FieldDisplayConfig } from '../../types';
import { colors } from '../../styles/design-system';

interface FieldRendererProps {
  value: unknown;
  config: FieldDisplayConfig;
}

const FieldRenderer: React.FC<FieldRendererProps> = ({ value, config }) => {
  if (value === null || value === undefined) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
        -
      </Typography>
    );
  }

  const renderType = config.render_type || inferRenderType(config.data_type);

  switch (renderType) {
    case 'currency':
      return renderCurrency(value, config.format);

    case 'date':
      return renderDate(value);

    case 'datetime':
      return renderDateTime(value);

    case 'chip':
      return renderChip(value);

    case 'json':
      return renderJson(value);

    case 'link':
      return renderLink(value);

    case 'text':
    default:
      return renderText(value, config);
  }
};

// Infer render type from data type
function inferRenderType(dataType: string): string {
  const typeMap: Record<string, string> = {
    decimal: 'currency',
    timestamp: 'datetime',
    date: 'date',
    boolean: 'chip',
    json: 'json',
  };
  return typeMap[dataType] || 'text';
}

// Render currency values
function renderCurrency(value: unknown, format?: string): React.ReactElement {
  const numValue = typeof value === 'number' ? value : parseFloat(String(value));
  if (isNaN(numValue)) {
    return <Typography variant="body2">{String(value)}</Typography>;
  }

  const formatted = numValue.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });

  return (
    <Typography
      variant="body2"
      sx={{ fontFamily: 'monospace', textAlign: 'right', fontWeight: 500 }}
    >
      {format ? `${format} ${formatted}` : formatted}
    </Typography>
  );
}

// Render date values
function renderDate(value: unknown): React.ReactElement {
  const dateStr = String(value);
  try {
    const date = new Date(dateStr);
    const formatted = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
    return <Typography variant="body2">{formatted}</Typography>;
  } catch {
    return <Typography variant="body2">{dateStr}</Typography>;
  }
}

// Render datetime values
function renderDateTime(value: unknown): React.ReactElement {
  const dateStr = String(value);
  try {
    const date = new Date(dateStr);
    const formatted = date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
    return (
      <Typography variant="body2" sx={{ fontSize: 12 }}>
        {formatted}
      </Typography>
    );
  } catch {
    return <Typography variant="body2">{dateStr}</Typography>;
  }
}

// Render chip values (for status, boolean, etc.)
function renderChip(value: unknown): React.ReactElement {
  const strValue = String(value);
  const colorMap: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
    // Boolean values
    true: 'success',
    false: 'default',
    // Status values
    COMPLETED: 'success',
    SUCCESS: 'success',
    PASSED: 'success',
    MATCHED: 'success',
    PROCESSED: 'success',
    PROCESSING: 'info',
    PENDING: 'warning',
    IN_PROGRESS: 'info',
    FAILED: 'error',
    ERROR: 'error',
    CRITICAL: 'error',
    WARNING: 'warning',
    NEW: 'info',
    RESOLVED: 'success',
    // DQ status
    DQ_PASSED: 'success',
    DQ_FAILED: 'error',
    VALIDATED: 'success',
  };

  const color = colorMap[strValue.toUpperCase()] || 'default';

  return (
    <Chip
      label={strValue}
      size="small"
      color={color}
      sx={{ fontSize: 11, fontWeight: 500 }}
    />
  );
}

// Render JSON values
function renderJson(value: unknown): React.ReactElement {
  let jsonStr: string;
  try {
    jsonStr = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  } catch {
    jsonStr = String(value);
  }

  const displayStr = jsonStr.length > 100 ? jsonStr.substring(0, 100) + '...' : jsonStr;

  return (
    <Tooltip
      title={
        <Box
          component="pre"
          sx={{
            m: 0,
            maxHeight: 300,
            overflow: 'auto',
            fontSize: 11,
            fontFamily: 'monospace',
          }}
        >
          {jsonStr}
        </Box>
      }
    >
      <Box
        sx={{
          p: 0.5,
          backgroundColor: colors.grey[100],
          borderRadius: 1,
          fontFamily: 'monospace',
          fontSize: 11,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: 200,
        }}
      >
        {displayStr}
      </Box>
    </Tooltip>
  );
}

// Render link values
function renderLink(value: unknown): React.ReactElement {
  const strValue = String(value);
  if (!strValue.startsWith('http')) {
    return <Typography variant="body2">{strValue}</Typography>;
  }

  return (
    <Link href={strValue} target="_blank" rel="noopener noreferrer" sx={{ fontSize: 14 }}>
      {strValue.length > 50 ? strValue.substring(0, 50) + '...' : strValue}
    </Link>
  );
}

// Render text values
function renderText(value: unknown, config: FieldDisplayConfig): React.ReactElement {
  const strValue = String(value);
  const maxLength = config.width ? Math.floor(config.width / 8) : 50;

  if (strValue.length > maxLength) {
    return (
      <Tooltip title={strValue}>
        <Typography
          variant="body2"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {strValue}
        </Typography>
      </Tooltip>
    );
  }

  return <Typography variant="body2">{strValue}</Typography>;
}

export default FieldRenderer;
