/**
 * GPS CDM - Mappings Documentation Page
 *
 * Displays field mappings documentation for all payment standards.
 * Users can select a standard and view/edit mappings from Standard -> Bronze -> Silver -> Gold.
 */
import React, { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  IconButton,
  Chip,
  Tooltip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Collapse,
  Divider,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Warning as WarningIcon,
  CheckCircle as MappedIcon,
  Cancel as UnmappedIcon,
  Storage as DatabaseIcon,
  Schema as SchemaIcon,
  Category as CategoryIcon,
} from '@mui/icons-material';
import {
  mappingsApi,
  MessageFormatSummary,
  MappingDocumentationRow,
  CoverageStats,
  FieldCategory,
} from '../api/client';

// Color constants
const CATEGORY_COLORS: Record<string, string> = {
  ISO20022: '#1976d2',
  SWIFT_MT: '#9c27b0',
  REGIONAL: '#2e7d32',
  PROPRIETARY: '#ed6c02',
};

const ZONE_COLORS = {
  bronze: '#cd7f32',
  silver: '#c0c0c0',
  gold: '#ffd700',
};

// CDM entity table ordering priority
const CDM_TABLE_ORDER: Record<string, number> = {
  // Base/Payment tables first (lower number = higher priority)
  'cdm_pacs_fi_customer_credit_transfer': 1,
  'cdm_pacs_fi_credit_transfer': 2,
  'cdm_pacs_fi_payment_status_report': 3,
  'cdm_pacs_payment_return': 4,
  'cdm_pain_customer_credit_transfer_initiation': 5,
  'cdm_pain_payment_status_report': 6,
  'cdm_camt_bank_to_customer_statement': 7,
  'cdm_payment_instruction': 10,
  // Entity tables in specified order
  'cdm_party': 20,
  'cdm_party_identifier': 21,
  'cdm_financial_institution': 30,
  'cdm_institution_identifier': 31,
  'cdm_account': 40,
  'cdm_account_identifier': 41,
  'cdm_transaction_identifier': 50,
};

// Get sort order for a gold table
const getTableOrder = (tableName: string | null | undefined): number => {
  if (!tableName) return 999;
  // Remove schema prefix if present
  const cleanName = tableName.replace(/^gold\./, '');
  // Check for exact match first
  if (CDM_TABLE_ORDER[cleanName] !== undefined) {
    return CDM_TABLE_ORDER[cleanName];
  }
  // Check for base table patterns (cdm_pacs_*, cdm_pain_*, cdm_camt_*)
  if (cleanName.startsWith('cdm_pacs_') || cleanName.startsWith('cdm_pain_') || cleanName.startsWith('cdm_camt_')) {
    return 15; // After known base tables but before entity tables
  }
  // Extension tables
  if (cleanName.startsWith('cdm_payment_extension_')) {
    return 60;
  }
  return 100; // Unknown tables last
};

// Format table name for display
const formatTableName = (tableName: string): string => {
  const cleanName = tableName.replace(/^gold\./, '');
  return cleanName
    .replace(/^cdm_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
};

// Coverage Stats Card
const CoverageCard: React.FC<{
  label: string;
  value: number;
  total: number;
  color: string;
}> = ({ label, value, total, color }) => {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" sx={{ color }}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          of {total} ({pct}%)
        </Typography>
        <LinearProgress
          variant="determinate"
          value={pct}
          sx={{ mt: 1, height: 6, borderRadius: 3 }}
        />
      </CardContent>
    </Card>
  );
};

