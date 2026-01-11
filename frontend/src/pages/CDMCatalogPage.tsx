/**
 * GPS CDM - CDM Catalog Page
 *
 * Displays searchable catalog of CDM data elements with business descriptions,
 * ISO 20022 mappings, and legacy format mappings.
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
  TextField,
  Button,
  IconButton,
  Chip,
  Tooltip,
  LinearProgress,
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
  Collapse,
  Divider,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  Popover,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Search as SearchIcon,
  Storage as DatabaseIcon,
  Person as PartyIcon,
  AccountBalance as InstitutionIcon,
  AccountCircle as AccountIcon,
  Payment as PaymentIcon,
  Extension as ExtensionIcon,
  Description as DocIcon,
  CheckCircle as DocumentedIcon,
  Warning as UndocumentedIcon,
  Clear as ClearIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { catalogApi, CatalogElement, CatalogTableSummary, CatalogStats } from '../api/client';

// Table category styling
const getTableStyle = (tableName: string): { icon: React.ElementType; color: string; bg: string } => {
  if (tableName.includes('party')) return { icon: PartyIcon, color: '#7b1fa2', bg: '#f3e5f5' };
  if (tableName.includes('institution')) return { icon: InstitutionIcon, color: '#1565c0', bg: '#e3f2fd' };
  if (tableName.includes('account')) return { icon: AccountIcon, color: '#2e7d32', bg: '#e8f5e9' };
  if (tableName.includes('payment_instruction')) return { icon: PaymentIcon, color: '#c62828', bg: '#ffebee' };
  if (tableName.includes('extension')) return { icon: ExtensionIcon, color: '#ef6c00', bg: '#fff3e0' };
  if (tableName.includes('pacs_') || tableName.includes('pain_') || tableName.includes('camt_')) return { icon: DocIcon, color: '#00695c', bg: '#e0f2f1' };
  return { icon: DatabaseIcon, color: '#546e7a', bg: '#eceff1' };
};

// Stats Card Component
const StatsCard: React.FC<{
  label: string;
  value: number;
  total?: number;
  color: string;
  showPercent?: boolean;
}> = ({ label, value, total, color, showPercent = true }) => {
  const pct = total && total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ textAlign: 'center', py: 2 }}>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" sx={{ color, my: 0.5 }}>
          {value.toLocaleString()}
        </Typography>
        {showPercent && total !== undefined && (
          <>
            <Typography variant="body2" color="text.secondary">
              of {total.toLocaleString()} ({pct}%)
            </Typography>
            <LinearProgress
              variant="determinate"
              value={pct}
              sx={{ mt: 1, height: 4, borderRadius: 2, bgcolor: `${color}22` }}
              color="inherit"
            />
          </>
        )}
      </CardContent>
    </Card>
  );
};

// Legacy Formats Popover Component
const LegacyFormatsPopover: React.FC<{
  element: CatalogElement;
  anchorEl: HTMLElement | null;
  onClose: () => void;
}> = ({ element, anchorEl, onClose }) => {
  return (
    <Popover
      open={Boolean(anchorEl)}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      transformOrigin={{ vertical: 'top', horizontal: 'left' }}
    >
      <Box sx={{ p: 2, minWidth: 350, maxWidth: 500, maxHeight: 400, overflow: 'auto' }}>
        <Typography variant="subtitle2" gutterBottom>
          Legacy Format Mappings for "{element.pde_column_name}"
        </Typography>
        <Divider sx={{ mb: 1 }} />
        {element.legacy_mappings && element.legacy_mappings.length > 0 ? (
          <List dense disablePadding>
            {element.legacy_mappings.map((mapping, idx) => (
              <ListItem key={idx} disablePadding sx={{ py: 0.5 }}>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip label={mapping.format_id} size="small" color="primary" sx={{ fontWeight: 600 }} />
                      {mapping.entity_role && (
                        <Chip label={mapping.entity_role} size="small" color="secondary" variant="outlined" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="caption" component="div" sx={{ fontFamily: 'monospace' }}>
                        Source: {mapping.source_expression || '-'}
                      </Typography>
                      {mapping.transform_expression && (
                        <Typography variant="caption" component="div" sx={{ fontFamily: 'monospace' }}>
                          Transform: {mapping.transform_expression}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No legacy format mappings
          </Typography>
        )}
      </Box>
    </Popover>
  );
};

// Allowed Values interface
interface AllowedValueItem {
  value: string;
  description?: string;
}

// Edit Catalog Element Dialog
const EditElementDialog: React.FC<{
  open: boolean;
  element: CatalogElement | null;
  onClose: () => void;
  onSave: (catalogId: number, updates: any) => void;
}> = ({ open, element, onClose, onSave }) => {
  const [businessName, setBusinessName] = useState('');
  const [businessDescription, setBusinessDescription] = useState('');
  const [dataFormat, setDataFormat] = useState('');
  const [allowedValues, setAllowedValues] = useState<AllowedValueItem[]>([]);
  const [isoElementName, setIsoElementName] = useState('');
  const [isoElementDescription, setIsoElementDescription] = useState('');
  const [isoElementPath, setIsoElementPath] = useState('');
  const [isoDataType, setIsoDataType] = useState('');

  React.useEffect(() => {
    if (element) {
      setBusinessName(element.business_name || '');
      setBusinessDescription(element.business_description || '');
      setDataFormat(element.data_format || '');
      setAllowedValues(element.allowed_values || []);
      setIsoElementName(element.iso_element_name || '');
      setIsoElementDescription(element.iso_element_description || '');
      setIsoElementPath(element.iso_element_path || '');
      setIsoDataType(element.iso_data_type || '');
    }
  }, [element]);

  if (!element) return null;

  const handleSave = () => {
    onSave(element.catalog_id, {
      business_name: businessName || null,
      business_description: businessDescription || null,
      data_format: dataFormat || null,
      allowed_values: allowedValues.length > 0 ? allowedValues : null,
      iso_element_name: isoElementName || null,
      iso_element_description: isoElementDescription || null,
      iso_element_path: isoElementPath || null,
      iso_data_type: isoDataType || null,
    });
    onClose();
  };

  const addAllowedValue = () => {
    setAllowedValues([...allowedValues, { value: '', description: '' }]);
  };

  const removeAllowedValue = (index: number) => {
    setAllowedValues(allowedValues.filter((_, i) => i !== index));
  };

  const updateAllowedValue = (index: number, field: 'value' | 'description', val: string) => {
    const updated = [...allowedValues];
    updated[index] = { ...updated[index], [field]: val };
    setAllowedValues(updated);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Edit Catalog Element: {element.pde_column_name}
      </DialogTitle>
      <DialogContent dividers>
        {/* Physical Data Element (Read-only) */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Physical Data Element (PDE) - Read Only
          </Typography>
          <Grid container spacing={2}>
            <Grid size={6}>
              <TextField fullWidth size="small" label="Table" value={element.pde_table_name} disabled sx={{ bgcolor: '#f5f5f5' }} />
            </Grid>
            <Grid size={6}>
              <TextField fullWidth size="small" label="Column" value={element.pde_column_name} disabled sx={{ bgcolor: '#f5f5f5' }} />
            </Grid>
            <Grid size={6}>
              <TextField fullWidth size="small" label="Data Type" value={element.pde_data_type || ''} disabled sx={{ bgcolor: '#f5f5f5' }} />
            </Grid>
            <Grid size={6}>
              <TextField fullWidth size="small" label="Nullable" value={element.pde_is_nullable ? 'Yes' : 'No'} disabled sx={{ bgcolor: '#f5f5f5' }} />
            </Grid>
          </Grid>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Business Metadata (Editable) */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="primary" gutterBottom>
            Business Metadata (Editable)
          </Typography>
          <Grid container spacing={2}>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Business Name"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                placeholder="e.g., Payment Amount"
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="Data Format"
                value={dataFormat}
                onChange={(e) => setDataFormat(e.target.value)}
                placeholder="e.g., Decimal with 4 decimal places"
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                size="small"
                label="Business Description"
                value={businessDescription}
                onChange={(e) => setBusinessDescription(e.target.value)}
                multiline
                rows={3}
                placeholder="Describe what this field represents in business terms..."
              />
            </Grid>
          </Grid>
        </Box>

        {/* Allowed Values (Editable) */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2" color="primary">
              Allowed Values
            </Typography>
            <Button size="small" startIcon={<AddIcon />} onClick={addAllowedValue}>
              Add Value
            </Button>
          </Box>
          {allowedValues.length > 0 ? (
            <Box sx={{ bgcolor: '#fafafa', p: 1, borderRadius: 1 }}>
              {allowedValues.map((av, idx) => (
                <Grid container spacing={1} key={idx} sx={{ mb: 1 }}>
                  <Grid size={4}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Value"
                      value={av.value}
                      onChange={(e) => updateAllowedValue(idx, 'value', e.target.value)}
                    />
                  </Grid>
                  <Grid size={7}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Description"
                      value={av.description || ''}
                      onChange={(e) => updateAllowedValue(idx, 'description', e.target.value)}
                    />
                  </Grid>
                  <Grid size={1}>
                    <IconButton size="small" onClick={() => removeAllowedValue(idx)} color="error">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Grid>
                </Grid>
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              No allowed values defined
            </Typography>
          )}
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* ISO 20022 Reference */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="secondary" gutterBottom>
            ISO 20022 Reference
          </Typography>
          <Grid container spacing={2}>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="ISO Element Name"
                value={isoElementName}
                onChange={(e) => setIsoElementName(e.target.value)}
                placeholder="e.g., InstructedAmount"
              />
            </Grid>
            <Grid size={6}>
              <TextField
                fullWidth
                size="small"
                label="ISO Data Type"
                value={isoDataType}
                onChange={(e) => setIsoDataType(e.target.value)}
                placeholder="e.g., ActiveOrHistoricCurrencyAndAmount"
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                size="small"
                label="ISO Element Path"
                value={isoElementPath}
                onChange={(e) => setIsoElementPath(e.target.value)}
                placeholder="e.g., CdtTrfTxInf/Amt/InstdAmt"
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                size="small"
                label="ISO Element Description"
                value={isoElementDescription}
                onChange={(e) => setIsoElementDescription(e.target.value)}
                multiline
                rows={2}
                placeholder="Description from ISO 20022 specification..."
              />
            </Grid>
          </Grid>
        </Box>

        {/* Legacy Mappings (Read-only) */}
        {element.legacy_mappings && element.legacy_mappings.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Legacy Format Mappings ({element.legacy_mapping_count}) - Read Only
              </Typography>
              <List dense sx={{ maxHeight: 200, overflow: 'auto', bgcolor: '#fafafa', borderRadius: 1 }}>
                {element.legacy_mappings.slice(0, 15).map((mapping, idx) => (
                  <ListItem key={idx} divider>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          <Chip label={mapping.format_id} size="small" color="primary" variant="outlined" />
                          {mapping.entity_role && (
                            <Chip label={mapping.entity_role} size="small" color="secondary" variant="outlined" />
                          )}
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                          {mapping.source_expression}
                          {mapping.transform_expression && ` → ${mapping.transform_expression}`}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
                {element.legacy_mapping_count > 15 && (
                  <ListItem>
                    <ListItemText secondary={`...and ${element.legacy_mapping_count - 15} more formats`} />
                  </ListItem>
                )}
              </List>
            </Box>
          </>
        )}
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
const CDMCatalogPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [collapsedTables, setCollapsedTables] = useState<Set<string>>(new Set());
  const [editElement, setEditElement] = useState<CatalogElement | null>(null);
  const [documentedOnly, setDocumentedOnly] = useState(false);
  const [formatsPopoverAnchor, setFormatsPopoverAnchor] = useState<HTMLElement | null>(null);
  const [formatsPopoverElement, setFormatsPopoverElement] = useState<CatalogElement | null>(null);

  // Queries
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['catalogStats'],
    queryFn: () => catalogApi.getStats(),
  });

  const { data: tables, isLoading: tablesLoading } = useQuery({
    queryKey: ['catalogTables'],
    queryFn: () => catalogApi.getTables(),
  });

  const { data: elements, isLoading: elementsLoading, refetch: refetchElements } = useQuery({
    queryKey: ['catalogElements', searchQuery, selectedTable, documentedOnly],
    queryFn: () => catalogApi.searchElements({
      query: searchQuery || undefined,
      table_name: selectedTable || undefined,
      documented_only: documentedOnly,
      limit: 2000,
    }),
  });

  // Mutations
  const updateMutation = useMutation({
    mutationFn: ({ catalogId, updates }: { catalogId: number; updates: any }) =>
      catalogApi.updateElement(catalogId, updates),
    onSuccess: () => {
      enqueueSnackbar('Catalog element updated', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['catalogElements'] });
      queryClient.invalidateQueries({ queryKey: ['catalogStats'] });
      queryClient.invalidateQueries({ queryKey: ['catalogTables'] });
    },
    onError: () => enqueueSnackbar('Failed to update element', { variant: 'error' }),
  });

  const refreshMutation = useMutation({
    mutationFn: () => catalogApi.refreshFromSchema(),
    onSuccess: (data) => {
      enqueueSnackbar(`Schema refreshed: ${data.inserted} new, ${data.updated} updated`, { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['catalogElements'] });
      queryClient.invalidateQueries({ queryKey: ['catalogStats'] });
      queryClient.invalidateQueries({ queryKey: ['catalogTables'] });
    },
    onError: () => enqueueSnackbar('Failed to refresh schema', { variant: 'error' }),
  });

  // Handlers
  const handleSaveElement = useCallback((catalogId: number, updates: any) => {
    updateMutation.mutate({ catalogId, updates });
  }, [updateMutation]);

  const handleExport = useCallback(async (format: 'csv' | 'xlsx') => {
    try {
      const response = await catalogApi.exportCatalog({
        table_names: selectedTable || undefined,
        format,
      });
      const blob = new Blob([response], {
        type: format === 'xlsx'
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : 'text/csv'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cdm_catalog_${new Date().toISOString().split('T')[0]}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      enqueueSnackbar('Export downloaded', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar('Export failed', { variant: 'error' });
    }
  }, [selectedTable, enqueueSnackbar]);

  const toggleTable = useCallback((tableName: string) => {
    setCollapsedTables(prev => {
      const newSet = new Set(prev);
      if (newSet.has(tableName)) {
        newSet.delete(tableName);
      } else {
        newSet.add(tableName);
      }
      return newSet;
    });
  }, []);

  const collapseAll = useCallback(() => {
    if (tables) {
      setCollapsedTables(new Set(tables.map(t => t.table_name)));
    }
  }, [tables]);

  const expandAll = useCallback(() => {
    setCollapsedTables(new Set());
  }, []);

  const handleFormatsClick = useCallback((event: React.MouseEvent<HTMLElement>, element: CatalogElement) => {
    event.stopPropagation();
    setFormatsPopoverAnchor(event.currentTarget);
    setFormatsPopoverElement(element);
  }, []);

  const handleFormatsClose = useCallback(() => {
    setFormatsPopoverAnchor(null);
    setFormatsPopoverElement(null);
  }, []);

  // Group elements by table
  const groupedElements = useMemo(() => {
    if (!elements?.elements) return [];

    const groups = new Map<string, CatalogElement[]>();
    elements.elements.forEach(el => {
      if (!groups.has(el.pde_table_name)) {
        groups.set(el.pde_table_name, []);
      }
      groups.get(el.pde_table_name)!.push(el);
    });

    const tableMap = new Map(tables?.map(t => [t.table_name, t]) || []);

    return Array.from(groups.entries())
      .map(([tableName, els]) => ({
        tableName,
        displayName: tableMap.get(tableName)?.display_name || tableName,
        sortOrder: tableMap.get(tableName)?.sort_order || 999,
        elements: els,
        documentedCount: els.filter(e => e.business_description).length,
      }))
      .sort((a, b) => a.sortOrder - b.sortOrder);
  }, [elements, tables]);

  const isLoading = statsLoading || tablesLoading || elementsLoading;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4">CDM Data Catalog</Typography>
          <Typography variant="body2" color="text.secondary">
            Searchable catalog of CDM data elements with business descriptions, ISO 20022 mappings, and legacy format mappings
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button startIcon={<DownloadIcon />} onClick={() => handleExport('xlsx')} variant="outlined" size="small">
            Export Excel
          </Button>
          <Button startIcon={<DownloadIcon />} onClick={() => handleExport('csv')} variant="outlined" size="small">
            Export CSV
          </Button>
          <Button
            startIcon={<RefreshIcon />}
            onClick={() => refreshMutation.mutate()}
            variant="outlined"
            size="small"
            disabled={refreshMutation.isPending}
          >
            Refresh Schema
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid size={{ xs: 6, sm: 3 }}>
            <StatsCard label="Total Elements" value={stats.total_elements} color="#1976d2" showPercent={false} />
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <StatsCard label="Documented" value={stats.documented_elements} total={stats.total_elements} color="#2e7d32" />
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <StatsCard label="ISO Mapped" value={stats.iso_mapped_elements} total={stats.total_elements} color="#9c27b0" />
          </Grid>
          <Grid size={{ xs: 6, sm: 3 }}>
            <StatsCard label="CDM Tables" value={stats.total_tables} color="#ef6c00" showPercent={false} />
          </Grid>
        </Grid>
      )}

      {/* Search & Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search business name, description, column, ISO element, ISO path..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: searchQuery && (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setSearchQuery('')}>
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 3 }}>
            <Button
              variant={documentedOnly ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setDocumentedOnly(!documentedOnly)}
              startIcon={documentedOnly ? <DocumentedIcon /> : <UndocumentedIcon />}
              fullWidth
            >
              {documentedOnly ? 'Documented Only' : 'All Elements'}
            </Button>
          </Grid>
          <Grid size={{ xs: 12, sm: 3 }}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button startIcon={<CollapseIcon />} onClick={collapseAll} variant="outlined" size="small">
                Collapse All
              </Button>
              <Button startIcon={<ExpandIcon />} onClick={expandAll} variant="outlined" size="small">
                Expand All
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Loading */}
      {isLoading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Results Summary */}
      {elements && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Showing {elements.elements.length} elements across {groupedElements.length} tables
          {searchQuery && ` matching "${searchQuery}"`}
        </Typography>
      )}

      {/* Grouped Tables */}
      {groupedElements.map((group) => {
        const style = getTableStyle(group.tableName);
        const TableIcon = style.icon;

        return (
          <Paper key={group.tableName} sx={{ mb: 2, overflow: 'hidden' }}>
            {/* Table Header */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                p: 1.5,
                bgcolor: style.bg,
                borderBottom: '1px solid',
                borderColor: 'divider',
                cursor: 'pointer',
                '&:hover': { bgcolor: `${style.bg}dd` },
              }}
              onClick={() => toggleTable(group.tableName)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton size="small">
                  {collapsedTables.has(group.tableName) ? <ExpandIcon /> : <CollapseIcon />}
                </IconButton>
                <TableIcon sx={{ color: style.color, fontSize: 22 }} />
                <Typography variant="subtitle1" fontWeight={600}>
                  {group.displayName}
                </Typography>
                <Chip label={group.tableName} size="small" sx={{ fontFamily: 'monospace', fontSize: 10 }} />
              </Box>
              <Chip
                icon={<DocumentedIcon sx={{ fontSize: 14 }} />}
                label={`${group.documentedCount}/${group.elements.length}`}
                size="small"
                color={group.documentedCount === group.elements.length ? 'success' : 'default'}
                variant="outlined"
              />
            </Box>

            {/* Table Content - ALL REQUIRED COLUMNS */}
            <Collapse in={!collapsedTables.has(group.tableName)}>
              <TableContainer sx={{ maxHeight: 600 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 130 }}>PDE Column</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 130 }}>Business Name</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', minWidth: 200 }}>Business Description</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 100 }}>PDE Type</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 100 }}>Format</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 120 }}>ISO Element</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 150 }}>ISO Path</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 80 }}>Formats</TableCell>
                      <TableCell sx={{ fontWeight: 'bold', bgcolor: '#fafafa', width: 50 }}>Edit</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {group.elements.map((el) => (
                      <TableRow
                        key={el.catalog_id}
                        hover
                        sx={{
                          bgcolor: el.business_description ? undefined : 'rgba(255, 152, 0, 0.05)',
                        }}
                      >
                        {/* PDE Column */}
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                            {el.pde_column_name}
                          </Typography>
                        </TableCell>

                        {/* Business Name */}
                        <TableCell>
                          <Typography variant="body2" fontSize={11} fontWeight={el.business_name ? 500 : 400}>
                            {el.business_name || <span style={{ color: '#999', fontStyle: 'italic' }}>-</span>}
                          </Typography>
                        </TableCell>

                        {/* Business Description */}
                        <TableCell>
                          <Tooltip title={el.business_description || 'No description'} arrow>
                            <Typography
                              variant="body2"
                              fontSize={11}
                              sx={{
                                maxWidth: 250,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                color: el.business_description ? 'text.primary' : '#999',
                                fontStyle: el.business_description ? 'normal' : 'italic',
                              }}
                            >
                              {el.business_description || 'No description'}
                            </Typography>
                          </Tooltip>
                        </TableCell>

                        {/* PDE Data Type */}
                        <TableCell>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 10 }}>
                            {el.pde_data_type || '-'}
                          </Typography>
                        </TableCell>

                        {/* Data Format */}
                        <TableCell>
                          <Typography variant="body2" fontSize={10} color={el.data_format ? 'text.primary' : 'text.disabled'}>
                            {el.data_format || '-'}
                          </Typography>
                        </TableCell>

                        {/* ISO Element Name */}
                        <TableCell>
                          {el.iso_element_name ? (
                            <Chip label={el.iso_element_name} size="small" color="secondary" variant="outlined" sx={{ fontSize: 9, maxWidth: 110 }} />
                          ) : (
                            <Typography color="text.disabled" fontSize={10}>-</Typography>
                          )}
                        </TableCell>

                        {/* ISO Element Path */}
                        <TableCell>
                          {el.iso_element_path ? (
                            <Tooltip title={el.iso_element_path}>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: 9, maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {el.iso_element_path}
                              </Typography>
                            </Tooltip>
                          ) : (
                            <Typography color="text.disabled" fontSize={10}>-</Typography>
                          )}
                        </TableCell>

                        {/* Legacy Formats (Clickable) */}
                        <TableCell>
                          {el.legacy_mapping_count > 0 ? (
                            <Chip
                              label={el.legacy_mapping_count}
                              size="small"
                              color="primary"
                              sx={{ fontSize: 10, cursor: 'pointer' }}
                              onClick={(e) => handleFormatsClick(e, el)}
                            />
                          ) : (
                            <Typography color="text.disabled" fontSize={10}>0</Typography>
                          )}
                        </TableCell>

                        {/* Edit Button */}
                        <TableCell>
                          <IconButton size="small" onClick={() => setEditElement(el)}>
                            <EditIcon sx={{ fontSize: 16 }} />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Collapse>
          </Paper>
        );
      })}

      {/* No Results */}
      {!isLoading && groupedElements.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            {searchQuery ? 'No elements match your search' : 'No catalog elements found'}
          </Typography>
        </Paper>
      )}

      {/* Edit Dialog */}
      <EditElementDialog
        open={!!editElement}
        element={editElement}
        onClose={() => setEditElement(null)}
        onSave={handleSaveElement}
      />

      {/* Legacy Formats Popover */}
      {formatsPopoverElement && (
        <LegacyFormatsPopover
          element={formatsPopoverElement}
          anchorEl={formatsPopoverAnchor}
          onClose={handleFormatsClose}
        />
      )}
    </Box>
  );
};

export default CDMCatalogPage;
