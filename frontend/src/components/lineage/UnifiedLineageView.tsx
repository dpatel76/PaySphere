/**
 * Unified Lineage View Component
 * A single component for visualizing lineage at table-level or attribute-level
 * Supports filtering by: message type (forward), CDM entity (backward), report (backward)
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Drawer,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  CenterFocusStrong as FitIcon,
  Refresh as RefreshIcon,
  TableChart as TableIcon,
  Code as FieldIcon,
  ArrowForward as ForwardIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import cytoscape, { Core, ElementDefinition } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { useQuery } from '@tanstack/react-query';
import { lineageApi } from '../../api/client';
import { colors } from '../../styles/design-system';

// Register dagre layout
if (!cytoscape.prototype.hasOwnProperty('dagre')) {
  cytoscape.use(dagre);
}

// Zone colors for styling nodes
const zoneColors: Record<string, { bg: string; border: string; text: string }> = {
  bronze: { bg: colors.zones.bronze.light, border: colors.zones.bronze.main, text: colors.zones.bronze.dark },
  silver: { bg: colors.zones.silver.light, border: colors.zones.silver.main, text: colors.zones.silver.dark },
  gold: { bg: colors.zones.gold.light, border: colors.zones.gold.main, text: colors.zones.gold.dark },
  analytics: { bg: colors.zones.analytical.light, border: colors.zones.analytical.main, text: colors.zones.analytical.dark },
  analytical: { bg: colors.zones.analytical.light, border: colors.zones.analytical.main, text: colors.zones.analytical.dark },
  report: { bg: '#e8f5e9', border: '#4caf50', text: '#1b5e20' },
};

// Standard Gold CDM entities used by most payment formats
const standardGoldEntities = [
  'cdm_payment_instruction',
  'cdm_party',
  'cdm_account',
  'cdm_financial_institution',
];

// Normalized identifier tables added in ISO 20022 CDM enhancements
const identifierTables = [
  'cdm_party_identifier',
  'cdm_account_identifier',
  'cdm_fi_identifier',
  'cdm_payment_identifier',
];

// Table routing - maps message types to their actual Bronze/Silver/Gold tables
// Gold layer includes ALL applicable CDM entities + identifier tables for complete lineage
// ISO 20022 formats now use shared Silver tables (stg_iso20022_pacs008, stg_iso20022_pain001, etc.)
const tableRouting: Record<string, { bronze: string[]; silver: string[]; gold: string[] }> = {
  // ==========================================
  // ISO 20022 Core Formats
  // ==========================================
  'pain.001': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pain001'],  // Shared ISO 20022 table
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'pain.002': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_pain002'],
    gold: ['cdm_payment_status', 'cdm_payment_instruction', 'cdm_party', ...identifierTables],
  },
  'pacs.008': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Shared ISO 20022 table
    gold: [...standardGoldEntities, 'cdm_fx_rate', ...identifierTables],
  },
  'pacs.009': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs009'],  // Shared ISO 20022 table
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'pacs.002': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_pacs002'],
    gold: ['cdm_payment_status', 'cdm_payment_instruction', ...identifierTables],
  },
  'camt.053': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_camt053'],  // Shared ISO 20022 table
    gold: ['cdm_account_statement', 'cdm_transaction', 'cdm_account', ...identifierTables],
  },

  // ==========================================
  // SWIFT MT Formats
  // ==========================================
  'MT103': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_mt103'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'MT202': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_mt202'],
    gold: ['cdm_payment_instruction', 'cdm_party', 'cdm_financial_institution', ...identifierTables],
  },
  'MT940': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_mt940'],
    gold: ['cdm_account_statement', 'cdm_transaction', 'cdm_account', ...identifierTables],
  },

  // ==========================================
  // US Regional Formats
  // ==========================================
  'FEDWIRE': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='FEDWIRE'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'ACH': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_ach'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'CHIPS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='CHIPS'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'RTP': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='RTP'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'FEDNOW': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='FEDNOW'
    gold: [...standardGoldEntities, ...identifierTables],
  },

  // ==========================================
  // EU Regional Formats
  // ==========================================
  'SEPA': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pain001'],  // Uses shared pain.001 table with source_format='SEPA'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'TARGET2': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs009'],  // Uses shared pacs.009 table with source_format='TARGET2'
    gold: [...standardGoldEntities, ...identifierTables],
  },

  // ==========================================
  // UK Regional Formats
  // ==========================================
  'CHAPS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='CHAPS'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'FPS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='FPS'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'BACS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_bacs'],
    gold: ['cdm_payment_instruction', 'cdm_party', 'cdm_account', ...identifierTables],
  },

  // ==========================================
  // Asia-Pacific Regional Formats
  // ==========================================
  'NPP': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='NPP'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'MEPS_PLUS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='MEPS_PLUS'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'RTGS_HK': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='RTGS_HK'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'CNAPS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_cnaps'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'BOJNET': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_bojnet'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'KFTC': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_kftc'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'INSTAPAY': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='INSTAPAY'
    gold: [...standardGoldEntities, ...identifierTables],
  },

  // ==========================================
  // Middle East Regional Formats
  // ==========================================
  'UAEFTS': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_iso20022_pacs008'],  // Uses shared pacs.008 table with source_format='UAEFTS'
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'SARIE': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_sarie'],
    gold: [...standardGoldEntities, ...identifierTables],
  },

  // ==========================================
  // Latin America & Other Regional Formats
  // ==========================================
  'PIX': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_pix'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'UPI': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_upi'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'PROMPTPAY': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_promptpay'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
  'PAYNOW': {
    bronze: ['raw_payment_messages'],
    silver: ['stg_paynow'],
    gold: [...standardGoldEntities, ...identifierTables],
  },
};

// Friendly display names for CDM entity tables
const cdmEntityLabels: Record<string, string> = {
  // Core CDM entities
  'cdm_payment_instruction': 'Payment Instruction',
  'cdm_party': 'Party',
  'cdm_account': 'Account',
  'cdm_financial_institution': 'Financial Institution',
  'cdm_payment_status': 'Payment Status',
  'cdm_fx_rate': 'FX Rate',
  'cdm_account_statement': 'Account Statement',
  'cdm_transaction': 'Transaction',
  // Normalized identifier tables (ISO 20022 CDM enhancements)
  'cdm_party_identifier': 'Party Identifier',
  'cdm_account_identifier': 'Account Identifier',
  'cdm_fi_identifier': 'FI Identifier',
  'cdm_payment_identifier': 'Payment Identifier',
};

// All 29 supported message formats
const allMessageFormats = [
  'pain.001', 'pain.002', 'pacs.008', 'pacs.009', 'pacs.002', 'camt.053',
  'MT103', 'MT202', 'MT940',
  'FEDWIRE', 'ACH', 'CHIPS', 'RTP', 'FEDNOW',
  'SEPA', 'TARGET2',
  'CHAPS', 'FPS', 'BACS',
  'NPP', 'MEPS_PLUS', 'RTGS_HK', 'CNAPS', 'BOJNET', 'KFTC', 'INSTAPAY',
  'UAEFTS', 'SARIE',
  'PIX', 'UPI', 'PROMPTPAY', 'PAYNOW',
];

// Get all unique Silver tables from tableRouting
const getAllSilverTables = (): string[] => {
  const tables = new Set<string>();
  Object.values(tableRouting).forEach(routing => {
    routing.silver.forEach(t => tables.add(t));
  });
  return Array.from(tables);
};

// CDM Entity backward routing - maps CDM entities to their source message types and tables
// Updated to include all 29 formats and the shared ISO 20022 Silver tables
const entityRouting: Record<string, { messageTypes: string[]; silverTables: string[]; bronzeTables: string[] }> = {
  'cdm_payment_instruction': {
    messageTypes: allMessageFormats.filter(f => !['pain.002', 'pacs.002', 'camt.053', 'MT940'].includes(f)),
    silverTables: getAllSilverTables().filter(t => !['stg_pain002', 'stg_pacs002', 'stg_iso20022_camt053', 'stg_mt940'].includes(t)),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_party': {
    messageTypes: allMessageFormats.filter(f => !['pain.002', 'pacs.002', 'camt.053', 'MT940'].includes(f)),
    silverTables: getAllSilverTables().filter(t => !['stg_pain002', 'stg_pacs002', 'stg_iso20022_camt053', 'stg_mt940'].includes(t)),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_account': {
    messageTypes: allMessageFormats.filter(f => !['pain.002', 'pacs.002', 'MT202'].includes(f)),
    silverTables: getAllSilverTables().filter(t => !['stg_pain002', 'stg_pacs002', 'stg_mt202'].includes(t)),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_financial_institution': {
    messageTypes: allMessageFormats.filter(f => !['pain.002', 'pacs.002', 'camt.053', 'MT940', 'BACS'].includes(f)),
    silverTables: getAllSilverTables().filter(t => !['stg_pain002', 'stg_pacs002', 'stg_iso20022_camt053', 'stg_mt940', 'stg_bacs'].includes(t)),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_payment_status': {
    messageTypes: ['pain.002', 'pacs.002'],
    silverTables: ['stg_pain002', 'stg_pacs002'],
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_fx_rate': {
    messageTypes: ['pacs.008', 'MT103', 'FEDWIRE', 'CHIPS', 'CHAPS', 'FPS', 'NPP', 'MEPS_PLUS', 'RTGS_HK', 'UAEFTS', 'INSTAPAY'],
    silverTables: ['stg_iso20022_pacs008', 'stg_mt103'],
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_account_statement': {
    messageTypes: ['camt.053', 'MT940'],
    silverTables: ['stg_iso20022_camt053', 'stg_mt940'],
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_transaction': {
    messageTypes: ['camt.053', 'MT940'],
    silverTables: ['stg_iso20022_camt053', 'stg_mt940'],
    bronzeTables: ['raw_payment_messages'],
  },
  // Normalized identifier tables
  'cdm_party_identifier': {
    messageTypes: allMessageFormats,
    silverTables: getAllSilverTables(),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_account_identifier': {
    messageTypes: allMessageFormats,
    silverTables: getAllSilverTables(),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_fi_identifier': {
    messageTypes: allMessageFormats,
    silverTables: getAllSilverTables(),
    bronzeTables: ['raw_payment_messages'],
  },
  'cdm_payment_identifier': {
    messageTypes: allMessageFormats,
    silverTables: getAllSilverTables(),
    bronzeTables: ['raw_payment_messages'],
  },
};

// Report backward routing - maps reports to CDM entities and further to source
const reportRouting: Record<string, { cdmEntities: string[]; description: string }> = {
  'FATCA_8966': {
    cdmEntities: ['cdm_party', 'cdm_account', 'cdm_payment_instruction'],
    description: 'Account holder reporting for US tax purposes',
  },
  'FINCEN_CTR': {
    cdmEntities: ['cdm_payment_instruction', 'cdm_party', 'cdm_account'],
    description: 'Cash transactions over $10,000',
  },
  'FINCEN_SAR': {
    cdmEntities: ['cdm_payment_instruction', 'cdm_party', 'cdm_account'],
    description: 'Suspicious transaction reporting',
  },
  'AUSTRAC_IFTI': {
    cdmEntities: ['cdm_payment_instruction', 'cdm_party', 'cdm_financial_institution'],
    description: 'International transfers reporting',
  },
  'FINTRAC_EFT': {
    cdmEntities: ['cdm_payment_instruction', 'cdm_party', 'cdm_account'],
    description: 'Electronic funds transfer reporting',
  },
  'OECD_CRS': {
    cdmEntities: ['cdm_party', 'cdm_account'],
    description: 'Cross-border tax information exchange',
  },
};

// Default routing for unknown message types
const defaultRouting = {
  bronze: ['raw_payment_messages'],
  silver: ['stg_payment_instruction'],
  gold: ['cdm_payment_instruction'],
};

export type LineageDirection = 'forward' | 'backward';
export type FilterType = 'message_type' | 'cdm_entity' | 'report';
export type ViewLevel = 'table' | 'attribute';

interface UnifiedLineageViewProps {
  direction?: LineageDirection;
  filterType?: FilterType;
  filterValue?: string;
  viewLevel?: ViewLevel;
  onNodeClick?: (nodeId: string, nodeType: string) => void;
  height?: number | string;
  showControls?: boolean;
  showSelector?: boolean;
}

// Cytoscape stylesheet with compound node support for entity grouping
// Using 'any' cast for styles to avoid TypeScript strict type checking issues with Cytoscape
const graphStyles: any[] = [
  // Zone container (compound parent) nodes
  {
    selector: 'node[type="zone"]',
    style: {
      'background-color': '#f8f9fa',
      'background-opacity': 0.3,
      'border-width': 2,
      'border-color': '#dee2e6',
      'border-style': 'dashed',
      label: 'data(label)',
      'text-valign': 'top',
      'text-halign': 'center',
      'font-size': 14,
      'font-weight': 'bold',
      color: '#495057',
      'text-margin-y': 10,
      padding: 20,
    },
  },
  // Default node style
  {
    selector: 'node',
    style: {
      'background-color': '#f5f5f5',
      'border-width': 2,
      'border-color': '#666',
      label: 'data(label)',
      'text-valign': 'center',
      'text-halign': 'center',
      'font-size': 11,
      'text-wrap': 'wrap',
      'text-max-width': 120,
      width: 150,
      height: 55,
      shape: 'roundrectangle',
    },
  },
  // Table/Entity nodes (compound parents for fields)
  {
    selector: 'node[type="table"]',
    style: {
      'background-color': 'data(bgColor)',
      'border-color': 'data(borderColor)',
      color: 'data(textColor)',
      'font-weight': 'bold',
      'font-size': 12,
      'text-valign': 'top',
      'text-halign': 'center',
      'text-margin-y': 8,
      padding: 15,
      width: 'label',
      height: 'label',
      'min-width': 180,
      'min-height': 60,
    },
  },
  // Field nodes (children inside tables)
  {
    selector: 'node[type="field"]',
    style: {
      'background-color': '#ffffff',
      'border-color': 'data(borderColor)',
      'border-style': 'solid',
      'border-width': 1,
      'font-size': 10,
      width: 130,
      height: 28,
      shape: 'roundrectangle',
      'text-valign': 'center',
      'text-halign': 'center',
      'text-wrap': 'ellipsis',
      'text-max-width': 120,
    },
  },
  // Selected node
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': colors.primary.main,
      'background-color': colors.primary.light,
    },
  },
  // Parent (compound) nodes when they contain children
  {
    selector: ':parent',
    style: {
      'text-valign': 'top',
      'text-halign': 'center',
    },
  },
  // Default edge style
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': '#999',
      'target-arrow-color': '#999',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 1.2,
    },
  },
  // Table-to-table transformation edges
  {
    selector: 'edge[type="table_transform"]',
    style: {
      width: 3,
      'line-color': colors.primary.main,
      'target-arrow-color': colors.primary.main,
    },
  },
  // Field-level mapping edges
  {
    selector: 'edge[type="field_mapping"]',
    style: {
      width: 1.5,
      'line-color': colors.info.main,
      'target-arrow-color': colors.info.main,
      'line-style': 'solid',
      'arrow-scale': 0.8,
    },
  },
  // Selected edge
  {
    selector: 'edge:selected',
    style: {
      width: 4,
      'line-color': colors.primary.dark,
      'target-arrow-color': colors.primary.dark,
    },
  },
];

const UnifiedLineageView: React.FC<UnifiedLineageViewProps> = ({
  direction = 'forward',
  filterType = 'message_type',
  filterValue = 'pain.001',
  viewLevel: initialViewLevel = 'table',
  onNodeClick,
  height = 600,
  showControls = true,
  showSelector = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [viewLevel, setViewLevel] = useState<ViewLevel>(initialViewLevel);
  const [selectedValue, setSelectedValue] = useState(filterValue);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [fieldPanelOpen, setFieldPanelOpen] = useState(false);
  const [selectedFieldInfo, setSelectedFieldInfo] = useState<any>(null);

  // Sync selectedValue with filterValue prop when it changes externally
  useEffect(() => {
    setSelectedValue(filterValue);
  }, [filterValue]);

  // Fetch available options based on filter type
  const { data: messageTypes } = useQuery({
    queryKey: ['messageTypes'],
    queryFn: () => lineageApi.getSupportedMessageTypes(),
    enabled: filterType === 'message_type' && showSelector,
  });

  const { data: cdmEntities } = useQuery({
    queryKey: ['cdmEntities'],
    queryFn: () => lineageApi.getCDMEntities(),
    enabled: filterType === 'cdm_entity' && showSelector,
  });

  const { data: reports } = useQuery({
    queryKey: ['reports'],
    queryFn: () => lineageApi.getSupportedReports(),
    enabled: filterType === 'report' && showSelector,
  });

  // Fetch field lineage for attribute view
  const { data: fieldLineage, isLoading: loadingFields, refetch: refetchFields } = useQuery({
    queryKey: ['fieldLineage', selectedValue],
    queryFn: () => lineageApi.getFieldLineage(selectedValue, {}),
    enabled: viewLevel === 'attribute' && filterType === 'message_type',
  });

  // Build elements for forward table-level view (message type -> bronze -> silver -> gold)
  // Shows ALL applicable CDM entities for complete lineage visualization
  const buildForwardTableElements = useCallback((): ElementDefinition[] => {
    const elements: ElementDefinition[] = [];
    const routing = tableRouting[selectedValue] || defaultRouting;

    // Add Bronze tables
    routing.bronze.forEach((table) => {
      const style = zoneColors.bronze;
      elements.push({
        data: {
          id: `bronze.${table}`,
          label: table,
          type: 'table',
          layer: 'bronze',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });
    });

    // Add Silver tables
    routing.silver.forEach((table) => {
      const style = zoneColors.silver;
      elements.push({
        data: {
          id: `silver.${table}`,
          label: table,
          type: 'table',
          layer: 'silver',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });
    });

    // Add Gold CDM entity tables with friendly labels
    routing.gold.forEach((table) => {
      const style = zoneColors.gold;
      const displayLabel = cdmEntityLabels[table] || table;
      elements.push({
        data: {
          id: `gold.${table}`,
          label: `${displayLabel}\n(${table})`,
          type: 'table',
          layer: 'gold',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });
    });

    // Add edges Bronze -> Silver
    routing.bronze.forEach(bronzeTable => {
      routing.silver.forEach(silverTable => {
        elements.push({
          data: {
            id: `edge-${bronzeTable}-${silverTable}`,
            source: `bronze.${bronzeTable}`,
            target: `silver.${silverTable}`,
            type: 'table_transform',
          },
        });
      });
    });

    // Add edges Silver -> Gold (to all CDM entities)
    routing.silver.forEach(silverTable => {
      routing.gold.forEach(goldTable => {
        elements.push({
          data: {
            id: `edge-${silverTable}-${goldTable}`,
            source: `silver.${silverTable}`,
            target: `gold.${goldTable}`,
            type: 'table_transform',
          },
        });
      });
    });

    return elements;
  }, [selectedValue]);

  // Build elements for backward entity lineage (gold entity <- silver <- bronze)
  const buildEntityBackwardElements = useCallback((): ElementDefinition[] => {
    const elements: ElementDefinition[] = [];
    const routing = entityRouting[selectedValue];

    if (!routing) {
      // Fallback for unknown entity
      const style = zoneColors.gold;
      elements.push({
        data: {
          id: `gold.${selectedValue}`,
          label: selectedValue,
          type: 'table',
          layer: 'gold',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });
      return elements;
    }

    // Add Gold entity
    const goldStyle = zoneColors.gold;
    elements.push({
      data: {
        id: `gold.${selectedValue}`,
        label: selectedValue,
        type: 'table',
        layer: 'gold',
        bgColor: goldStyle.bg,
        borderColor: goldStyle.border,
        textColor: goldStyle.text,
      },
    });

    // Add Silver tables
    routing.silverTables.forEach((table) => {
      const style = zoneColors.silver;
      elements.push({
        data: {
          id: `silver.${table}`,
          label: table,
          type: 'table',
          layer: 'silver',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });

      // Add edge Silver -> Gold
      elements.push({
        data: {
          id: `edge-${table}-${selectedValue}`,
          source: `silver.${table}`,
          target: `gold.${selectedValue}`,
          type: 'table_transform',
        },
      });
    });

    // Add Bronze tables
    routing.bronzeTables.forEach((table) => {
      const style = zoneColors.bronze;
      elements.push({
        data: {
          id: `bronze.${table}`,
          label: table,
          type: 'table',
          layer: 'bronze',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });

      // Add edges Bronze -> all Silver tables
      routing.silverTables.forEach((silverTable) => {
        elements.push({
          data: {
            id: `edge-${table}-${silverTable}`,
            source: `bronze.${table}`,
            target: `silver.${silverTable}`,
            type: 'table_transform',
          },
        });
      });
    });

    return elements;
  }, [selectedValue]);

  // Build elements for backward report lineage (report <- gold <- silver <- bronze)
  const buildReportBackwardElements = useCallback((): ElementDefinition[] => {
    const elements: ElementDefinition[] = [];
    const routing = reportRouting[selectedValue];

    if (!routing) {
      return elements;
    }

    // Add Report node
    const reportStyle = zoneColors.report;
    elements.push({
      data: {
        id: `report.${selectedValue}`,
        label: selectedValue.replace('_', ' '),
        type: 'table',
        layer: 'report',
        bgColor: reportStyle.bg,
        borderColor: reportStyle.border,
        textColor: reportStyle.text,
      },
    });

    // Track all silver and bronze tables from CDM entities
    const allSilverTables = new Set<string>();
    const allBronzeTables = new Set<string>();

    // Add Gold entities and edges to report
    routing.cdmEntities.forEach((entity) => {
      const goldStyle = zoneColors.gold;
      elements.push({
        data: {
          id: `gold.${entity}`,
          label: entity,
          type: 'table',
          layer: 'gold',
          bgColor: goldStyle.bg,
          borderColor: goldStyle.border,
          textColor: goldStyle.text,
        },
      });

      // Edge Gold -> Report
      elements.push({
        data: {
          id: `edge-${entity}-${selectedValue}`,
          source: `gold.${entity}`,
          target: `report.${selectedValue}`,
          type: 'table_transform',
        },
      });

      // Get routing for this entity
      const entityRoute = entityRouting[entity];
      if (entityRoute) {
        entityRoute.silverTables.forEach(t => allSilverTables.add(t));
        entityRoute.bronzeTables.forEach(t => allBronzeTables.add(t));
      }
    });

    // Add Silver tables
    allSilverTables.forEach((table) => {
      const style = zoneColors.silver;
      elements.push({
        data: {
          id: `silver.${table}`,
          label: table,
          type: 'table',
          layer: 'silver',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });

      // Add edges Silver -> relevant Gold entities
      routing.cdmEntities.forEach((entity) => {
        const entityRoute = entityRouting[entity];
        if (entityRoute && entityRoute.silverTables.includes(table)) {
          elements.push({
            data: {
              id: `edge-${table}-${entity}`,
              source: `silver.${table}`,
              target: `gold.${entity}`,
              type: 'table_transform',
            },
          });
        }
      });
    });

    // Add Bronze tables
    allBronzeTables.forEach((table) => {
      const style = zoneColors.bronze;
      elements.push({
        data: {
          id: `bronze.${table}`,
          label: table,
          type: 'table',
          layer: 'bronze',
          bgColor: style.bg,
          borderColor: style.border,
          textColor: style.text,
        },
      });

      // Add edges Bronze -> all Silver tables
      allSilverTables.forEach((silverTable) => {
        elements.push({
          data: {
            id: `edge-${table}-${silverTable}`,
            source: `bronze.${table}`,
            target: `silver.${silverTable}`,
            type: 'table_transform',
          },
        });
      });
    });

    return elements;
  }, [selectedValue]);

  // Complete field lineage mappings - Bronze -> Silver -> Gold CDM entities
  // Normalized CDM: Multiple Silver fields map to same CDM entity fields (e.g., debtor_name & creditor_name -> cdm_party.name)
  // Only fields with actual Bronze sources are included to ensure all fields have incoming edges
  const completeFieldMappings: Record<string, {
    // Each entry maps: bronze XPath -> silver field -> gold entity.field
    // Format: { bronze, silver, goldEntity, goldField, transform? }
    mappings: {
      bronze: string;
      silver: string;
      goldEntity: string;
      goldEntityLabel: string;
      goldField: string;
      transform?: string;
    }[];
  }> = {
    'pain.001': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'GrpHdr/MsgId', silver: 'msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'GrpHdr/CreDtTm', silver: 'creation_date_time', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'PmtInf/ReqdExctnDt', silver: 'requested_execution_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'requested_execution_date' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/PmtId/UETR', silver: 'uetr', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'uetr' },
        { bronze: 'CdtTrfTxInf/PmtId/InstrId', silver: 'instruction_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instruction_id_ext' },
        { bronze: 'CdtTrfTxInf/Amt/InstdAmt', silver: 'instructed_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'CdtTrfTxInf/Amt/@Ccy', silver: 'instructed_currency', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_currency' },
        { bronze: 'CdtTrfTxInf/Purp/Cd', silver: 'purpose_code', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'purpose' },
        { bronze: 'CdtTrfTxInf/ChrgBr', silver: 'charge_bearer', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'charge_bearer', transform: 'lookup' },
        { bronze: 'CdtTrfTxInf/RmtInf/Ustrd', silver: 'remittance_info', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'remittance_unstructured' },
        // === PARTY (Normalized - Debtor & Creditor map to same entity type) ===
        { bronze: 'PmtInf/Dbtr/Nm', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'PmtInf/Dbtr/Id/OrgId/LEI', silver: 'debtor_lei', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'lei' },
        { bronze: 'PmtInf/Dbtr/PstlAdr/Ctry', silver: 'debtor_country', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'country' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Id/OrgId/LEI', silver: 'creditor_lei', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'lei' },
        { bronze: 'CdtTrfTxInf/Cdtr/PstlAdr/Ctry', silver: 'creditor_country', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'country' },
        // === ACCOUNT (Normalized) ===
        { bronze: 'PmtInf/DbtrAcct/Id/IBAN', silver: 'debtor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: 'PmtInf/DbtrAcct/Ccy', silver: 'debtor_acct_ccy', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'currency' },
        { bronze: 'CdtTrfTxInf/CdtrAcct/Id/IBAN', silver: 'creditor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        // === FINANCIAL INSTITUTION (Normalized) ===
        { bronze: 'PmtInf/DbtrAgt/FinInstnId/BICFI', silver: 'debtor_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'PmtInf/DbtrAgt/FinInstnId/Nm', silver: 'debtor_agent_name', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'institution_name' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'creditor_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/Nm', silver: 'creditor_agent_name', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'institution_name' },
      ],
    },
    'pacs.008': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'GrpHdr/MsgId', silver: 'msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'GrpHdr/CreDtTm', silver: 'creation_date_time', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/PmtId/UETR', silver: 'uetr', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'uetr' },
        { bronze: 'CdtTrfTxInf/PmtId/TxId', silver: 'transaction_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'transaction_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'settlement_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt/@Ccy', silver: 'settlement_currency', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_currency' },
        { bronze: 'CdtTrfTxInf/InstdAmt', silver: 'instructed_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'CdtTrfTxInf/InstdAmt/@Ccy', silver: 'instructed_currency', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_currency' },
        { bronze: 'CdtTrfTxInf/ChrgBr', silver: 'charge_bearer', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'charge_bearer' },
        // === PARTY ===
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Dbtr/PstlAdr/Ctry', silver: 'debtor_country', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'country' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/PstlAdr/Ctry', silver: 'creditor_country', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'country' },
        // === ACCOUNT ===
        { bronze: 'CdtTrfTxInf/DbtrAcct/Id/IBAN', silver: 'debtor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: 'CdtTrfTxInf/CdtrAcct/Id/IBAN', silver: 'creditor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        // === FINANCIAL INSTITUTION ===
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'debtor_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'creditor_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/InstgAgt/FinInstnId/BICFI', silver: 'instructing_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/InstdAgt/FinInstnId/BICFI', silver: 'instructed_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'MT103': {
      mappings: [
        // === PAYMENT INSTRUCTION (SWIFT FIN fields use tag numbers) ===
        { bronze: ':20:', silver: 'sender_reference', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: ':21:', silver: 'related_reference', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'related_reference' },
        { bronze: ':23B:', silver: 'bank_operation_code', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'bank_operation_code' },
        { bronze: ':32A:', silver: 'value_date_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        { bronze: ':32A:', silver: 'instructed_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: ':32A:', silver: 'instructed_currency', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_currency' },
        { bronze: ':33B:', silver: 'original_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'original_instructed_amount' },
        { bronze: ':36:', silver: 'exchange_rate', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'exchange_rate' },
        { bronze: ':71A:', silver: 'charge_bearer', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'charge_bearer', transform: 'lookup' },
        { bronze: ':70:', silver: 'remittance_info', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'remittance_unstructured' },
        { bronze: ':121:', silver: 'uetr', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'uetr' },
        // === PARTY ===
        { bronze: ':50K:', silver: 'ordering_customer', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: ':50K:', silver: 'ordering_customer_acct', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'account_number' },
        { bronze: ':59:', silver: 'beneficiary_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: ':59:', silver: 'beneficiary_address', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'address' },
        // === ACCOUNT ===
        { bronze: ':50K:', silver: 'ordering_acct_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: ':59:', silver: 'beneficiary_acct', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        // === FINANCIAL INSTITUTION ===
        { bronze: ':52A:', silver: 'ordering_institution', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':53A:', silver: 'senders_correspondent', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':54A:', silver: 'receivers_correspondent', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':56A:', silver: 'intermediary_institution', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':57A:', silver: 'account_with_institution', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'MT202': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: ':20:', silver: 'transaction_ref', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: ':21:', silver: 'related_reference', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'related_reference' },
        { bronze: ':32A:', silver: 'value_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        { bronze: ':32A:', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: ':32A:', silver: 'currency', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_currency' },
        { bronze: ':121:', silver: 'uetr', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'uetr' },
        // === FINANCIAL INSTITUTION ===
        { bronze: ':52A:', silver: 'ordering_institution', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':53A:', silver: 'senders_correspondent', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':54A:', silver: 'receivers_correspondent', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':56A:', silver: 'intermediary', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':57A:', silver: 'account_with_inst', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: ':58A:', silver: 'beneficiary_inst', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'FEDWIRE': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'IMAD', silver: 'imad', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'OMAD', silver: 'omad', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'related_reference' },
        { bronze: 'TypeCode', silver: 'type_code', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'payment_type' },
        { bronze: 'SubTypeCode', silver: 'subtype_code', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'payment_subtype' },
        { bronze: 'Amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'Currency', silver: 'currency', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_currency' },
        { bronze: 'BusinessDate', silver: 'business_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        { bronze: 'SenderRef', silver: 'sender_reference', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'BeneficiaryRef', silver: 'beneficiary_ref', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'remittance_reference' },
        // === PARTY (Originator & Beneficiary) ===
        { bronze: 'OriginatorName', silver: 'originator_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'OriginatorAddress', silver: 'originator_address', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'address' },
        { bronze: 'OriginatorId', silver: 'originator_id', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'identification' },
        { bronze: 'BeneficiaryName', silver: 'beneficiary_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'BeneficiaryAddress', silver: 'beneficiary_address', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'address' },
        { bronze: 'BeneficiaryId', silver: 'beneficiary_id', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'identification' },
        // === ACCOUNT ===
        { bronze: 'OriginatorAcct', silver: 'originator_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'BeneficiaryAcct', silver: 'beneficiary_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        // === FINANCIAL INSTITUTION (ABA Routing Numbers) ===
        { bronze: 'SenderABA', silver: 'sender_aba', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'SenderName', silver: 'sender_fi_name', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'institution_name' },
        { bronze: 'ReceiverABA', silver: 'receiver_aba', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'ReceiverName', silver: 'receiver_fi_name', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'institution_name' },
        { bronze: 'OriginatorFI_ABA', silver: 'originator_fi_aba', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'BeneficiaryFI_ABA', silver: 'beneficiary_fi_aba', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'ACH': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'TraceNumber', silver: 'trace_number', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'TransactionCode', silver: 'transaction_code', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'payment_type' },
        { bronze: 'Amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'EffectiveDate', silver: 'effective_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'requested_execution_date' },
        { bronze: 'CompanyId', silver: 'company_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'batch_id' },
        { bronze: 'CompanyEntryDesc', silver: 'entry_description', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'remittance_unstructured' },
        { bronze: 'IndividualId', silver: 'individual_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        // === PARTY ===
        { bronze: 'CompanyName', silver: 'company_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'IndividualName', silver: 'individual_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        // === ACCOUNT ===
        { bronze: 'DFIAccountNumber', silver: 'account_number', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'AccountType', silver: 'account_type', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_type' },
        // === FINANCIAL INSTITUTION ===
        { bronze: 'ReceivingDFI', silver: 'receiving_dfi', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'OriginatingDFI', silver: 'originating_dfi', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'SEPA': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'MsgId', silver: 'msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CreDtTm', silver: 'creation_date_time', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'EndToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'InstdAmt', silver: 'instructed_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'ReqdExctnDt', silver: 'requested_execution_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'requested_execution_date' },
        { bronze: 'RmtInf/Ustrd', silver: 'remittance_info', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'remittance_unstructured' },
        // === PARTY ===
        { bronze: 'Dbtr/Nm', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'Cdtr/Nm', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        // === ACCOUNT ===
        { bronze: 'DbtrAcct/Id/IBAN', silver: 'debtor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: 'CdtrAcct/Id/IBAN', silver: 'creditor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        // === FINANCIAL INSTITUTION ===
        { bronze: 'DbtrAgt/FinInstnId/BIC', silver: 'debtor_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtrAgt/FinInstnId/BIC', silver: 'creditor_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'CHAPS': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'MsgId', silver: 'msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CreDtTm', silver: 'creation_date_time', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'EndToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'UETR', silver: 'uetr', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'uetr' },
        { bronze: 'IntrBkSttlmAmt', silver: 'settlement_amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'IntrBkSttlmDt', silver: 'settlement_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        { bronze: 'ChrgBr', silver: 'charge_bearer', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'charge_bearer' },
        // === PARTY ===
        { bronze: 'Dbtr/Nm', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'Cdtr/Nm', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        // === ACCOUNT ===
        { bronze: 'DbtrAcct/Id/IBAN', silver: 'debtor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: 'DbtrAcct/Id/Othr/Id', silver: 'debtor_sort_acct', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'CdtrAcct/Id/IBAN', silver: 'creditor_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: 'CdtrAcct/Id/Othr/Id', silver: 'creditor_sort_acct', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        // === FINANCIAL INSTITUTION ===
        { bronze: 'DbtrAgt/FinInstnId/BICFI', silver: 'debtor_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'debtor_sort_code', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'CdtrAgt/FinInstnId/BICFI', silver: 'creditor_agent_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'creditor_sort_code', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'BACS': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'TransactionCode', silver: 'transaction_code', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'payment_type' },
        { bronze: 'ProcessingDate', silver: 'processing_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        { bronze: 'Amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'Reference', silver: 'reference', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'UserRef', silver: 'user_reference', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'remittance_reference' },
        // === PARTY ===
        { bronze: 'OriginatorName', silver: 'originator_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'DestinationName', silver: 'destination_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        // === ACCOUNT ===
        { bronze: 'OriginatorAcctNo', silver: 'originator_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'DestinationAcctNo', silver: 'destination_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        // === FINANCIAL INSTITUTION (Sort Codes) ===
        { bronze: 'OriginatorSortCode', silver: 'originator_sort_code', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'DestinationSortCode', silver: 'destination_sort_code', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'RTP': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'MsgId', silver: 'msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CreDtTm', silver: 'creation_date_time', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'EndToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'TxId', silver: 'transaction_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'transaction_id' },
        { bronze: 'IntrBkSttlmAmt', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'AccptncDtTm', silver: 'acceptance_datetime', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        // === PARTY ===
        { bronze: 'Dbtr/Nm', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'Cdtr/Nm', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        // === ACCOUNT ===
        { bronze: 'DbtrAcct/Id', silver: 'debtor_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'CdtrAcct/Id', silver: 'creditor_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        // === FINANCIAL INSTITUTION ===
        { bronze: 'DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'debtor_routing', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'creditor_routing', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'FEDNOW': {
      mappings: [
        // === PAYMENT INSTRUCTION ===
        { bronze: 'MsgId', silver: 'msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CreDtTm', silver: 'creation_date_time', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'EndToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'UETR', silver: 'uetr', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'uetr' },
        { bronze: 'IntrBkSttlmAmt', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'IntrBkSttlmDt', silver: 'settlement_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'value_date' },
        // === PARTY ===
        { bronze: 'Dbtr/Nm', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'Cdtr/Nm', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        // === ACCOUNT ===
        { bronze: 'DbtrAcct/Id', silver: 'debtor_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'CdtrAcct/Id', silver: 'creditor_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        // === FINANCIAL INSTITUTION ===
        { bronze: 'DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'debtor_routing', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'creditor_routing', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    // ==========================================
    // Additional Message Formats (ISO 20022 shared Silver tables)
    // ==========================================
    'TARGET2': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'GrpHdr/CreDtTm', silver: 'grp_hdr_cre_dt_tm', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'dbtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'cdtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'FPS': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAcct/Id/Othr/Id', silver: 'dbtr_acct_id_othr_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'CdtTrfTxInf/CdtrAcct/Id/Othr/Id', silver: 'cdtr_acct_id_othr_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'dbtr_agt_clr_sys_mmb_id', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'cdtr_agt_clr_sys_mmb_id', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'CHIPS': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/PmtId/ClrSysRef', silver: 'pmt_id_clr_sys_ref', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'clearing_system_reference' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'dbtr_agt_clr_sys_mmb_id', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/ClrSysMmbId/MmbId', silver: 'cdtr_agt_clr_sys_mmb_id', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'NPP': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAcct/Prxy/Id', silver: 'dbtr_acct_prxy_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
        { bronze: 'CdtTrfTxInf/CdtrAcct/Prxy/Id', silver: 'cdtr_acct_prxy_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'dbtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'cdtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'MEPS_PLUS': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'dbtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'cdtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'RTGS_HK': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'dbtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'cdtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'UAEFTS': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'dbtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'cdtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    'INSTAPAY': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'CdtTrfTxInf/PmtId/EndToEndId', silver: 'pmt_id_end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'CdtTrfTxInf/IntrBkSttlmAmt', silver: 'intr_bk_sttlm_amt', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'interbank_settlement_amount' },
        { bronze: 'CdtTrfTxInf/Dbtr/Nm', silver: 'dbtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/Cdtr/Nm', silver: 'cdtr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'CdtTrfTxInf/DbtrAgt/FinInstnId/BICFI', silver: 'dbtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
        { bronze: 'CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI', silver: 'cdtr_agt_bic', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'bic' },
      ],
    },
    // JSON-based formats
    'PIX': {
      mappings: [
        { bronze: 'transactionId', silver: 'transaction_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'creationDate', silver: 'creation_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'endToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'debtor.name', silver: 'debtor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'creditor.name', silver: 'creditor_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'debtor.account.number', silver: 'debtor_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'creditor.pixKey', silver: 'creditor_pix_key', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
        { bronze: 'debtor.ispbCode', silver: 'debtor_ispb', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'creditor.ispbCode', silver: 'creditor_ispb', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'UPI': {
      mappings: [
        { bronze: 'txnId', silver: 'txn_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'txnDate', silver: 'txn_date', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'creation_datetime' },
        { bronze: 'refId', silver: 'ref_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'payer.name', silver: 'payer_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'payee.name', silver: 'payee_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'payer.vpa', silver: 'payer_vpa', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
        { bronze: 'payee.vpa', silver: 'payee_vpa', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
        { bronze: 'payer.ifsc', silver: 'payer_ifsc', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
        { bronze: 'payee.ifsc', silver: 'payee_ifsc', goldEntity: 'cdm_financial_institution', goldEntityLabel: 'Financial Institution', goldField: 'national_clearing_code' },
      ],
    },
    'PROMPTPAY': {
      mappings: [
        { bronze: 'transactionId', silver: 'transaction_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'endToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'senderName', silver: 'sender_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'receiverName', silver: 'receiver_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'senderAccount', silver: 'sender_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'receiverProxyId', silver: 'receiver_proxy_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
      ],
    },
    'PAYNOW': {
      mappings: [
        { bronze: 'transactionId', silver: 'transaction_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'message_id' },
        { bronze: 'endToEndId', silver: 'end_to_end_id', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'end_to_end_id' },
        { bronze: 'amount', silver: 'amount', goldEntity: 'cdm_payment_instruction', goldEntityLabel: 'Payment Instruction', goldField: 'instructed_amount' },
        { bronze: 'senderName', silver: 'sender_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'receiverName', silver: 'receiver_name', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'senderAccount', silver: 'sender_account', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: 'receiverProxyId', silver: 'receiver_proxy_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'proxy_id' },
      ],
    },
    // Statement formats
    'camt.053': {
      mappings: [
        { bronze: 'GrpHdr/MsgId', silver: 'grp_hdr_msg_id', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'statement_id' },
        { bronze: 'Stmt/Id', silver: 'stmt_id', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'statement_number' },
        { bronze: 'Stmt/CreDtTm', silver: 'stmt_cre_dt_tm', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'creation_datetime' },
        { bronze: 'Stmt/Acct/Id/IBAN', silver: 'acct_id_iban', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'iban' },
        { bronze: 'Stmt/Acct/Ownr/Nm', silver: 'acct_ownr_nm', goldEntity: 'cdm_party', goldEntityLabel: 'Party', goldField: 'name' },
        { bronze: 'Stmt/Bal/Amt', silver: 'bal_amt', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'balance_amount' },
        { bronze: 'Stmt/Ntry/Amt', silver: 'ntry_amt', goldEntity: 'cdm_transaction', goldEntityLabel: 'Transaction', goldField: 'amount' },
      ],
    },
    'MT940': {
      mappings: [
        { bronze: ':20:', silver: 'transaction_ref', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'statement_id' },
        { bronze: ':25:', silver: 'account_id', goldEntity: 'cdm_account', goldEntityLabel: 'Account', goldField: 'account_number' },
        { bronze: ':28C:', silver: 'statement_number', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'statement_number' },
        { bronze: ':60F:', silver: 'opening_balance', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'opening_balance' },
        { bronze: ':62F:', silver: 'closing_balance', goldEntity: 'cdm_account_statement', goldEntityLabel: 'Account Statement', goldField: 'closing_balance' },
        { bronze: ':61:', silver: 'entry_amount', goldEntity: 'cdm_transaction', goldEntityLabel: 'Transaction', goldField: 'amount' },
        { bronze: ':86:', silver: 'entry_info', goldEntity: 'cdm_transaction', goldEntityLabel: 'Transaction', goldField: 'additional_info' },
      ],
    },
  };

  // Helper to truncate label text
  const truncateLabel = (label: string, maxLen: number = 18): string => {
    if (label.length <= maxLen) return label;
    return label.substring(0, maxLen - 2) + '..';
  };

  // Build elements for attribute-level view with full Bronze->Silver->Gold lineage
  // Uses DYNAMIC data from API (loaded from YAML mapping files) - NOT static frontend config
  const buildAttributeElements = useCallback((): ElementDefinition[] => {
    const elements: ElementDefinition[] = [];
    const silverTable = tableRouting[selectedValue]?.silver[0] || 'stg_payment';

    // Use API data if available (dynamic from YAML mappings)
    if (fieldLineage && Array.isArray(fieldLineage) && fieldLineage.length > 0) {
      // Collect unique tables/entities from API data
      const bronzeTables = new Set<string>();
      const silverTables = new Set<string>();
      const goldTables = new Set<string>();

      fieldLineage.forEach((m: any) => {
        if (m.source_layer === 'bronze') bronzeTables.add(m.source_table);
        if (m.source_layer === 'silver') silverTables.add(m.source_table);
        if (m.target_layer === 'silver') silverTables.add(m.target_table);
        if (m.target_layer === 'gold') goldTables.add(m.target_table);
      });

      // Add Bronze table nodes
      bronzeTables.forEach(table => {
        elements.push({
          data: {
            id: `bronze.${table}`,
            label: table,
            type: 'table',
            layer: 'bronze',
            bgColor: zoneColors.bronze.bg,
            borderColor: zoneColors.bronze.border,
            textColor: zoneColors.bronze.text,
          },
        });
      });

      // Add Silver table nodes
      silverTables.forEach(table => {
        elements.push({
          data: {
            id: `silver.${table}`,
            label: table,
            type: 'table',
            layer: 'silver',
            bgColor: zoneColors.silver.bg,
            borderColor: zoneColors.silver.border,
            textColor: zoneColors.silver.text,
          },
        });
      });

      // Add Gold CDM entity nodes with friendly labels
      goldTables.forEach(table => {
        const label = cdmEntityLabels[table] || table;
        elements.push({
          data: {
            id: `gold.${table}`,
            label: label,
            type: 'table',
            layer: 'gold',
            bgColor: zoneColors.gold.bg,
            borderColor: zoneColors.gold.border,
            textColor: zoneColors.gold.text,
          },
        });
      });

      // Track added fields and create nodes/edges from API data
      const fieldsAdded = new Set<string>();

      fieldLineage.forEach((mapping: any, idx: number) => {
        const sourceTable = mapping.source_table;
        const targetTable = mapping.target_table;
        const sourceField = mapping.source_field;
        const targetField = mapping.target_field;
        const sourceLayer = mapping.source_layer;
        const targetLayer = mapping.target_layer;

        // Create unique field IDs
        const sourceFieldId = `${sourceLayer}.field.${sourceTable}.${sourceField.replace(/[\/\[\]@:]/g, '_')}`;
        const targetFieldId = `${targetLayer}.field.${targetTable}.${targetField.replace(/[\/\[\]@:]/g, '_')}`;

        // Add source field node if not already added
        if (!fieldsAdded.has(sourceFieldId)) {
          const shortLabel = sourceField.includes('/') ? sourceField.split('/').pop() || sourceField : sourceField;
          elements.push({
            data: {
              id: sourceFieldId,
              label: truncateLabel(shortLabel, 16),
              fullPath: sourceField,
              type: 'field',
              layer: sourceLayer,
              parent: `${sourceLayer}.${sourceTable}`,
              borderColor: zoneColors[sourceLayer as keyof typeof zoneColors]?.border || '#666',
            },
          });
          fieldsAdded.add(sourceFieldId);
        }

        // Add target field node if not already added
        if (!fieldsAdded.has(targetFieldId)) {
          elements.push({
            data: {
              id: targetFieldId,
              label: truncateLabel(targetField, 16),
              type: 'field',
              layer: targetLayer,
              parent: `${targetLayer}.${targetTable}`,
              borderColor: zoneColors[targetLayer as keyof typeof zoneColors]?.border || '#666',
            },
          });
          fieldsAdded.add(targetFieldId);
        }

        // Add edge
        elements.push({
          data: {
            id: `edge-${idx}`,
            source: sourceFieldId,
            target: targetFieldId,
            type: 'field_mapping',
            transform: mapping.transformation_type || 'direct',
          },
        });
      });

      return elements;
    }

    // Fallback to static config if no API data (for message types without YAML mappings)
    const mappingConfig = completeFieldMappings[selectedValue];

    // Collect unique entities from static mappings
    const goldEntitiesMap = new Map<string, string>();
    if (mappingConfig) {
      mappingConfig.mappings.forEach(m => {
        goldEntitiesMap.set(m.goldEntity, m.goldEntityLabel);
      });
    } else {
      // Default entities for unknown message types
      goldEntitiesMap.set('cdm_payment_instruction', 'Payment Instruction');
      goldEntitiesMap.set('cdm_party', 'Party');
      goldEntitiesMap.set('cdm_account', 'Account');
      goldEntitiesMap.set('cdm_financial_institution', 'Financial Institution');
    }

    // Add table nodes
    elements.push({
      data: {
        id: 'bronze.raw_payment_messages',
        label: 'raw_payment_messages',
        type: 'table',
        layer: 'bronze',
        bgColor: zoneColors.bronze.bg,
        borderColor: zoneColors.bronze.border,
        textColor: zoneColors.bronze.text,
      },
    });

    elements.push({
      data: {
        id: `silver.${silverTable}`,
        label: silverTable,
        type: 'table',
        layer: 'silver',
        bgColor: zoneColors.silver.bg,
        borderColor: zoneColors.silver.border,
        textColor: zoneColors.silver.text,
      },
    });

    goldEntitiesMap.forEach((label, entity) => {
      elements.push({
        data: {
          id: `gold.${entity}`,
          label: label,
          type: 'table',
          layer: 'gold',
          bgColor: zoneColors.gold.bg,
          borderColor: zoneColors.gold.border,
          textColor: zoneColors.gold.text,
        },
      });
    });

    // Use static mappings if available
    if (mappingConfig && mappingConfig.mappings.length > 0) {
      const bronzeFieldsAdded = new Set<string>();
      const silverFieldsAdded = new Set<string>();
      const goldFieldsAdded = new Set<string>();

      mappingConfig.mappings.forEach((mapping, idx) => {
        const bronzeFieldId = `bronze.field.raw_payment_messages.${mapping.bronze.replace(/[\/\[\]@:]/g, '_')}`;
        const silverFieldId = `silver.field.${silverTable}.${mapping.silver}`;
        const goldFieldId = `gold.field.${mapping.goldEntity}.${mapping.goldField}`;

        if (!bronzeFieldsAdded.has(bronzeFieldId)) {
          const shortLabel = mapping.bronze.split('/').pop() || mapping.bronze;
          elements.push({
            data: {
              id: bronzeFieldId,
              label: truncateLabel(shortLabel, 16),
              fullPath: mapping.bronze,
              type: 'field',
              layer: 'bronze',
              parent: 'bronze.raw_payment_messages',
              borderColor: zoneColors.bronze.border,
            },
          });
          bronzeFieldsAdded.add(bronzeFieldId);
        }

        if (!silverFieldsAdded.has(silverFieldId)) {
          elements.push({
            data: {
              id: silverFieldId,
              label: truncateLabel(mapping.silver, 16),
              type: 'field',
              layer: 'silver',
              parent: `silver.${silverTable}`,
              borderColor: zoneColors.silver.border,
            },
          });
          silverFieldsAdded.add(silverFieldId);
        }

        if (!goldFieldsAdded.has(goldFieldId)) {
          elements.push({
            data: {
              id: goldFieldId,
              label: truncateLabel(mapping.goldField, 16),
              type: 'field',
              layer: 'gold',
              parent: `gold.${mapping.goldEntity}`,
              borderColor: zoneColors.gold.border,
            },
          });
          goldFieldsAdded.add(goldFieldId);
        }

        elements.push({
          data: { id: `edge-b2s-${idx}`, source: bronzeFieldId, target: silverFieldId, type: 'field_mapping' },
        });
        elements.push({
          data: { id: `edge-s2g-${idx}`, source: silverFieldId, target: goldFieldId, type: 'field_mapping', transform: mapping.transform || 'direct' },
        });
      });
    } else {
      // No mappings - show table-level edges only
      elements.push({
        data: { id: 'edge-bronze-silver', source: 'bronze.raw_payment_messages', target: `silver.${silverTable}`, type: 'table_transform' },
      });
      goldEntitiesMap.forEach((_, entity) => {
        elements.push({
          data: { id: `edge-silver-${entity}`, source: `silver.${silverTable}`, target: `gold.${entity}`, type: 'table_transform' },
        });
      });
    }

    return elements;
  }, [fieldLineage, selectedValue]);

  // Build elements based on filter type and view level
  const buildElements = useCallback((): ElementDefinition[] => {
    if (viewLevel === 'attribute') {
      return buildAttributeElements();
    }

    if (filterType === 'message_type') {
      return buildForwardTableElements();
    }

    if (filterType === 'cdm_entity') {
      return buildEntityBackwardElements();
    }

    if (filterType === 'report') {
      return buildReportBackwardElements();
    }

    return [];
  }, [viewLevel, filterType, buildAttributeElements, buildForwardTableElements, buildEntityBackwardElements, buildReportBackwardElements]);

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const elements = buildElements();

    // Destroy existing instance
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Create new instance
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements,
      style: graphStyles,
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: viewLevel === 'attribute' ? 30 : 60,
        rankSep: viewLevel === 'attribute' ? 100 : 150,
        padding: 50,
      } as any,
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    // Add click handler
    cyRef.current.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeId = node.id();
      const nodeType = node.data('type');
      setSelectedNode(nodeId);

      if (nodeType === 'field') {
        setSelectedFieldInfo({
          id: nodeId,
          label: node.data('label'),
          layer: node.data('layer'),
        });
        setFieldPanelOpen(true);
      }

      onNodeClick?.(nodeId, nodeType);
    });

    // Fit to container
    cyRef.current.fit(undefined, 50);

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [viewLevel, buildElements, onNodeClick]);

  // Zoom controls
  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.2);
  const handleFit = () => cyRef.current?.fit(undefined, 50);
  const handleRefresh = () => refetchFields();

  const handleViewLevelChange = (_: React.MouseEvent<HTMLElement>, newLevel: ViewLevel | null) => {
    if (newLevel) setViewLevel(newLevel);
  };

  const isLoading = loadingFields;

  // Get options for selector
  const getOptions = () => {
    if (filterType === 'message_type') {
      return messageTypes?.supported_types || [
        { id: 'pain.001', display_name: 'pain.001 - Customer Credit Transfer' },
        { id: 'pacs.008', display_name: 'pacs.008 - FI Credit Transfer' },
        { id: 'MT103', display_name: 'MT103 - Single Customer Credit Transfer' },
        { id: 'FEDWIRE', display_name: 'FEDWIRE - Federal Reserve Wire' },
      ];
    }
    if (filterType === 'cdm_entity') {
      return cdmEntities?.entities || [
        { table: 'cdm_payment_instruction', display_name: 'Payment Instruction' },
        { table: 'cdm_party', display_name: 'Party' },
        { table: 'cdm_account', display_name: 'Account' },
      ];
    }
    if (filterType === 'report') {
      return reports?.reports || [
        { id: 'FATCA_8966', name: 'FATCA Form 8966', jurisdiction: 'US' },
        { id: 'FINCEN_CTR', name: 'FinCEN CTR', jurisdiction: 'US' },
      ];
    }
    return [];
  };

  const getOptionValue = (option: any) => {
    if (filterType === 'message_type') return option.id;
    if (filterType === 'cdm_entity') return option.table;
    if (filterType === 'report') return option.id;
    return option.id || option.table;
  };

  const getOptionLabel = (option: any) => {
    if (filterType === 'message_type') return option.display_name;
    if (filterType === 'cdm_entity') return option.display_name;
    if (filterType === 'report') return `${option.name} (${option.jurisdiction})`;
    return option.display_name || option.name;
  };

  const getSelectorLabel = () => {
    if (filterType === 'message_type') return 'Message Type';
    if (filterType === 'cdm_entity') return 'CDM Entity';
    if (filterType === 'report') return 'Report';
    return 'Filter';
  };

  return (
    <Paper elevation={1} sx={{ height, display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      {showControls && (
        <Box
          sx={{
            p: 2,
            borderBottom: `1px solid ${colors.grey[200]}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {showSelector && (
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>{getSelectorLabel()}</InputLabel>
                <Select
                  value={selectedValue}
                  label={getSelectorLabel()}
                  onChange={(e) => setSelectedValue(e.target.value)}
                >
                  {getOptions().map((option: any) => (
                    <MenuItem key={getOptionValue(option)} value={getOptionValue(option)}>
                      {getOptionLabel(option)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <Chip
              label={`${direction === 'forward' ? 'Forward' : 'Backward'} Lineage`}
              size="small"
              color={direction === 'forward' ? 'primary' : 'secondary'}
              variant="outlined"
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* View Level Toggle */}
            <ToggleButtonGroup
              value={viewLevel}
              exclusive
              onChange={handleViewLevelChange}
              size="small"
            >
              <ToggleButton value="table">
                <Tooltip title="Table View">
                  <TableIcon fontSize="small" />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="attribute">
                <Tooltip title="Attribute View">
                  <FieldIcon fontSize="small" />
                </Tooltip>
              </ToggleButton>
            </ToggleButtonGroup>

            {/* Zoom Controls */}
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Tooltip title="Zoom In">
                <IconButton size="small" onClick={handleZoomIn}>
                  <ZoomInIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Zoom Out">
                <IconButton size="small" onClick={handleZoomOut}>
                  <ZoomOutIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Fit to View">
                <IconButton size="small" onClick={handleFit}>
                  <FitIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Refresh">
                <IconButton size="small" onClick={handleRefresh}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Box>
      )}

      {/* Legend */}
      <Box
        sx={{
          px: 2,
          py: 1,
          borderBottom: `1px solid ${colors.grey[200]}`,
          display: 'flex',
          gap: 3,
          flexWrap: 'wrap',
        }}
      >
        {Object.entries(zoneColors).slice(0, filterType === 'report' ? 5 : 4).map(([zone, style]) => (
          <Box key={zone} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: 1,
                backgroundColor: style.bg,
                border: `2px solid ${style.border}`,
              }}
            />
            <Typography variant="caption" sx={{ textTransform: 'capitalize', fontWeight: 500 }}>
              {zone}
            </Typography>
          </Box>
        ))}
        <Box sx={{ ml: 2, display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box sx={{ width: 24, height: 2, backgroundColor: colors.primary.main }} />
          <Typography variant="caption">Transform</Typography>
        </Box>
        {viewLevel === 'attribute' && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 24, height: 2, borderBottom: `2px dashed ${colors.info.main}` }} />
            <Typography variant="caption">Field Mapping</Typography>
          </Box>
        )}
      </Box>

      {/* Graph Container */}
      <Box sx={{ flex: 1, position: 'relative', minHeight: 300 }}>
        {isLoading && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 10,
            }}
          >
            <CircularProgress />
          </Box>
        )}

        <Box
          ref={containerRef}
          sx={{
            width: '100%',
            height: '100%',
            minHeight: 300,
            backgroundColor: colors.grey[50],
          }}
        />
      </Box>

      {/* Selected Node Info */}
      {selectedNode && (
        <Box
          sx={{
            p: 1.5,
            borderTop: `1px solid ${colors.grey[200]}`,
            backgroundColor: colors.grey[50],
          }}
        >
          <Typography variant="body2" color="text.secondary">
            Selected: <strong>{selectedNode}</strong>
          </Typography>
        </Box>
      )}

      {/* Field Details Drawer */}
      <Drawer
        anchor="right"
        open={fieldPanelOpen}
        onClose={() => setFieldPanelOpen(false)}
        PaperProps={{ sx: { width: 350 } }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight={600}>
              Field Details
            </Typography>
            <IconButton onClick={() => setFieldPanelOpen(false)} size="small">
              <CloseIcon />
            </IconButton>
          </Box>

          {selectedFieldInfo && (
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Field Name
              </Typography>
              <Typography variant="body1" fontWeight={500} gutterBottom>
                {selectedFieldInfo.label}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Layer
              </Typography>
              <Chip
                label={selectedFieldInfo.layer}
                size="small"
                sx={{
                  backgroundColor: zoneColors[selectedFieldInfo.layer]?.bg,
                  color: zoneColors[selectedFieldInfo.layer]?.text,
                  fontWeight: 600,
                }}
              />

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Lineage Path
              </Typography>
              <List dense>
                {fieldLineage?.filter((m: any) =>
                  m.source_field === selectedFieldInfo.label ||
                  m.target_field === selectedFieldInfo.label
                ).map((mapping: any, idx: number) => (
                  <ListItem key={idx} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: 12 }}>
                          <Chip label={mapping.source_layer} size="small" sx={{ fontSize: 10 }} />
                          <Typography variant="caption">{mapping.source_field}</Typography>
                          <ForwardIcon fontSize="small" sx={{ color: colors.grey[400] }} />
                          <Chip label={mapping.target_layer} size="small" sx={{ fontSize: 10 }} />
                          <Typography variant="caption">{mapping.target_field}</Typography>
                        </Box>
                      }
                      secondary={mapping.transformation_type || 'direct'}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      </Drawer>
    </Paper>
  );
};

export default UnifiedLineageView;