// Edit Dialog for updating mappings
const EditMappingDialog: React.FC<{
  open: boolean;
  row: MappingDocumentationRow | null;
  onClose: () => void;
  onSave: (updates: any) => void;
}> = ({ open, row, onClose, onSave }) => {
  const [silverUpdates, setSilverUpdates] = useState<any>({});
  const [goldUpdates, setGoldUpdates] = useState<any>({});
  const [standardUpdates, setStandardUpdates] = useState<any>({});

  React.useEffect(() => {
    if (row) {
      setSilverUpdates({});
      setGoldUpdates({});
      setStandardUpdates({});
    }
  }, [row]);

  if (!row) return null;

  const handleSave = () => {
    onSave({
      standard_field_id: row.standard_field_id,
      silver_mapping_id: row.silver_mapping_id,
      gold_mapping_id: row.gold_mapping_id,
      standardUpdates: Object.keys(standardUpdates).length > 0 ? standardUpdates : null,
      silverUpdates: Object.keys(silverUpdates).length > 0 ? silverUpdates : null,
      goldUpdates: Object.keys(goldUpdates).length > 0 ? goldUpdates : null,
    });
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Edit Mapping: {row.standard_field_name || row.silver_column}
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Standard Field Metadata
          </Typography>
          <Grid container spacing={2}>
            <Grid size={12}>
              <TextField
                fullWidth
                size="small"
                label="Field Description"
                defaultValue={row.standard_field_description || ''}
                onChange={(e) => setStandardUpdates({ ...standardUpdates, field_description: e.target.value })}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Data Type"
                defaultValue={row.standard_field_data_type || ''}
                onChange={(e) => setStandardUpdates({ ...standardUpdates, data_type: e.target.value })}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Allowed Values"
                defaultValue={row.standard_field_allowed_values || ''}
                onChange={(e) => setStandardUpdates({ ...standardUpdates, allowed_values: e.target.value })}
              />
            </Grid>
          </Grid>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: ZONE_COLORS.silver }} gutterBottom>
            Silver Mapping
          </Typography>
          <Grid container spacing={2}>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Silver Column"
                defaultValue={row.silver_column || ''}
                onChange={(e) => setSilverUpdates({ ...silverUpdates, target_column: e.target.value })}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Source Path"
                defaultValue={row.silver_source_path || ''}
                onChange={(e) => setSilverUpdates({ ...silverUpdates, source_path: e.target.value })}
              />
            </Grid>
            <Grid size={4}>
              <TextField
                fullWidth
                size="small"
                label="Data Type"
                defaultValue={row.silver_data_type || 'VARCHAR'}
                onChange={(e) => setSilverUpdates({ ...silverUpdates, data_type: e.target.value })}
              />
            </Grid>
            <Grid size={4}>
              <TextField
                fullWidth
                size="small"
                label="Max Length"
                type="number"
                defaultValue={row.silver_max_length || ''}
                onChange={(e) => setSilverUpdates({ ...silverUpdates, max_length: parseInt(e.target.value) || null })}
              />
            </Grid>
            <Grid size={4}>
              <TextField
                fullWidth
                size="small"
                label="Transform"
                defaultValue={row.silver_transform || ''}
                onChange={(e) => setSilverUpdates({ ...silverUpdates, transform_function: e.target.value })}
              />
            </Grid>
          </Grid>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box>
          <Typography variant="subtitle2" sx={{ color: ZONE_COLORS.gold }} gutterBottom>
            Gold Mapping
          </Typography>
          <Grid container spacing={2}>
            <Grid size={4}>
              <TextField
                fullWidth
                size="small"
                label="Gold Table"
                defaultValue={row.gold_table || ''}
                onChange={(e) => setGoldUpdates({ ...goldUpdates, gold_table: e.target.value })}
              />
            </Grid>
            <Grid size={4}>
              <TextField
                fullWidth
                size="small"
                label="Gold Column"
                defaultValue={row.gold_column || ''}
                onChange={(e) => setGoldUpdates({ ...goldUpdates, gold_column: e.target.value })}
              />
            </Grid>
            <Grid size={4}>
              <TextField
                fullWidth
                size="small"
                label="Entity Role"
                defaultValue={row.gold_entity_role || ''}
                onChange={(e) => setGoldUpdates({ ...goldUpdates, entity_role: e.target.value })}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Source Expression"
                defaultValue={row.gold_source_expression || ''}
                onChange={(e) => setGoldUpdates({ ...goldUpdates, source_expression: e.target.value })}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Purpose Code"
                defaultValue={row.gold_purpose_code || ''}
                onChange={(e) => setGoldUpdates({ ...goldUpdates, purpose_code: e.target.value })}
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Main Component
const MappingsDocumentationPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  // State
  const [selectedFormat, setSelectedFormat] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [fieldCategoryFilter, setFieldCategoryFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const [showMappedOnly, setShowMappedOnly] = useState(false);
  const [showUnmappedOnly, setShowUnmappedOnly] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [editRow, setEditRow] = useState<MappingDocumentationRow | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());

  // Queries
  const { data: formats, isLoading: formatsLoading } = useQuery({
    queryKey: ['messageFormats', selectedCategory],
    queryFn: () => mappingsApi.getFormats({ category: selectedCategory || undefined }),
  });

  const { data: documentation, isLoading: docLoading, refetch: refetchDoc } = useQuery({
    queryKey: ['mappingsDoc', selectedFormat, fieldCategoryFilter, showMappedOnly, showUnmappedOnly],
    queryFn: () => mappingsApi.getDocumentation(selectedFormat, {
      field_category: fieldCategoryFilter || undefined,
      mapped_only: showMappedOnly,
      unmapped_only: showUnmappedOnly,
    }),
    enabled: !!selectedFormat,
  });

  const { data: fieldCategories } = useQuery({
    queryKey: ['fieldCategories', selectedFormat],
    queryFn: () => mappingsApi.getFieldCategories(selectedFormat),
    enabled: !!selectedFormat,
  });

  const { data: coverage } = useQuery({
    queryKey: ['coverage', selectedFormat],
    queryFn: () => mappingsApi.getCoverage(selectedFormat),
    enabled: !!selectedFormat,
  });

  // Mutations
  const updateStandardMutation = useMutation({
    mutationFn: ({ fieldId, updates }: { fieldId: number; updates: any }) =>
      mappingsApi.updateStandardField(fieldId, updates),
    onSuccess: () => {
      enqueueSnackbar('Standard field updated', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['mappingsDoc'] });
    },
    onError: () => enqueueSnackbar('Failed to update standard field', { variant: 'error' }),
  });

  const updateSilverMutation = useMutation({
    mutationFn: ({ mappingId, updates }: { mappingId: number; updates: any }) =>
      mappingsApi.updateSilverMapping(mappingId, updates),
    onSuccess: () => {
      enqueueSnackbar('Silver mapping updated', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['mappingsDoc'] });
    },
    onError: () => enqueueSnackbar('Failed to update silver mapping', { variant: 'error' }),
  });

  const updateGoldMutation = useMutation({
    mutationFn: ({ mappingId, updates }: { mappingId: number; updates: any }) =>
      mappingsApi.updateGoldMapping(mappingId, updates),
    onSuccess: () => {
      enqueueSnackbar('Gold mapping updated', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['mappingsDoc'] });
    },
    onError: () => enqueueSnackbar('Failed to update gold mapping', { variant: 'error' }),
  });

  const deleteGoldMutation = useMutation({
    mutationFn: ({ mappingId, softDelete }: { mappingId: number; softDelete: boolean }) =>
      mappingsApi.deleteGoldMapping(mappingId, softDelete),
    onSuccess: () => {
      enqueueSnackbar('Gold mapping deleted', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['mappingsDoc'] });
      queryClient.invalidateQueries({ queryKey: ['coverage'] });
    },
    onError: () => enqueueSnackbar('Failed to delete gold mapping', { variant: 'error' }),
  });

  // Handlers
  const handleDeleteGoldMapping = useCallback((mappingId: number) => {
    if (window.confirm('Are you sure you want to delete this Gold mapping? This will soft-delete (deactivate) the mapping.')) {
      deleteGoldMutation.mutate({ mappingId, softDelete: true });
    }
  }, [deleteGoldMutation]);
  const handleSaveMapping = useCallback((updates: any) => {
    if (updates.standardUpdates && updates.standard_field_id) {
      updateStandardMutation.mutate({
        fieldId: updates.standard_field_id,
        updates: updates.standardUpdates,
      });
    }
    if (updates.silverUpdates && updates.silver_mapping_id) {
      updateSilverMutation.mutate({
        mappingId: updates.silver_mapping_id,
        updates: updates.silverUpdates,
      });
    }
    if (updates.goldUpdates && updates.gold_mapping_id) {
      updateGoldMutation.mutate({
        mappingId: updates.gold_mapping_id,
        updates: updates.goldUpdates,
      });
    }
  }, [updateStandardMutation, updateSilverMutation, updateGoldMutation]);

  const handleExport = useCallback(async () => {
    if (!selectedFormat) return;
    try {
      const result = await mappingsApi.exportMappings(selectedFormat, 'csv');
      // Create download
      const blob = new Blob([result.data as string], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `mappings_${selectedFormat}_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      enqueueSnackbar('Export downloaded', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar('Export failed', { variant: 'error' });
    }
  }, [selectedFormat, enqueueSnackbar]);

  // Computed values - Group mappings by gold_table with CDM entity ordering
  const groupedData = useMemo(() => {
    if (!documentation) return [];

    // Group by gold_table
    const groups = new Map<string, MappingDocumentationRow[]>();
    documentation.forEach(row => {
      const tableName = row.gold_table || 'Unmapped';
      if (!groups.has(tableName)) {
        groups.set(tableName, []);
      }
      groups.get(tableName)!.push(row);
    });

    // Sort groups by CDM entity order
    const sortedGroups = Array.from(groups.entries())
      .sort((a, b) => getTableOrder(a[0]) - getTableOrder(b[0]));

    return sortedGroups.map(([tableName, rows]) => ({
      tableName,
      displayName: tableName === 'Unmapped' ? 'Unmapped Fields' : formatTableName(tableName),
      rows,
      order: getTableOrder(tableName),
    }));
  }, [documentation]);

  // Toggle group collapse
  const toggleGroup = useCallback((tableName: string) => {
    setCollapsedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tableName)) {
        newSet.delete(tableName);
      } else {
        newSet.add(tableName);
      }
      return newSet;
    });
  }, []);

  // Collapse/Expand all
  const collapseAll = useCallback(() => {
    const allTables = groupedData.map(g => g.tableName);
    setCollapsedGroups(new Set(allTables));
  }, [groupedData]);

  const expandAll = useCallback(() => {
    setCollapsedGroups(new Set());
  }, []);

  const selectedFormatInfo = useMemo(() => {
    return formats?.find(f => f.format_id === selectedFormat);
  }, [formats, selectedFormat]);

  const coverageInfo = useMemo(() => {
    return coverage?.[0];
  }, [coverage]);

  // Categories for filter
  const categories = useMemo(() => {
    const cats = new Set<string>();
    formats?.forEach(f => cats.add(f.format_category));
    return Array.from(cats);
  }, [formats]);

  // Total count for display
  const totalMappings = useMemo(() => {
    return documentation?.length || 0;
  }, [documentation]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4">Mappings Documentation</Typography>
          <Typography variant="body2" color="text.secondary">
            View and manage field mappings from payment standards to Bronze, Silver, and Gold zones
          </Typography>
        </Box>
        <Box>
          <Button
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
            variant={showFilters ? 'contained' : 'outlined'}
            size="small"
            sx={{ mr: 1 }}
          >
            Filters
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            onClick={handleExport}
            disabled={!selectedFormat}
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          >
            Export CSV
          </Button>
          {selectedFormat && groupedData.length > 0 && (
            <>
              <Button
                startIcon={<CollapseIcon />}
                onClick={collapseAll}
                variant="outlined"
                size="small"
                sx={{ mr: 1 }}
              >
                Collapse All
              </Button>
              <Button
                startIcon={<ExpandIcon />}
                onClick={expandAll}
                variant="outlined"
                size="small"
                sx={{ mr: 1 }}
              >
                Expand All
              </Button>
            </>
          )}
          <IconButton onClick={() => refetchDoc()}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Format Selection */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 4 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Format Category</InputLabel>
              <Select
                value={selectedCategory}
                label="Format Category"
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setSelectedFormat('');
                }}
                sx={{ minWidth: 200 }}
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map(cat => (
                  <MenuItem key={cat} value={cat}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={cat}
                        size="small"
                        sx={{ bgcolor: CATEGORY_COLORS[cat] || '#757575', color: 'white' }}
                      />
                      <Typography variant="body2">{cat}</Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 5 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Message Format</InputLabel>
              <Select
                value={selectedFormat}
                label="Message Format"
                onChange={(e) => {
                  setSelectedFormat(e.target.value);
                  setPage(0);
                }}
                sx={{ minWidth: 300 }}
                MenuProps={{
                  PaperProps: {
                    sx: { maxHeight: 400, minWidth: 450 }
                  }
                }}
              >
                <MenuItem value="">Select a format...</MenuItem>
                {formats?.map(f => (
                  <MenuItem key={f.format_id} value={f.format_id} sx={{ minWidth: 400 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between', gap: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {f.format_id} - {f.format_name}
                      </Typography>
                      <Chip
                        label={`${f.total_standard_fields} fields`}
                        size="small"
                        variant="outlined"
                        color={f.unmapped_fields === 0 ? 'success' : 'warning'}
                      />
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid size={{ xs: 12, sm: 3 }}>
            {selectedFormat && (
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={<SchemaIcon />}
                  label={selectedFormatInfo?.standard_name || 'Standard'}
                  size="small"
                />
                <Chip
                  icon={<CategoryIcon />}
                  label={selectedFormatInfo?.country || 'Global'}
                  size="small"
                />
              </Box>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* Filters Panel */}
      <Collapse in={showFilters}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControl fullWidth size="small">
                <InputLabel>Field Category</InputLabel>
                <Select
                  value={fieldCategoryFilter}
                  label="Field Category"
                  onChange={(e) => {
                    setFieldCategoryFilter(e.target.value);
                    setPage(0);
                  }}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {fieldCategories?.map(fc => (
                    <MenuItem key={fc.field_category} value={fc.field_category}>
                      {fc.field_category} ({fc.field_count})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showMappedOnly}
                    onChange={(e) => {
                      setShowMappedOnly(e.target.checked);
                      if (e.target.checked) setShowUnmappedOnly(false);
                      setPage(0);
                    }}
                  />
                }
                label="Mapped Only"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showUnmappedOnly}
                    onChange={(e) => {
                      setShowUnmappedOnly(e.target.checked);
                      if (e.target.checked) setShowMappedOnly(false);
                      setPage(0);
                    }}
                  />
                }
                label="Unmapped Only"
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 3 }}>
              <Button
                variant="outlined"
                onClick={() => {
                  setFieldCategoryFilter('');
                  setShowMappedOnly(false);
                  setShowUnmappedOnly(false);
                  setPage(0);
                }}
                fullWidth
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Collapse>

      {/* Coverage Stats */}
      {coverageInfo && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={{ xs: 12, sm: 3 }}>
            <CoverageCard
              label="Standard Fields"
              value={coverageInfo.total_standard_fields}
              total={coverageInfo.total_standard_fields}
              color="#1976d2"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 3 }}>
            <CoverageCard
              label="Mapped to Silver"
              value={coverageInfo.mapped_to_silver}
              total={coverageInfo.total_standard_fields}
              color={ZONE_COLORS.silver}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 3 }}>
            <CoverageCard
              label="Mapped to Gold"
              value={coverageInfo.mapped_to_gold}
              total={coverageInfo.mapped_to_silver || 1}
              color={ZONE_COLORS.gold}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 3 }}>
            <CoverageCard
              label="Unmapped Fields"
              value={coverageInfo.unmapped_fields}
              total={coverageInfo.total_standard_fields}
              color="#f44336"
            />
          </Grid>
        </Grid>
      )}

      {/* Loading */}
      {(formatsLoading || docLoading) && <LinearProgress sx={{ mb: 2 }} />}

      {/* No Format Selected */}
      {!selectedFormat && !formatsLoading && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Select a message format above to view its field mappings documentation.
        </Alert>
      )}

      {/* Mappings Table - Grouped by CDM Entity */}
      {selectedFormat && documentation && (
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Showing {totalMappings} field mappings grouped by {groupedData.length} CDM entities
          </Typography>

          {groupedData.map((group) => (
            <Paper key={group.tableName} sx={{ mb: 2 }}>
              {/* Group Header */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  p: 1.5,
                  bgcolor: group.order <= 15 ? 'rgba(255, 215, 0, 0.15)' :
                           group.order <= 25 ? 'rgba(33, 150, 243, 0.1)' :
                           group.order <= 35 ? 'rgba(156, 39, 176, 0.1)' :
                           group.order <= 45 ? 'rgba(76, 175, 80, 0.1)' :
                           'rgba(0, 0, 0, 0.03)',
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
                onClick={() => toggleGroup(group.tableName)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <IconButton size="small">
                    {collapsedGroups.has(group.tableName) ? <ExpandIcon /> : <CollapseIcon />}
                  </IconButton>
                  <DatabaseIcon sx={{ color: ZONE_COLORS.gold, fontSize: 20 }} />
                  <Typography variant="subtitle1" fontWeight={600}>
                    {group.displayName}
                  </Typography>
                  <Chip
                    label={group.tableName.replace('gold.', '')}
                    size="small"
                    sx={{ fontFamily: 'monospace', fontSize: 11 }}
                  />
                </Box>
                <Chip
                  label={`${group.rows.length} fields`}
                  size="small"
                  color={group.order <= 15 ? 'warning' : 'default'}
                  variant="outlined"
                />
              </Box>

              {/* Group Content */}
              <Collapse in={!collapsedGroups.has(group.tableName)}>
                <TableContainer sx={{ maxHeight: 400 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 160 }}>Silver Column</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 160 }}>Gold Column</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 110 }}>Entity Role</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 140 }}>Standard Field</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 200 }}>Source Path</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5' }}>Description</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 90 }}>Transform</TableCell>
                        <TableCell sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5', width: 70 }}>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {group.rows.map((row, idx) => (
                        <TableRow
                          key={`${group.tableName}-${row.silver_column || idx}-${row.gold_column || idx}-${row.gold_entity_role || ''}`}
                          hover
                          sx={{
                            bgcolor: !row.is_mapped_to_silver ? 'rgba(244, 67, 54, 0.05)' : undefined,
                          }}
                        >
                          <TableCell>
                            <Typography
                              variant="body2"
                              sx={{ fontFamily: 'monospace', fontSize: 11 }}
                            >
                              {row.silver_column || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography
                              variant="body2"
                              sx={{ fontFamily: 'monospace', fontSize: 11 }}
                            >
                              {row.gold_column || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {row.gold_entity_role ? (
                              <Chip
                                label={row.gold_entity_role}
                                size="small"
                                color="primary"
                                variant="outlined"
                                sx={{ fontSize: 10 }}
                              />
                            ) : (
                              '-'
                            )}
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              {row.is_mapped_to_silver ? (
                                <MappedIcon sx={{ fontSize: 14, color: 'success.main' }} />
                              ) : (
                                <UnmappedIcon sx={{ fontSize: 14, color: 'error.main' }} />
                              )}
                              <Typography variant="body2" fontSize={12}>
                                {row.standard_field_name || '-'}
                              </Typography>
                              {row.standard_field_mandatory && (
                                <Chip label="REQ" size="small" color="error" sx={{ height: 14, fontSize: 9 }} />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={row.standard_field_path || row.silver_source_path || ''}>
                              <Typography
                                variant="body2"
                                fontSize={10}
                                noWrap
                                sx={{ fontFamily: 'monospace', maxWidth: 200, color: 'text.secondary' }}
                              >
                                {row.standard_field_path || row.silver_source_path || '-'}
                              </Typography>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={row.standard_field_description || ''}>
                              <Typography variant="body2" fontSize={11} noWrap sx={{ maxWidth: 180 }}>
                                {row.standard_field_description || '-'}
                              </Typography>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontSize={10} sx={{ fontFamily: 'monospace' }}>
                              {row.gold_transform || row.silver_transform || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              <Tooltip title="Edit mapping">
                                <span>
                                  <IconButton
                                    size="small"
                                    onClick={() => setEditRow(row)}
                                    disabled={!row.standard_field_id && !row.silver_mapping_id}
                                  >
                                    <EditIcon sx={{ fontSize: 16 }} />
                                  </IconButton>
                                </span>
                              </Tooltip>
                              {row.gold_mapping_id && (
                                <Tooltip title="Delete Gold mapping">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleDeleteGoldMapping(row.gold_mapping_id!)}
                                    color="error"
                                  >
                                    <DeleteIcon sx={{ fontSize: 16 }} />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Collapse>
            </Paper>
          ))}

          {groupedData.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No mappings found for this format
              </Typography>
            </Paper>
          )}
        </Box>
      )}

      {/* Edit Dialog */}
      <EditMappingDialog
        open={!!editRow}
        row={editRow}
        onClose={() => setEditRow(null)}
        onSave={handleSaveMapping}
      />
    </Box>
  );
};

export default MappingsDocumentationPage;
