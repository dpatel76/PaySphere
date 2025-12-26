/**
 * Data Lineage Visualization Page
 * Uses UnifiedLineageView component across all tabs with different filters
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Paper,
  Chip,
} from '@mui/material';
import {
  AccountTree as LineageIcon,
  ArrowForward as ForwardIcon,
  ArrowBack as BackwardIcon,
  BubbleChart as GraphIcon,
  Description as ReportIcon,
  TableChart as EntityIcon,
} from '@mui/icons-material';
import { lineageApi } from '../api/client';
import { colors } from '../styles/design-system';
import UnifiedLineageView from '../components/lineage/UnifiedLineageView';

const LineagePage: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [messageType, setMessageType] = useState('pain.001');
  const [selectedEntity, setSelectedEntity] = useState('cdm_payment_instruction');
  const [selectedReport, setSelectedReport] = useState('FATCA_8966');

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

  const handleNodeClick = (nodeId: string, nodeType: string) => {
    console.log('Node clicked:', nodeId, nodeType);
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Data Lineage
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Trace data flow from source to target across the pipeline layers.
          Toggle between table-level and attribute-level views.
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
          <Tab icon={<LineageIcon />} label="Attributes" iconPosition="start" />
          <Tab icon={<EntityIcon />} label="Entity Backward" iconPosition="start" />
          <Tab icon={<ReportIcon />} label="Report Backward" iconPosition="start" />
        </Tabs>
      </Card>

      {/* Tab 0: Graph View - Default unified view */}
      {selectedTab === 0 && (
        <Card>
          <CardContent sx={{ p: 0 }}>
            <Box sx={{ p: 2, borderBottom: `1px solid ${colors.grey[200]}` }}>
              <Typography variant="h6" fontWeight={600}>
                Unified Lineage Graph
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Select a message type to view its complete data flow from Bronze to Gold.
                Use the table/attribute toggle to switch between views.
              </Typography>
            </Box>
            <UnifiedLineageView
              direction="forward"
              filterType="message_type"
              filterValue={messageType}
              viewLevel="table"
              onNodeClick={handleNodeClick}
              height={650}
              showControls={true}
              showSelector={true}
            />
          </CardContent>
        </Card>
      )}

      {/* Tab 1: Forward Lineage with summary stats */}
      {selectedTab === 1 && (
        <Grid container spacing={3}>
          <Grid size={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" fontWeight={600}>
                    Message Type Forward Lineage
                  </Typography>
                  <FormControl size="small" sx={{ minWidth: 250 }}>
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
                          <MenuItem value="pain.001">pain.001 - Customer Credit Transfer</MenuItem>
                          <MenuItem value="pacs.008">pacs.008 - FI Credit Transfer</MenuItem>
                          <MenuItem value="MT103">MT103 - Single Customer Transfer</MenuItem>
                          <MenuItem value="FEDWIRE">FEDWIRE - Federal Reserve Wire</MenuItem>
                          <MenuItem value="ACH">ACH - Automated Clearing House</MenuItem>
                          <MenuItem value="SEPA">SEPA - Single Euro Payments</MenuItem>
                        </>
                      )}
                    </Select>
                  </FormControl>
                </Box>

                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Showing forward lineage for <strong>{messageType}</strong>:
                    how data flows from Bronze (raw) through Silver (staged) to Gold (CDM).
                    Click the attribute toggle to see field-level mappings.
                  </Typography>
                </Alert>

                <UnifiedLineageView
                  direction="forward"
                  filterType="message_type"
                  filterValue={messageType}
                  viewLevel="table"
                  onNodeClick={handleNodeClick}
                  height={550}
                  showControls={true}
                  showSelector={false}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Attributes View - Field-level lineage */}
      {selectedTab === 2 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Attribute-Level Lineage
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  View field mappings between Bronze, Silver, and Gold layers
                </Typography>
              </Box>
              <FormControl size="small" sx={{ minWidth: 250 }}>
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
                      <MenuItem value="pacs.008">pacs.008</MenuItem>
                      <MenuItem value="MT103">MT103</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Box>

            <UnifiedLineageView
              direction="forward"
              filterType="message_type"
              filterValue={messageType}
              viewLevel="attribute"
              onNodeClick={handleNodeClick}
              height={600}
              showControls={true}
              showSelector={false}
            />
          </CardContent>
        </Card>
      )}

      {/* Tab 3: Entity Backward Lineage */}
      {selectedTab === 3 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  CDM Entity Backward Lineage
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Select a CDM entity to see which message types feed into it
                </Typography>
              </Box>
              <FormControl size="small" sx={{ minWidth: 300 }}>
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
                      <MenuItem value="cdm_fx_rate">FX Rate</MenuItem>
                      <MenuItem value="cdm_payment_status">Payment Status</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Box>

            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Showing backward lineage for <strong>{selectedEntity}</strong>:
                which source tables and message types contribute data to this CDM entity.
              </Typography>
            </Alert>

            <UnifiedLineageView
              direction="backward"
              filterType="cdm_entity"
              filterValue={selectedEntity}
              viewLevel="table"
              onNodeClick={handleNodeClick}
              height={550}
              showControls={true}
              showSelector={false}
            />
          </CardContent>
        </Card>
      )}

      {/* Tab 4: Report Backward Lineage */}
      {selectedTab === 4 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Regulatory Report Backward Lineage
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Select a report to see which CDM entities and message types feed into it
                </Typography>
              </Box>
              <FormControl size="small" sx={{ minWidth: 350 }}>
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
                      <MenuItem value="FATCA_8966">FATCA Form 8966 (US)</MenuItem>
                      <MenuItem value="FINCEN_CTR">FinCEN CTR (US)</MenuItem>
                      <MenuItem value="FINCEN_SAR">FinCEN SAR (US)</MenuItem>
                      <MenuItem value="AUSTRAC_IFTI">AUSTRAC IFTI (AU)</MenuItem>
                      <MenuItem value="FINTRAC_EFT">FINTRAC EFT (CA)</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Box>

            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Showing backward lineage for <strong>{selectedReport}</strong>:
                trace report fields back through CDM entities to source message types.
              </Typography>
            </Alert>

            <UnifiedLineageView
              direction="backward"
              filterType="report"
              filterValue={selectedReport}
              viewLevel="table"
              onNodeClick={handleNodeClick}
              height={550}
              showControls={true}
              showSelector={false}
            />

            {/* Report Fields Summary */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
                Report Field Coverage
              </Typography>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" fontWeight={700} color="primary.main">
                        15
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Report Fields
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" fontWeight={700} color="success.main">
                        12
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Mapped to CDM
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" fontWeight={700} color="warning.main">
                        3
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Derived/Computed
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default LineagePage;
