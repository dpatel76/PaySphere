/**
 * Record Editor Component
 * JSON-driven record edit form that works for any message type
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  TextField,
  Button,
  Divider,
  Chip,
  FormControlLabel,
  Checkbox,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { schemaApi, reprocessApi } from '../../api/client';
import type { FieldDisplayConfig, ValidationConfig } from '../../types';
import { colors } from '../../styles/design-system';

interface RecordEditorProps {
  record: Record<string, unknown>;
  layer: 'bronze' | 'silver' | 'gold';
  tableName: string;
  messageType?: string;
  recordId: string;
  onSave?: (updatedRecord: Record<string, unknown>) => void;
  onCancel?: () => void;
}

interface FieldState {
  value: unknown;
  error?: string;
  touched: boolean;
}

const RecordEditor: React.FC<RecordEditorProps> = ({
  record,
  layer,
  tableName,
  messageType,
  recordId,
  onSave,
  onCancel,
}) => {
  const [formState, setFormState] = useState<Record<string, FieldState>>({});
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch display configuration
  const { data: displayConfig, isLoading } = useQuery({
    queryKey: ['tableDisplayConfig', layer, tableName, messageType],
    queryFn: () => schemaApi.getTableDisplayConfig(layer, tableName, messageType),
    staleTime: 5 * 60 * 1000,
  });

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: async (updates: Record<string, unknown>) => {
      return reprocessApi.updateRecord(layer, tableName, recordId, updates, true);
    },
    onSuccess: (result) => {
      onSave?.(result);
    },
  });

  // Initialize form state from record
  useEffect(() => {
    const initialState: Record<string, FieldState> = {};
    for (const [key, value] of Object.entries(record)) {
      initialState[key] = { value, touched: false };
    }
    setFormState(initialState);
    setHasChanges(false);
  }, [record]);

  const handleFieldChange = (fieldName: string, value: unknown) => {
    setFormState((prev) => ({
      ...prev,
      [fieldName]: { ...prev[fieldName], value, touched: true },
    }));
    setHasChanges(true);
  };

  const validateField = (field: FieldDisplayConfig, value: unknown): string | undefined => {
    const validation = field.validation;
    if (!validation) return undefined;

    if (validation.required && (value === null || value === undefined || value === '')) {
      return `${field.display_name} is required`;
    }

    if (validation.max_length && typeof value === 'string' && value.length > validation.max_length) {
      return `${field.display_name} cannot exceed ${validation.max_length} characters`;
    }

    if (validation.pattern && typeof value === 'string') {
      const regex = new RegExp(validation.pattern);
      if (!regex.test(value)) {
        return `${field.display_name} has invalid format`;
      }
    }

    if (validation.min !== undefined && typeof value === 'number' && value < validation.min) {
      return `${field.display_name} must be at least ${validation.min}`;
    }

    if (validation.max !== undefined && typeof value === 'number' && value > validation.max) {
      return `${field.display_name} cannot exceed ${validation.max}`;
    }

    return undefined;
  };

  const handleSave = () => {
    if (!displayConfig) return;

    // Validate all editable fields
    const errors: Record<string, string> = {};
    const updates: Record<string, unknown> = {};

    for (const field of displayConfig.display_columns) {
      const state = formState[field.field_name];
      if (!state) continue;

      const error = validateField(field, state.value);
      if (error) {
        errors[field.field_name] = error;
      }

      // Only include changed values
      if (state.value !== record[field.field_name]) {
        updates[field.field_name] = state.value;
      }
    }

    if (Object.keys(errors).length > 0) {
      // Update form state with errors
      setFormState((prev) => {
        const newState = { ...prev };
        for (const [field, error] of Object.entries(errors)) {
          newState[field] = { ...newState[field], error };
        }
        return newState;
      });
      return;
    }

    if (Object.keys(updates).length > 0) {
      saveMutation.mutate(updates);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // If no config, show raw JSON editor
  if (!displayConfig) {
    return (
      <Card>
        <CardContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            No schema configuration found. Editing is not available.
          </Alert>
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

  const editableFields = displayConfig.editable_fields || [];
  const columns = displayConfig.display_columns;

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              Edit Record
            </Typography>
            <Chip
              label={layer}
              size="small"
              sx={{
                backgroundColor: colors.zones[layer]?.light || colors.grey[200],
                color: colors.zones[layer]?.dark || colors.grey[700],
                fontWeight: 500,
              }}
            />
          </Box>
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }} color="text.secondary">
            {recordId}
          </Typography>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Error Alert */}
        {saveMutation.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Failed to save changes: {(saveMutation.error as Error).message}
          </Alert>
        )}

        {/* Form Fields */}
        <Grid container spacing={2}>
          {columns.map((field: FieldDisplayConfig) => {
            const state = formState[field.field_name] || { value: record[field.field_name], touched: false };
            const isEditable = editableFields.length === 0 || editableFields.includes(field.field_name);
            const isReadOnly = field.field_name.endsWith('_id') || field.field_name === 'batch_id';

            return (
              <Grid key={field.field_name} size={{ xs: 12, sm: 6, md: 4 }}>
                <FieldEditor
                  field={field}
                  value={state.value}
                  error={state.error}
                  disabled={!isEditable || isReadOnly}
                  onChange={(value) => handleFieldChange(field.field_name, value)}
                />
              </Grid>
            );
          })}
        </Grid>

        {/* Action Buttons */}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<CancelIcon />}
            onClick={onCancel}
            disabled={saveMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            disabled={!hasChanges || saveMutation.isPending}
          >
            {saveMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

// Individual field editor component
interface FieldEditorProps {
  field: FieldDisplayConfig;
  value: unknown;
  error?: string;
  disabled: boolean;
  onChange: (value: unknown) => void;
}

const FieldEditor: React.FC<FieldEditorProps> = ({ field, value, error, disabled, onChange }) => {
  const { data_type, render_type, display_name, enum_values } = field;

  // Boolean fields
  if (data_type === 'boolean' || render_type === 'chip') {
    if (enum_values && enum_values.length > 0) {
      return (
        <FormControl fullWidth size="small" disabled={disabled} error={!!error}>
          <InputLabel>{display_name}</InputLabel>
          <Select
            value={String(value || '')}
            label={display_name}
            onChange={(e) => onChange(e.target.value)}
          >
            {enum_values.map((opt) => (
              <MenuItem key={opt} value={opt}>
                {opt}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      );
    }

    return (
      <FormControlLabel
        control={
          <Checkbox
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
            disabled={disabled}
          />
        }
        label={display_name}
      />
    );
  }

  // Enum/select fields
  if (enum_values && enum_values.length > 0) {
    return (
      <FormControl fullWidth size="small" disabled={disabled} error={!!error}>
        <InputLabel>{display_name}</InputLabel>
        <Select
          value={String(value || '')}
          label={display_name}
          onChange={(e) => onChange(e.target.value)}
        >
          {enum_values.map((opt) => (
            <MenuItem key={opt} value={opt}>
              {opt}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  }

  // Number fields
  if (data_type === 'decimal' || data_type === 'integer' || data_type === 'number') {
    return (
      <TextField
        fullWidth
        size="small"
        label={display_name}
        type="number"
        value={value ?? ''}
        onChange={(e) => {
          const numValue = e.target.value === '' ? null : parseFloat(e.target.value);
          onChange(numValue);
        }}
        disabled={disabled}
        error={!!error}
        helperText={error}
        slotProps={{
          input: {
            sx: { fontFamily: 'monospace' },
          },
        }}
      />
    );
  }

  // Date fields
  if (data_type === 'date') {
    return (
      <TextField
        fullWidth
        size="small"
        label={display_name}
        type="date"
        value={value ? String(value).split('T')[0] : ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        error={!!error}
        helperText={error}
        slotProps={{
          inputLabel: { shrink: true },
        }}
      />
    );
  }

  // Datetime fields
  if (data_type === 'timestamp') {
    return (
      <TextField
        fullWidth
        size="small"
        label={display_name}
        type="datetime-local"
        value={value ? String(value).slice(0, 16) : ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        error={!!error}
        helperText={error}
        slotProps={{
          inputLabel: { shrink: true },
        }}
      />
    );
  }

  // JSON fields
  if (data_type === 'json' || render_type === 'json') {
    const jsonStr = typeof value === 'string' ? value : JSON.stringify(value || {}, null, 2);
    return (
      <TextField
        fullWidth
        size="small"
        label={display_name}
        multiline
        rows={3}
        value={jsonStr}
        onChange={(e) => {
          try {
            onChange(JSON.parse(e.target.value));
          } catch {
            onChange(e.target.value);
          }
        }}
        disabled={disabled}
        error={!!error}
        helperText={error}
        slotProps={{
          input: {
            sx: { fontFamily: 'monospace', fontSize: 12 },
          },
        }}
      />
    );
  }

  // Default text field
  return (
    <TextField
      fullWidth
      size="small"
      label={display_name}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      error={!!error}
      helperText={error}
    />
  );
};

export default RecordEditor;
