/**
 * Data Lineage Visualization Page
 * Interactive graph visualization and tabular views for lineage across Bronze -> Silver -> Gold
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tabs,
  Tab,
  Alert,
  Drawer,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  AccountTree as LineageIcon,
  ArrowForward as ForwardIcon,
  ArrowBack as BackwardIcon,
  Search as SearchIcon,
  BubbleChart as GraphIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { lineageApi, graphApi } from '../api/client';
import { FieldLineage } from '../types';
import { colors, pipelineConfig } from '../styles/design-system';
import LineageGraphViewer from '../components/lineage/LineageGraphViewer';

const layerColors: Record<string, string> = {
  bronze: colors.zones.bronze.main,
  silver: colors.zones.silver.main,
  gold: colors.zones.gold.main,
  analytical: colors.zones.analytical.main,
};

const LineagePage: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [messageType, setMessageType] = useState('pain.001');
  const [fieldFilter, setFieldFilter] = useState('');
  const [layerFilter, setLayerFilter] = useState('');
  const [selectedEntity, setSelectedEntity] = useState('cdm_payment_instruction');
  const [selectedReport, setSelectedReport] = useState('FATCA_8966');
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [fieldPanelOpen, setFieldPanelOpen] = useState(false);

  // Fetch supported message types
  const { data: messageTypes } = useQuery({
    queryKey: ['messageTypes'],
    queryFn: () => lineageApi.getSupportedMessageTypes(),
  });

  // Fetch CDM entities
  const { data: cdmEntities } = useQuery({
    queryKey: ['cdmEntities'],
    queryFn: () => lineageApi.getCDMEntities(),
  });

  // Fetch reports
  const { data: reports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => lineageApi.getSupportedReports(),
  });

  // Fetch message type lineage (forward)
  const { data: forwardLineage, isLoading: loadingForward } = useQuery({
    queryKey: ['forwardLineage', messageType],
    queryFn: () => lineageApi.getMessageTypeLineage(messageType),
    enabled: selectedTab === 1,
  });

  // Fetch field lineage for search tab
  const { data: fieldLineage, isLoading: loadingFields } = useQuery({
    queryKey: ['fieldLineage', messageType, fieldFilter, layerFilter],
    queryFn: () => lineageApi.getFieldLineage(messageType, {
      field_name: fieldFilter || undefined,
      layer: layerFilter || undefined,
    }),
    enabled: selectedTab === 2,
  });

  // Fetch field lineage details for panel
  const { data: fieldLineageDetails } = useQuery({
    queryKey: ['fieldLineageDetails', messageType, selectedField],
    queryFn: () => graphApi.getFieldLineage(messageType, selectedField!),
    enabled: !!selectedField && fieldPanelOpen,
  });

  // Fetch backward lineage from entity
  const { data: entityLineage, isLoading: loadingEntity } = useQuery({
    queryKey: ['entityLineage', selectedEntity],
    queryFn: () => lineageApi.getBackwardLineageFromEntity(selectedEntity),
    enabled: selectedTab === 3,
  });

  // Fetch backward lineage from report
  const { data: reportLineage, isLoading: loadingReport } = useQuery({
    queryKey: ['reportLineage', selectedReport],
    queryFn: () => lineageApi.getBackwardLineageFromReport(selectedReport),
    enabled: selectedTab === 4,
  });

  // Fetch lineage graph for visualization
  const { data: lineageGraph } = useQuery({
    queryKey: ['lineageGraph', messageType],
    queryFn: () => lineageApi.getLineageGraph(messageType),
    enabled: selectedTab === 1,
  });

  const handleNodeClick = (nodeId: string, nodeType: string) => {
    if (nodeType === 'field') {
      setSelectedField(nodeId);
      setFieldPanelOpen(true);
    }
  };

  const LayerBadge: React.FC<{ layer: string }> = ({ layer }) => (
    <Chip
      label={layer}
      size="small"
      sx={{
        backgroundColor: `${layerColors[layer]}20`,
        color: layerColors[layer],
        fontWeight: 600,
        fontSize: 11,
      }}
    />
  );

  const LineageFlowDiagram: React.FC = () => {
    if (!lineageGraph) return null;

    return (
      <Box sx={{ p: 3, overflowX: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 3 }}>
          {pipelineConfig.layers.map((layer, index) => (
            <React.Fragment key={layer}>
              <Paper
                sx={{
                  p: 2,
                  minWidth: 160,
                  border: `2px solid ${layerColors[layer]}`,
                  borderRadius: 2,
                  textAlign: 'center',
                }}
              >
                <Typography variant="subtitle2" fontWeight={600} sx={{ color: layerColors[layer] }}>
                  {pipelineConfig.layerNames[layer]}
                </Typography>
                <Typography variant="h5" fontWeight={700} sx={{ my: 1 }}>
                  {lineageGraph.nodes?.filter((n: any) => n.layer === layer).length || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  fields mapped
                </Typography>
              </Paper>
              {index < pipelineConfig.layers.length - 1 && (
                <ForwardIcon sx={{ fontSize: 32, color: colors.grey[400] }} />
              )}
            </React.Fragment>
          ))}
        </Box>
      </Box>
    );
  };

  // Field Lineage Panel (Drawer)
  const FieldLineagePanel = () => (
    <Drawer
      anchor="right"
      open={fieldPanelOpen}
      onClose={() => setFieldPanelOpen(false)}
      PaperProps={{ sx: { width: 400 } }}
    >
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={600}>
            Field Lineage
          </Typography>
          <IconButton onClick={() => setFieldPanelOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {selectedField && (
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Selected Field
            </Typography>
            <Typography variant="body1" fontWeight={500} gutterBottom>
              {selectedField}
            </Typography>

            <Divider sx={{ my: 2 }} />

            {fieldLineageDetails ? (
              <>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Field Variations Across Layers
                </Typography>
                <List dense>
                  {fieldLineageDetails.nodes?.map((node: any) => (
                    <ListItem key={node.id} sx={{ py: 0.5 }}>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={node.layer || node.id?.split('.')[0]}
                              size="small"
                              sx={{
                                backgroundColor: `${layerColors[node.layer || node.id?.split('.')[0]] || colors.grey[400]}20`,
                                color: layerColors[node.layer || node.id?.split('.')[0]] || colors.grey[600],
                                fontWeight: 600,
                                fontSize: 10,
                                minWidth: 60,
                              }}
                            />
                            <Typography variant="body2" fontWeight={500}>
                              {node.field_name || node.label}
                            </Typography>
                          </Box>
                        }
                        secondary={node.data_type || 'string'}
                      />
                    </ListItem>
                  ))}
                </List>

                {fieldLineageDetails.edges?.length > 0 && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Transformations
                    </Typography>
                    <List dense>
                      {fieldLineageDetails.edges?.map((edge: any, idx: number) => (
                        <ListItem key={idx} sx={{ py: 0.5 }}>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="caption">
                                  {edge.source?.split('.').pop()}
                                </Typography>
                                <ForwardIcon fontSize="small" sx={{ color: colors.grey[400] }} />
                                <Typography variant="caption">
                                  {edge.target?.split('.').pop()}
                                </Typography>
                              </Box>
                            }
                            secondary={
                              <Chip
                                label={edge.transform_type || 'direct'}
                                size="small"
                                variant="outlined"
                                sx={{ mt: 0.5 }}
                              />
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}
              </>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Loading field lineage details...
              </Typography>
            )}
          </Box>
        )}
      </Box>
    </Drawer>
  );

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Data Lineage
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Trace data flow from source to target across the pipeline layers
        </Typography>
      </Box>

      {/* Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={(_, v) => setSelectedTab(v)}
          sx={{ borderBottom: `1px solid ${colors.grey[200]}` }}
        >
          <Tab icon={<GraphIcon />} label="Graph View" iconPosition="start" />
          <Tab icon={<ForwardIcon />} label="Forward Lineage" iconPosition="start" />
          <Tab icon={<SearchIcon />} label="Field Search" iconPosition="start" />
          <Tab icon={<BackwardIcon />} label="Entity Backward" iconPosition="start" />
          <Tab icon={<BackwardIcon />} label="Report Backward" iconPosition="start" />
        </Tabs>
      </Card>

      {/* Tab 0: Interactive Graph View */}
      {selectedTab === 0 && (
        <Card sx={{ height: 700 }}>
          <CardContent sx={{ height: '100%', p: 0 }}>
            <LineageGraphViewer
              messageType={messageType}
              selectedField={selectedField || undefined}
              onNodeClick={handleNodeClick}
            />
          </CardContent>
        </Card>
      )}

      {/* Tab 1: Forward Lineage */}
      {selectedTab === 1 && (
        <Grid container spacing={3}>
          <Grid size={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight={600}>
                    Message Type Lineage
                  </Typography>
                  <FormControl size="small" sx={{ minWidth: 200 }}>
                    <InputLabel>Message Type</InputLabel>
                    <Select
                      value={messageType}
                      label="Message Type"
                      onChange={(e) => setMessageType(e.target.value)}
                    >
                      {messageTypes?.supported_types?.map((mt: any) => (
                        <MenuItem key={mt.id} value={mt.id}>
                          {mt.display_name}
                        </MenuItem>
                      )) || (
                        <>
                          <MenuItem value="pain.001">pain.001</MenuItem>
                          <MenuItem value="MT103">MT103</MenuItem>
                          <MenuItem value="pacs.008">pacs.008</MenuItem>
                        </>
                      )}
                    </Select>
                  </FormControl>
                </Box>

                <LineageFlowDiagram />

                {forwardLineage && (
                  <Box sx={{ mt: 3 }}>
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, md: 6 }}>
                        <Paper sx={{ p: 2, backgroundColor: `${colors.zones.bronze.main}08` }}>
                          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            Bronze - Silver Mappings
                          </Typography>
                          <Typography variant="h4" fontWeight={700}>
                            {forwardLineage.bronze_to_silver?.field_count || 0}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            fields mapped
                          </Typography>
                        </Paper>
                      </Grid>
                      <Grid size={{ xs: 12, md: 6 }}>
                        <Paper sx={{ p: 2, backgroundColor: `${colors.zones.gold.main}08` }}>
                          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            Silver - Gold Mappings
                          </Typography>
                          <Typography variant="h4" fontWeight={700}>
                            {forwardLineage.silver_to_gold?.field_count || 0}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            fields mapped
                          </Typography>
                        </Paper>
                      </Grid>
                    </Grid>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Field Search */}
      {selectedTab === 2 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                size="small"
                placeholder="Search field name..."
                value={fieldFilter}
                onChange={(e) => setFieldFilter(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: colors.grey[400] }} />,
                }}
                sx={{ minWidth: 250 }}
              />
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Layer</InputLabel>
                <Select
                  value={layerFilter}
                  label="Layer"
                  onChange={(e) => setLayerFilter(e.target.value)}
                >
                  <MenuItem value="">All Layers</MenuItem>
                  <MenuItem value="bronze">Bronze</MenuItem>
                  <MenuItem value="silver">Silver</MenuItem>
                  <MenuItem value="gold">Gold</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Message Type</InputLabel>
                <Select
                  value={messageType}
                  label="Message Type"
                  onChange={(e) => setMessageType(e.target.value)}
                >
                  <MenuItem value="pain.001">pain.001</MenuItem>
                  <MenuItem value="MT103">MT103</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Source Layer</TableCell>
                    <TableCell>Source Field</TableCell>
                    <TableCell></TableCell>
                    <TableCell>Target Layer</TableCell>
                    <TableCell>Target Field</TableCell>
                    <TableCell>Transformation</TableCell>
                    <TableCell>Data Type</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fieldLineage?.map((field: FieldLineage, index: number) => (
                    <TableRow key={index}>
                      <TableCell>
                        <LayerBadge layer={field.source_layer} />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {field.source_field}
                        </Typography>
                        {field.source_path && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                            {field.source_path}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <ForwardIcon sx={{ color: colors.grey[400] }} />
                      </TableCell>
                      <TableCell>
                        <LayerBadge layer={field.target_layer} />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {field.target_field}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={field.transformation_type || 'DIRECT'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">{field.data_type}</Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                  {(!fieldLineage || fieldLineage.length === 0) && (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography color="text.secondary" sx={{ py: 3 }}>
                          No field lineage data found. Try adjusting your filters.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Tab 3: Entity Backward Lineage */}
      {selectedTab === 3 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <FormControl size="small" sx={{ minWidth: 250 }}>
                <InputLabel>CDM Entity</InputLabel>
                <Select
                  value={selectedEntity}
                  label="CDM Entity"
                  onChange={(e) => setSelectedEntity(e.target.value)}
                >
                  {cdmEntities?.entities?.map((entity: any) => (
                    <MenuItem key={entity.table} value={entity.table}>
                      {entity.display_name}
                    </MenuItem>
                  )) || (
                    <>
                      <MenuItem value="cdm_payment_instruction">Payment Instruction</MenuItem>
                      <MenuItem value="cdm_party">Party</MenuItem>
                      <MenuItem value="cdm_account">Account</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Box>

            {entityLineage && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    <strong>{entityLineage.entity_table}</strong> receives data from{' '}
                    <strong>{entityLineage.message_types?.length || 0}</strong> message types
                    through <strong>{entityLineage.source_mappings?.length || 0}</strong> field mappings.
                  </Typography>
                </Alert>

                {entityLineage.message_types?.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Source Message Types:</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {entityLineage.message_types.map((mt: string) => (
                        <Chip key={mt} label={mt} variant="outlined" size="small" />
                      ))}
                    </Box>
                  </Box>
                )}

                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Message Type</TableCell>
                        <TableCell>Source Layer</TableCell>
                        <TableCell>Source Field</TableCell>
                        <TableCell></TableCell>
                        <TableCell>Target Field</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {entityLineage.source_mappings?.map((mapping: any, index: number) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Chip label={mapping.message_type} size="small" />
                          </TableCell>
                          <TableCell>
                            <LayerBadge layer={mapping.source_layer} />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">{mapping.source_field}</Typography>
                          </TableCell>
                          <TableCell>
                            <ForwardIcon sx={{ color: colors.grey[400] }} />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight={500}>
                              {mapping.target_field}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab 4: Report Backward Lineage */}
      {selectedTab === 4 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <FormControl size="small" sx={{ minWidth: 300 }}>
                <InputLabel>Regulatory Report</InputLabel>
                <Select
                  value={selectedReport}
                  label="Regulatory Report"
                  onChange={(e) => setSelectedReport(e.target.value)}
                >
                  {reports?.reports?.map((report: any) => (
                    <MenuItem key={report.id} value={report.id}>
                      {report.name} ({report.jurisdiction})
                    </MenuItem>
                  )) || (
                    <>
                      <MenuItem value="FATCA_8966">FATCA Form 8966</MenuItem>
                      <MenuItem value="FINCEN_CTR">FinCEN CTR</MenuItem>
                      <MenuItem value="FINCEN_SAR">FinCEN SAR</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Box>

            {reportLineage && !reportLineage.error ? (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Report <strong>{selectedReport}</strong> pulls data from CDM entities
                    which trace back to source message types.
                  </Typography>
                </Alert>

                {reportLineage.fields?.length > 0 && (
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Report Field</TableCell>
                          <TableCell>CDM Entity</TableCell>
                          <TableCell>CDM Field</TableCell>
                          <TableCell>Source Message Types</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {reportLineage.fields.map((field: any, index: number) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Typography variant="body2" fontWeight={500}>
                                {field.report_field}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">{field.cdm_entity}</Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">{field.cdm_field}</Typography>
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                {field.source_message_types?.map((mt: string) => (
                                  <Chip key={mt} label={mt} size="small" variant="outlined" />
                                ))}
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Box>
            ) : (
              <Alert severity="warning">
                {reportLineage?.error || 'No lineage data available for this report'}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Field Lineage Panel */}
      <FieldLineagePanel />
    </Box>
  );
};

export default LineagePage;
