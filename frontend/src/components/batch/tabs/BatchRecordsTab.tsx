/**
 * Batch Records Tab
 * Displays paginated records for a batch with layer selector and cross-zone comparison
 *
 * Cross-Zone Comparison organized by CDM entities:
 * 1. CDM_PAYMENT_INSTRUCTION - Core payment fields
 * 2. CDM_PARTY (DEBTOR) - Debtor party entity
 * 3. CDM_PARTY (CREDITOR) - Creditor party entity
 * 4. CDM_ACCOUNT (DEBTOR) - Debtor account entity
 * 5. CDM_ACCOUNT (CREDITOR) - Creditor account entity
 * 6. CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT) - Ordering bank
 * 7. CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT) - Beneficiary bank
 * 8. CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES) - Intermediary agents
 * 9. EXTENSION DATA - Format-specific extension fields
 * 10. LINEAGE & METADATA - Processing and audit fields
 */
import React, { useState, useMemo, useCallback } from 'react';
import {
  Box,
  ToggleButtonGroup,
  ToggleButton,
  Typography,
  Chip,
  Tooltip,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Paper,
  TextField,
  Button,
  Alert,
  Snackbar,
  Collapse,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridPaginationModel,
} from '@mui/x-data-grid';
import {
  Close as CloseIcon,
  CompareArrows as CompareIcon,
  Edit as EditIcon,
  Replay as ReplayIcon,
  Error as ErrorIcon,
  AccountBalance as BankIcon,
  Person as PersonIcon,
  AccountBalanceWallet as AccountIcon,
  Payment as PaymentIcon,
  Extension as ExtensionIcon,
  History as HistoryIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  UnfoldMore as UnfoldMoreIcon,
  UnfoldLess as UnfoldLessIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelineApi, reprocessApi, mappingsApi } from '../../../api/client';

interface BatchRecordsTabProps {
  batchId: string;
  messageType: string;
}

type LayerType = 'bronze' | 'silver' | 'gold';

const statusColors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  PROCESSED: 'success',
  PROMOTED: 'success',
  PROMOTED_TO_SILVER: 'success',
  PROMOTED_TO_GOLD: 'success',
  PENDING: 'warning',
  FAILED: 'error',
  VALIDATED: 'info',
  DQ_PASSED: 'success',
  DQ_FAILED: 'error',
};

const zoneColors = {
  bronze: { bg: '#FFF8E1', border: '#FF8F00', text: '#E65100' },
  silver: { bg: '#ECEFF1', border: '#607D8B', text: '#37474F' },
  gold: { bg: '#FFF9C4', border: '#FBC02D', text: '#F57F17' },
};

// Entity category icons and colors
const entityStyles = {
  'CDM_PAYMENT_INSTRUCTION': { icon: PaymentIcon, color: '#1976d2', bg: '#e3f2fd' },
  'CDM_PARTY (DEBTOR)': { icon: PersonIcon, color: '#7b1fa2', bg: '#f3e5f5' },
  'CDM_PARTY (CREDITOR)': { icon: PersonIcon, color: '#388e3c', bg: '#e8f5e9' },
  'CDM_PARTY (ULTIMATE)': { icon: PersonIcon, color: '#5d4037', bg: '#efebe9' },
  'CDM_ACCOUNT (DEBTOR)': { icon: AccountIcon, color: '#7b1fa2', bg: '#f3e5f5' },
  'CDM_ACCOUNT (CREDITOR)': { icon: AccountIcon, color: '#388e3c', bg: '#e8f5e9' },
  'CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)': { icon: BankIcon, color: '#7b1fa2', bg: '#f3e5f5' },
  'CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)': { icon: BankIcon, color: '#388e3c', bg: '#e8f5e9' },
  'CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)': { icon: BankIcon, color: '#ff8f00', bg: '#fff3e0' },
  'CDM_PAYMENT_STATUS': { icon: PaymentIcon, color: '#f57c00', bg: '#fff3e0' },
  'CDM_FX_RATE': { icon: PaymentIcon, color: '#0288d1', bg: '#e1f5fe' },
  'CDM_ACCOUNT_STATEMENT': { icon: AccountIcon, color: '#5d4037', bg: '#efebe9' },
  'CDM_TRANSACTION': { icon: PaymentIcon, color: '#5d4037', bg: '#efebe9' },
  // Normalized identifier tables (ISO 20022 CDM enhancements)
  'CDM_PARTY_IDENTIFIER': { icon: PersonIcon, color: '#9c27b0', bg: '#f3e5f5' },
  'CDM_ACCOUNT_IDENTIFIER': { icon: AccountIcon, color: '#00838f', bg: '#e0f7fa' },
  'CDM_FI_IDENTIFIER': { icon: BankIcon, color: '#ef6c00', bg: '#fff3e0' },
  'CDM_FI_IDENTIFIERS': { icon: BankIcon, color: '#ef6c00', bg: '#fff3e0' },
  'CDM_INSTITUTION_IDENTIFIER': { icon: BankIcon, color: '#ef6c00', bg: '#fff3e0' },
  'CDM_PAYMENT_IDENTIFIER': { icon: PaymentIcon, color: '#1565c0', bg: '#e3f2fd' },
  'CDM_TRANSACTION_IDENTIFIER': { icon: PaymentIcon, color: '#1565c0', bg: '#e3f2fd' },
  'EXTENSION DATA': { icon: ExtensionIcon, color: '#0097a7', bg: '#e0f7fa' },
  'LINEAGE & METADATA': { icon: HistoryIcon, color: '#455a64', bg: '#eceff1' },
};

/**
 * Dynamic Field Mapping Comparison Dialog
 * Shows fields organized by CDM entity structure, dynamically fetched from mapping database
 * Only shows fields applicable to the selected message format
 */
const RecordComparisonDialog: React.FC<{
  open: boolean;
  onClose: () => void;
  layer: LayerType;
  recordId: string;
  messageType: string;
}> = ({ open, onClose, layer, recordId, messageType }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showPopulatedOnly, setShowPopulatedOnly] = useState(false);
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());

  // Fetch record lineage data
  const { data: lineage, isLoading: lineageLoading } = useQuery({
    queryKey: ['recordLineage', layer, recordId],
    queryFn: () => pipelineApi.getRecordLineage(layer, recordId),
    enabled: open && !!recordId,
  });

  // Fetch field mappings for this message type
  const { data: mappings, isLoading: mappingsLoading } = useQuery({
    queryKey: ['mappingsDoc', messageType],
    queryFn: () => mappingsApi.getDocumentation(messageType, { mapped_only: true }),
    enabled: open && !!messageType,
  });

  const isLoading = lineageLoading || mappingsLoading;

  // Format value for display
  const fmt = (val: any): string => {
    if (val === null || val === undefined) return '';
    if (typeof val === 'object') return JSON.stringify(val, null, 2);
    if (typeof val === 'boolean') return val ? 'Yes' : 'No';
    return String(val);
  };

  // Get value from nested object using path
  const getNestedValue = (obj: any, path: string): any => {
    if (!obj || !path) return undefined;
    // Handle paths like "CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt"
    const parts = path.split('/');
    let value = obj;
    for (const part of parts) {
      if (value === null || value === undefined) return undefined;
      // Try exact key first, then camelCase conversion
      if (value[part] !== undefined) {
        value = value[part];
      } else {
        // Try converting XML path to camelCase (e.g., InstdAmt -> instdAmt)
        const camelKey = part.charAt(0).toLowerCase() + part.slice(1);
        value = value[camelKey];
      }
    }
    return value;
  };

  // Build comparison data dynamically from mappings
  const comparisonData = useMemo(() => {
    if (!lineage || !mappings) return [];

    const bronze = lineage.bronze || {};
    const bronzeParsed = (lineage as any).bronze_parsed || {};
    const silver = lineage.silver || {};
    const gold = lineage.gold || {};
    const goldEntities = lineage.gold_entities || {};
    const goldExtension = (lineage as any).gold_extension || {};

    // Group mappings by gold_table + entity_role
    const groups: Record<string, {
      category: string;
      goldTable: string;
      entityRole: string | null;
      rows: {
        standardField: string;
        standardPath: string;
        silverColumn: string;
        goldColumn: string;
        bronzeValue: string;
        silverValue: string;
        goldValue: string;
      }[];
    }> = {};

    // Process each mapping
    mappings.forEach(mapping => {
      const goldTable = mapping.gold_table?.replace('gold.', '') || 'unmapped';
      const entityRole = mapping.gold_entity_role;
      const categoryKey = entityRole ? `${goldTable} (${entityRole})` : goldTable;

      if (!groups[categoryKey]) {
        groups[categoryKey] = {
          category: categoryKey,
          goldTable,
          entityRole,
          rows: []
        };
      }

      // Get bronze value from parsed data using standard field path
      const bronzePath = mapping.standard_field_path || '';
      let bronzeValue = '';
      if (bronzePath) {
        // Try to get from bronze_parsed first
        const lastPart = bronzePath.split('/').pop() || '';
        const camelKey = lastPart.charAt(0).toLowerCase() + lastPart.slice(1);
        bronzeValue = fmt(bronzeParsed[camelKey] || bronzeParsed[lastPart] || getNestedValue(bronzeParsed, bronzePath));
      }

      // Get silver value
      const silverColumn = mapping.silver_column || '';
      const silverValue = fmt(silver[silverColumn]);

      // Get gold value - need to determine which object to get it from based on gold_table
      const goldColumn = mapping.gold_column || '';
      let goldValue = '';

      if (goldTable === 'cdm_payment_instruction') {
        goldValue = fmt(gold[goldColumn]);
      } else if (goldTable === 'cdm_party') {
        // Map entity roles to gold_entities keys
        const partyKey = {
          'DEBTOR': 'debtor_party',
          'CREDITOR': 'creditor_party',
          'ULTIMATE_DEBTOR': 'ultimate_debtor',
          'ULTIMATE_CREDITOR': 'ultimate_creditor',
          'INITIATING_PARTY': 'initiating_party'
        }[entityRole || ''] || '';
        const party = goldEntities[partyKey] || {};
        goldValue = fmt(party[goldColumn]);
      } else if (goldTable === 'cdm_account') {
        const accountKey = {
          'DEBTOR': 'debtor_account',
          'CREDITOR': 'creditor_account'
        }[entityRole || ''] || '';
        const account = goldEntities[accountKey] || {};
        goldValue = fmt(account[goldColumn]);
      } else if (goldTable === 'cdm_financial_institution') {
        const fiKey = {
          'DEBTOR_AGENT': 'debtor_agent',
          'CREDITOR_AGENT': 'creditor_agent',
          'INTERMEDIARY_AGENT1': 'intermediary_agent1',
          'INTERMEDIARY_AGENT2': 'intermediary_agent2',
          'INSTRUCTING_AGENT': 'instructing_agent',
          'INSTRUCTED_AGENT': 'instructed_agent'
        }[entityRole || ''] || '';
        const fi = goldEntities[fiKey] || {};
        goldValue = fmt(fi[goldColumn]);
      } else if (goldTable.startsWith('cdm_payment_extension')) {
        goldValue = fmt(goldExtension[goldColumn]);
      } else if (goldTable === 'cdm_payment_status') {
        // Payment status entity
        const status = goldEntities['payment_status'] || {};
        goldValue = fmt(status[goldColumn]);
      } else if (goldTable === 'cdm_fx_rate') {
        // FX rate entity
        const fxRate = goldEntities['fx_rate'] || {};
        goldValue = fmt(fxRate[goldColumn]);
      } else if (goldTable === 'cdm_account_statement') {
        // Account statement entity (for camt.053, MT940)
        const statement = goldEntities['account_statement'] || gold;
        goldValue = fmt(statement[goldColumn]);
      } else if (goldTable === 'cdm_transaction') {
        // Transaction entity (for statements)
        const transactions = goldEntities['transactions'] || [];
        if (Array.isArray(transactions) && transactions.length > 0) {
          goldValue = fmt(transactions[0][goldColumn]);
        }
      }
      // Normalized identifier tables (ISO 20022 CDM enhancements)
      else if (goldTable === 'cdm_party_identifier') {
        const partyIdKey = {
          'DEBTOR': 'debtor_party_identifiers',
          'CREDITOR': 'creditor_party_identifiers',
          'ULTIMATE_DEBTOR': 'ultimate_debtor_identifiers',
          'ULTIMATE_CREDITOR': 'ultimate_creditor_identifiers',
          'INITIATING_PARTY': 'initiating_party_identifiers'
        }[entityRole || ''] || 'party_identifiers';
        const identifiers = goldEntities[partyIdKey] || [];
        if (Array.isArray(identifiers) && identifiers.length > 0) {
          // Find matching identifier by type or return first
          const idType = goldColumn.replace('identifier_', '').toUpperCase();
          const match = identifiers.find((id: any) => id.identifier_type === idType) || identifiers[0];
          goldValue = fmt(match?.[goldColumn] || match?.identifier_value);
        }
      } else if (goldTable === 'cdm_account_identifier') {
        // Account identifiers are linked via account_id FK - get all identifiers
        // entity_role in mapping (e.g., DEBTOR_IBAN) indicates which identifier record to create
        const toArray = (v: any) => Array.isArray(v) ? v : [];
        const allIdentifiers = [
          ...toArray(goldEntities['debtor_account_identifiers']),
          ...toArray(goldEntities['creditor_account_identifiers']),
          ...toArray(goldEntities['account_identifiers'])
        ];
        if (allIdentifiers.length > 0) {
          // If entity_role contains identifier type suffix, try to match it
          const idTypeSuffix = entityRole?.includes('_') ? entityRole.split('_').slice(1).join('_') : '';
          const match = idTypeSuffix
            ? allIdentifiers.find((id: any) => id.identifier_type === idTypeSuffix)
            : allIdentifiers[0];
          goldValue = fmt(match?.[goldColumn] || match?.identifier_value);
        }
      } else if (goldTable === 'cdm_fi_identifier' || goldTable === 'cdm_fi_identifiers' || goldTable === 'cdm_institution_identifier') {
        // Institution identifiers are linked via financial_institution_id FK - get all identifiers
        // entity_role in mapping (e.g., DEBTOR_AGENT_BIC) indicates which identifier record to create
        const toArray = (v: any) => Array.isArray(v) ? v : [];
        const allIdentifiers = [
          ...toArray(goldEntities['debtor_agent_identifiers']),
          ...toArray(goldEntities['creditor_agent_identifiers']),
          ...toArray(goldEntities['intermediary1_identifiers']),
          ...toArray(goldEntities['intermediary2_identifiers']),
          ...toArray(goldEntities['fi_identifiers'])
        ];
        if (allIdentifiers.length > 0) {
          // If entity_role contains identifier type suffix (BIC, CLR, LEI), try to match it
          const parts = entityRole?.split('_') || [];
          const idTypeSuffix = parts.length > 2 ? parts.slice(2).join('_') : '';
          const match = idTypeSuffix
            ? allIdentifiers.find((id: any) => id.identifier_type === idTypeSuffix)
            : allIdentifiers[0];
          goldValue = fmt(match?.[goldColumn] || match?.identifier_value);
        }
      } else if (goldTable === 'cdm_payment_identifier' || goldTable === 'cdm_transaction_identifier') {
        const paymentIdentifiers = goldEntities['payment_identifiers'] || [];
        if (Array.isArray(paymentIdentifiers) && paymentIdentifiers.length > 0) {
          const idType = goldColumn.replace('identifier_', '').toUpperCase();
          const match = paymentIdentifiers.find((id: any) => id.identifier_type === idType) || paymentIdentifiers[0];
          goldValue = fmt(match?.[goldColumn] || match?.identifier_value);
        }
      }

      groups[categoryKey].rows.push({
        standardField: mapping.standard_field_name || silverColumn || goldColumn,
        standardPath: bronzePath,
        silverColumn,
        goldColumn,
        bronzeValue,
        silverValue,
        goldValue
      });
    });

    // Add lineage/metadata section
    groups['LINEAGE & METADATA'] = {
      category: 'LINEAGE & METADATA',
      goldTable: 'metadata',
      entityRole: null,
      rows: [
        { standardField: 'raw_id', standardPath: '', silverColumn: 'raw_id', goldColumn: 'source_raw_id', bronzeValue: fmt(bronze.raw_id), silverValue: fmt(silver.raw_id), goldValue: fmt(gold.source_raw_id) },
        { standardField: 'stg_id', standardPath: '', silverColumn: 'stg_id', goldColumn: 'source_stg_id', bronzeValue: '', silverValue: fmt(silver.stg_id), goldValue: fmt(gold.source_stg_id) },
        { standardField: 'batch_id', standardPath: '', silverColumn: '_batch_id', goldColumn: 'lineage_batch_id', bronzeValue: fmt(bronze._batch_id), silverValue: fmt(silver._batch_id), goldValue: fmt(gold.lineage_batch_id) },
        { standardField: 'message_type', standardPath: '', silverColumn: 'message_type', goldColumn: 'source_message_type', bronzeValue: fmt(bronze.message_type), silverValue: fmt(silver.message_type), goldValue: fmt(gold.source_message_type) },
        { standardField: 'processing_status', standardPath: '', silverColumn: 'processing_status', goldColumn: 'current_status', bronzeValue: fmt(bronze.processing_status), silverValue: fmt(silver.processing_status), goldValue: fmt(gold.current_status) },
        { standardField: '_ingested_at', standardPath: '', silverColumn: '', goldColumn: '', bronzeValue: fmt(bronze._ingested_at), silverValue: '', goldValue: '' },
        { standardField: '_processed_at', standardPath: '', silverColumn: '_processed_at', goldColumn: '', bronzeValue: '', silverValue: fmt(silver._processed_at), goldValue: '' },
        { standardField: 'created_at', standardPath: '', silverColumn: '', goldColumn: 'created_at', bronzeValue: '', silverValue: '', goldValue: fmt(gold.created_at) },
      ]
    };

    // Sort groups by CDM entity order:
    // 1. CDM base tables first (cdm_pacs_*, cdm_pain_*, cdm_camt_*, cdm_payment_instruction)
    // 2. cdm_party then cdm_party_identifier
    // 3. cdm_financial_institution then cdm_institution_identifier
    // 4. cdm_account then cdm_account_identifier
    // 5. Extension tables
    // 6. Lineage & Metadata last
    const getGroupOrder = (category: string): number => {
      const cat = category.toLowerCase();

      // Base/Payment tables first
      if (cat.includes('cdm_pacs_')) return 1;
      if (cat.includes('cdm_pain_')) return 2;
      if (cat.includes('cdm_camt_')) return 3;
      if (cat.includes('cdm_payment_instruction')) return 10;
      if (cat.includes('cdm_payment_status')) return 11;
      if (cat.includes('cdm_fx_rate')) return 12;

      // Party entities
      if (cat.includes('cdm_party') && !cat.includes('identifier')) {
        if (cat.includes('debtor')) return 20;
        if (cat.includes('creditor')) return 21;
        if (cat.includes('initiating')) return 22;
        if (cat.includes('ultimate')) return 23;
        return 25;
      }
      if (cat.includes('cdm_party_identifier') || cat.includes('party_identifier')) return 29;

      // Financial Institution entities
      if (cat.includes('cdm_financial_institution') || cat.includes('financial_institution')) {
        if (cat.includes('debtor')) return 30;
        if (cat.includes('creditor')) return 31;
        if (cat.includes('intermediary') || cat.includes('instructing') || cat.includes('instructed')) return 32;
        return 35;
      }
      if (cat.includes('cdm_institution_identifier') || cat.includes('fi_identifier')) return 39;

      // Account entities
      if (cat.includes('cdm_account') && !cat.includes('identifier') && !cat.includes('statement')) {
        if (cat.includes('debtor')) return 40;
        if (cat.includes('creditor')) return 41;
        return 45;
      }
      if (cat.includes('cdm_account_identifier') || cat.includes('account_identifier')) return 49;

      // Statement/Transaction entities
      if (cat.includes('cdm_account_statement')) return 50;
      if (cat.includes('cdm_transaction')) return 51;
      if (cat.includes('transaction_identifier') || cat.includes('payment_identifier')) return 52;

      // Extension tables
      if (cat.includes('extension')) return 60;

      // Lineage & Metadata last
      if (cat.includes('lineage') || cat.includes('metadata')) return 100;

      return 80; // Unknown tables before lineage
    };

    const sortedGroups = Object.values(groups).sort((a, b) => {
      const aOrder = getGroupOrder(a.category);
      const bOrder = getGroupOrder(b.category);
      if (aOrder !== bOrder) return aOrder - bOrder;
      // If same order, sort alphabetically
      return a.category.localeCompare(b.category);
    });

    return sortedGroups;
  }, [lineage, mappings]);

  // Filter to show only populated rows if toggle is on
  const filteredData = useMemo(() => {
    if (!showPopulatedOnly) return comparisonData;
    return comparisonData.map(group => ({
      ...group,
      rows: group.rows.filter(row => row.bronzeValue || row.silverValue || row.goldValue)
    })).filter(group => group.rows.length > 0);
  }, [comparisonData, showPopulatedOnly]);

  // Count stats
  const stats = useMemo(() => {
    let bronze = 0, silver = 0, gold = 0, total = 0;
    comparisonData.forEach(group => {
      group.rows.forEach(row => {
        total++;
        if (row.bronzeValue) bronze++;
        if (row.silverValue) silver++;
        if (row.goldValue) gold++;
      });
    });
    return { bronze, silver, gold, total };
  }, [comparisonData]);

  // Get icon and color for category
  const getCategoryStyle = (category: string) => {
    const cat = category.toLowerCase();

    // CDM base/payment tables (ISO 20022 aligned)
    if (cat.includes('cdm_pacs_')) return { icon: PaymentIcon, color: '#fbc02d', bg: '#fffde7' }; // Gold for base tables
    if (cat.includes('cdm_pain_')) return { icon: PaymentIcon, color: '#fbc02d', bg: '#fffde7' };
    if (cat.includes('cdm_camt_')) return { icon: PaymentIcon, color: '#fbc02d', bg: '#fffde7' };

    // Normalized identifier tables (ISO 20022 CDM enhancements)
    if (cat.includes('party_identifier')) return { icon: PersonIcon, color: '#9c27b0', bg: '#f3e5f5' };
    if (cat.includes('account_identifier')) return { icon: AccountIcon, color: '#00838f', bg: '#e0f7fa' };
    if (cat.includes('fi_identifier') || cat.includes('institution_identifier')) return { icon: BankIcon, color: '#ef6c00', bg: '#fff3e0' };
    if (cat.includes('payment_identifier') || cat.includes('transaction_identifier')) return { icon: PaymentIcon, color: '#1565c0', bg: '#e3f2fd' };

    // Core CDM entities
    if (cat.includes('payment_instruction')) return { icon: PaymentIcon, color: '#1976d2', bg: '#e3f2fd' };
    if (cat.includes('payment_status')) return { icon: PaymentIcon, color: '#f57c00', bg: '#fff3e0' };
    if (cat.includes('fx_rate')) return { icon: PaymentIcon, color: '#0288d1', bg: '#e1f5fe' };
    if (cat.includes('account_statement')) return { icon: AccountIcon, color: '#5d4037', bg: '#efebe9' };
    if (cat.includes('transaction')) return { icon: PaymentIcon, color: '#5d4037', bg: '#efebe9' };
    if (cat.includes('party')) {
      if (cat.includes('debtor')) return { icon: PersonIcon, color: '#7b1fa2', bg: '#f3e5f5' };
      if (cat.includes('creditor')) return { icon: PersonIcon, color: '#388e3c', bg: '#e8f5e9' };
      return { icon: PersonIcon, color: '#5d4037', bg: '#efebe9' };
    }
    if (cat.includes('account')) {
      if (cat.includes('debtor')) return { icon: AccountIcon, color: '#7b1fa2', bg: '#f3e5f5' };
      return { icon: AccountIcon, color: '#388e3c', bg: '#e8f5e9' };
    }
    if (cat.includes('financial_institution')) {
      if (cat.includes('debtor')) return { icon: BankIcon, color: '#7b1fa2', bg: '#f3e5f5' };
      if (cat.includes('creditor')) return { icon: BankIcon, color: '#388e3c', bg: '#e8f5e9' };
      return { icon: BankIcon, color: '#ff8f00', bg: '#fff3e0' };
    }
    if (cat.includes('extension')) return { icon: ExtensionIcon, color: '#0097a7', bg: '#e0f7fa' };
    if (cat.includes('lineage')) return { icon: HistoryIcon, color: '#455a64', bg: '#eceff1' };
    return { icon: PaymentIcon, color: '#666', bg: '#f5f5f5' };
  };

  // Toggle group collapse
  const toggleGroup = useCallback((category: string) => {
    setCollapsedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  }, []);

  // Collapse/Expand all groups
  const collapseAll = useCallback(() => {
    const allCategories = filteredData.map(g => g.category);
    setCollapsedGroups(new Set(allCategories));
  }, [filteredData]);

  const expandAll = useCallback(() => {
    setCollapsedGroups(new Set());
  }, []);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth PaperProps={{ sx: { height: '90vh' } }}>
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CompareIcon />
            <Typography variant="h6" fontWeight={600}>
              Field Mapping Comparison
            </Typography>
            <Chip label={messageType} size="small" color="primary" variant="outlined" />
            <Chip label={`${stats.total} mapped fields`} size="small" variant="outlined" />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip label={`Bronze: ${stats.bronze}`} size="small" sx={{ backgroundColor: zoneColors.bronze.bg }} />
            <Chip label={`Silver: ${stats.silver}`} size="small" sx={{ backgroundColor: zoneColors.silver.bg }} />
            <Chip label={`Gold: ${stats.gold}`} size="small" sx={{ backgroundColor: zoneColors.gold.bg }} />
            <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ px: 2, py: 1, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label={`Field Mappings (${filteredData.length} groups)`} />
            <Tab label="Raw JSON" />
          </Tabs>
          <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">Show populated only:</Typography>
              <ToggleButton
                value="check"
                selected={showPopulatedOnly}
                onChange={() => setShowPopulatedOnly(!showPopulatedOnly)}
                size="small"
                sx={{ px: 1, py: 0.25 }}
              >
                {showPopulatedOnly ? 'ON' : 'OFF'}
              </ToggleButton>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Tooltip title="Collapse all groups">
                <IconButton size="small" onClick={collapseAll}>
                  <UnfoldLessIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Expand all groups">
                <IconButton size="small" onClick={expandAll}>
                  <UnfoldMoreIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Box>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
        ) : activeTab === 0 ? (
          <Box sx={{ height: 'calc(90vh - 160px)', overflow: 'auto' }}>
            <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <Box component="thead" sx={{ position: 'sticky', top: 0, zIndex: 10 }}>
                <Box component="tr">
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: '#f5f5f5', borderBottom: '2px solid #ccc', width: '18%' }}>
                    Standard Field
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: '#f5f5f5', borderBottom: '2px solid #ccc', width: '12%' }}>
                    Silver Column
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: '#f5f5f5', borderBottom: '2px solid #ccc', width: '12%' }}>
                    Gold Column
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: zoneColors.bronze.bg, borderBottom: `2px solid ${zoneColors.bronze.border}`, width: '18%' }}>
                    Bronze Value
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: zoneColors.silver.bg, borderBottom: `2px solid ${zoneColors.silver.border}`, width: '20%' }}>
                    Silver Value
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: zoneColors.gold.bg, borderBottom: `2px solid ${zoneColors.gold.border}`, width: '20%' }}>
                    Gold Value
                  </Box>
                </Box>
              </Box>
              <Box component="tbody">
                {filteredData.map((group, gIdx) => {
                  const style = getCategoryStyle(group.category);
                  const IconComponent = style.icon;
                  const populatedCount = group.rows.filter(r => r.bronzeValue || r.silverValue || r.goldValue).length;

                  return (
                    <React.Fragment key={gIdx}>
                      {/* Entity Category Header - Clickable to toggle collapse */}
                      <Box component="tr">
                        <Box
                          component="td"
                          colSpan={6}
                          onClick={() => toggleGroup(group.category)}
                          sx={{
                            p: 1, py: 0.75, fontWeight: 700, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5,
                            backgroundColor: style.bg, color: style.color, borderTop: gIdx > 0 ? `2px solid ${style.color}40` : 'none',
                            cursor: 'pointer', userSelect: 'none',
                            '&:hover': { filter: 'brightness(0.95)' },
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {collapsedGroups.has(group.category) ? (
                              <ExpandMoreIcon sx={{ fontSize: 18 }} />
                            ) : (
                              <ExpandLessIcon sx={{ fontSize: 18 }} />
                            )}
                            <IconComponent sx={{ fontSize: 16 }} />
                            {group.category}
                            <Chip label={`${populatedCount}/${group.rows.length}`} size="small" sx={{ ml: 1, height: 18, fontSize: 10, backgroundColor: 'white' }} />
                          </Box>
                        </Box>
                      </Box>
                      {/* Data Rows - Collapsible */}
                      {!collapsedGroups.has(group.category) && group.rows.map((row, rIdx) => {
                        const hasAnyData = row.bronzeValue || row.silverValue || row.goldValue;
                        const bronzeHasData = row.bronzeValue;
                        const silverMissing = !!(bronzeHasData && !row.silverValue);

                        return (
                          <Box component="tr" key={rIdx} sx={{
                            '&:hover': { backgroundColor: '#f5f5f5' },
                            backgroundColor: silverMissing ? '#ffebee' : 'transparent',
                            opacity: hasAnyData ? 1 : 0.5,
                          }}>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontWeight: 500,
                              fontFamily: 'monospace', fontSize: 11
                            }}>
                              {row.standardField}
                              {silverMissing && <Tooltip title="Data in Bronze but missing in Silver"><ErrorIcon sx={{ fontSize: 12, color: 'error.main', ml: 0.5 }} /></Tooltip>}
                            </Box>
                            <Box component="td" sx={{ p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10, color: 'text.secondary' }}>
                              {row.silverColumn || '-'}
                            </Box>
                            <Box component="td" sx={{ p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10, color: 'text.secondary' }}>
                              {row.goldColumn || '-'}
                            </Box>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10,
                              backgroundColor: row.bronzeValue ? zoneColors.bronze.bg + '80' : 'transparent',
                              wordBreak: 'break-word', maxWidth: 180
                            }}>
                              {row.bronzeValue || '-'}
                            </Box>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10,
                              backgroundColor: row.silverValue ? zoneColors.silver.bg + '80' : silverMissing ? '#ffcdd2' : 'transparent',
                              wordBreak: 'break-word', maxWidth: 200
                            }}>
                              {row.silverValue || (silverMissing ? '⚠️ MISSING' : '-')}
                            </Box>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10,
                              backgroundColor: row.goldValue ? zoneColors.gold.bg + '80' : 'transparent',
                              wordBreak: 'break-word', maxWidth: 200
                            }}>
                              {row.goldValue || '-'}
                            </Box>
                          </Box>
                        );
                      })}
                    </React.Fragment>
                  );
                })}
              </Box>
            </Box>
          </Box>
        ) : (
          <Box sx={{ p: 2, height: 'calc(90vh - 160px)', overflow: 'auto' }}>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Bronze (raw_content)</Typography>
            <Paper sx={{ p: 1, mb: 2, backgroundColor: zoneColors.bronze.bg, maxHeight: 200, overflow: 'auto' }}>
              <pre style={{ fontSize: 10, margin: 0, whiteSpace: 'pre-wrap' }}>
                {lineage?.bronze?.raw_content ? (typeof lineage.bronze.raw_content === 'string' ? (() => { try { return JSON.stringify(JSON.parse(lineage.bronze.raw_content), null, 2); } catch { return lineage.bronze.raw_content; } })() : JSON.stringify(lineage.bronze.raw_content, null, 2)) : 'N/A'}
              </pre>
            </Paper>

            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Bronze Parsed (extractor output)</Typography>
            <Paper sx={{ p: 1, mb: 2, backgroundColor: '#e8f5e9', maxHeight: 200, overflow: 'auto' }}>
              <pre style={{ fontSize: 10, margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify((lineage as any)?.bronze_parsed || {}, null, 2)}</pre>
            </Paper>

            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Silver (stg_* record)</Typography>
            <Paper sx={{ p: 1, mb: 2, backgroundColor: zoneColors.silver.bg, maxHeight: 200, overflow: 'auto' }}>
              <pre style={{ fontSize: 10, margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(lineage?.silver || {}, null, 2)}</pre>
            </Paper>

            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Gold (cdm_payment_instruction)</Typography>
            <Paper sx={{ p: 1, mb: 2, backgroundColor: zoneColors.gold.bg, maxHeight: 200, overflow: 'auto' }}>
              <pre style={{ fontSize: 10, margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(lineage?.gold || {}, null, 2)}</pre>
            </Paper>

            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Gold Entities</Typography>
            <Paper sx={{ p: 1, mb: 2, backgroundColor: zoneColors.gold.bg, maxHeight: 200, overflow: 'auto' }}>
              <pre style={{ fontSize: 10, margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(lineage?.gold_entities || {}, null, 2)}</pre>
            </Paper>

            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Gold Extension</Typography>
            <Paper sx={{ p: 1, backgroundColor: '#e0f7fa', maxHeight: 200, overflow: 'auto' }}>
              <pre style={{ fontSize: 10, margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify((lineage as any)?.gold_extension || {}, null, 2)}</pre>
            </Paper>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

// Edit Record Dialog
const EditRecordDialog: React.FC<{
  open: boolean;
  onClose: () => void;
  layer: LayerType;
  recordId: string;
  onSuccess: () => void;
}> = ({ open, onClose, layer, recordId, onSuccess }) => {
  const [editedContent, setEditedContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: recordData, isLoading } = useQuery({
    queryKey: ['recordDetail', layer, recordId],
    queryFn: () => pipelineApi.getRecordDetails(layer, recordId),
    enabled: open && !!recordId,
  });

  React.useEffect(() => {
    if (recordData?.raw_content) {
      setEditedContent(typeof recordData.raw_content === 'string' ? recordData.raw_content : JSON.stringify(recordData.raw_content, null, 2));
    }
  }, [recordData]);

  const reprocessMutation = useMutation({
    mutationFn: async () => {
      const parsedContent = JSON.parse(editedContent);
      return reprocessApi.updateRecord(layer, layer === 'bronze' ? 'raw_payment_messages' : layer === 'silver' ? 'stg_payment' : 'cdm_payment_instruction', recordId, { raw_content: parsedContent }, true);
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['batchRecords'] }); queryClient.invalidateQueries({ queryKey: ['recordLineage'] }); onSuccess(); onClose(); },
    onError: (err: any) => { setError(err.message || 'Failed to reprocess record'); },
  });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}><EditIcon /><Typography variant="h6" fontWeight={600}>Edit & Reprocess</Typography></Box>
          <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        {isLoading ? <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress /></Box> : (
          <Box sx={{ mt: 1 }}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <TextField fullWidth multiline rows={15} value={editedContent} onChange={(e) => setEditedContent(e.target.value)} sx={{ '& .MuiInputBase-input': { fontFamily: 'monospace', fontSize: 12 } }} />
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" startIcon={<ReplayIcon />} onClick={() => { setError(null); try { JSON.parse(editedContent); reprocessMutation.mutate(); } catch { setError('Invalid JSON'); } }} disabled={reprocessMutation.isPending || isLoading}>
          {reprocessMutation.isPending ? 'Reprocessing...' : 'Reprocess'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const BatchRecordsTab: React.FC<BatchRecordsTabProps> = ({ batchId, messageType }) => {
  const queryClient = useQueryClient();
  const [selectedLayer, setSelectedLayer] = useState<LayerType>('bronze');
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({ page: 0, pageSize: 25 });
  const [selectedRecord, setSelectedRecord] = useState<{ layer: LayerType; id: string } | null>(null);
  const [editRecord, setEditRecord] = useState<{ layer: LayerType; id: string } | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['batchRecords', batchId, selectedLayer, paginationModel],
    queryFn: async () => {
      const records = await pipelineApi.getBatchRecords(batchId, selectedLayer, paginationModel.pageSize, paginationModel.page * paginationModel.pageSize);
      return { items: records, total: records.length };
    },
    enabled: !!batchId,
  });

  const columns: GridColDef[] = useMemo(() => {
    const cols: GridColDef[] = [{
      field: 'actions', headerName: 'Actions', width: 100, sortable: false,
      renderCell: (params: GridRenderCellParams) => {
        const id = selectedLayer === 'bronze' ? params.row.raw_id : selectedLayer === 'silver' ? params.row.stg_id : params.row.instruction_id;
        return (
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="Compare All Zones"><IconButton size="small" onClick={() => setSelectedRecord({ layer: selectedLayer, id })} color="primary"><CompareIcon fontSize="small" /></IconButton></Tooltip>
            <Tooltip title="Edit"><IconButton size="small" onClick={() => setEditRecord({ layer: selectedLayer, id })}><EditIcon fontSize="small" /></IconButton></Tooltip>
          </Box>
        );
      },
    }];

    if (selectedLayer === 'bronze') {
      cols.push(
        { field: 'raw_id', headerName: 'Raw ID', width: 130, renderCell: (p) => <Tooltip title={p.value}><span style={{ fontFamily: 'monospace', fontSize: 11 }}>{p.value?.substring(0, 14)}...</span></Tooltip> },
        { field: 'message_type', headerName: 'Type', width: 100 },
        { field: 'message_format', headerName: 'Format', width: 90 },
        { field: 'source_system', headerName: 'Source', width: 80 },
        { field: 'processing_status', headerName: 'Status', width: 140, renderCell: (p) => <Chip label={p.value} size="small" color={statusColors[p.value] || 'default'} sx={{ fontSize: 10 }} /> },
        { field: '_ingested_at', headerName: 'Ingested', width: 150, valueFormatter: (v: string) => v ? new Date(v).toLocaleString() : '-' }
      );
    } else if (selectedLayer === 'silver') {
      cols.push(
        { field: 'stg_id', headerName: 'Stg ID', width: 120, renderCell: (p) => <Tooltip title={p.value}><span style={{ fontFamily: 'monospace', fontSize: 11 }}>{p.value?.substring(0, 10)}...</span></Tooltip> },
        { field: 'message_id', headerName: 'Msg ID', width: 100 },
        { field: 'amount', headerName: 'Amount', width: 100, type: 'number', valueFormatter: (v: number) => v ? v.toLocaleString() : '-' },
        { field: 'currency', headerName: 'Ccy', width: 50 },
        { field: 'debtor_name', headerName: 'Debtor', width: 140 },
        { field: 'creditor_name', headerName: 'Creditor', width: 140 },
        { field: 'processing_status', headerName: 'Status', width: 140, renderCell: (p) => <Chip label={p.value || 'N/A'} size="small" color={statusColors[p.value] || 'default'} sx={{ fontSize: 10 }} /> }
      );
    } else {
      cols.push(
        { field: 'instruction_id', headerName: 'Instr ID', width: 130, renderCell: (p) => <Tooltip title={p.value}><span style={{ fontFamily: 'monospace', fontSize: 11 }}>{p.value?.substring(0, 14)}...</span></Tooltip> },
        { field: 'payment_id', headerName: 'Payment ID', width: 120 },
        { field: 'payment_type', headerName: 'Type', width: 90 },
        { field: 'instructed_amount', headerName: 'Amount', width: 100, type: 'number', valueFormatter: (v: number) => v ? v.toLocaleString() : '-' },
        { field: 'instructed_currency', headerName: 'Ccy', width: 50 },
        { field: 'source_message_type', headerName: 'Src Type', width: 90 },
        { field: 'current_status', headerName: 'Status', width: 100, renderCell: (p) => <Chip label={p.value || 'N/A'} size="small" color={statusColors[p.value] || 'default'} sx={{ fontSize: 10 }} /> },
        { field: 'created_at', headerName: 'Created', width: 150, valueFormatter: (v: string) => v ? new Date(v).toLocaleString() : '-' }
      );
    }
    return cols;
  }, [selectedLayer]);

  const getRowId = (row: Record<string, unknown>) => selectedLayer === 'bronze' ? row.raw_id as string : selectedLayer === 'silver' ? row.stg_id as string : row.instruction_id as string;

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="body2" color="text.secondary">Layer:</Typography>
        <ToggleButtonGroup value={selectedLayer} exclusive onChange={(_, v) => v && (setSelectedLayer(v), setPaginationModel({ ...paginationModel, page: 0 }))} size="small">
          <ToggleButton value="bronze" sx={{ '&.Mui-selected': { backgroundColor: zoneColors.bronze.bg, color: zoneColors.bronze.text } }}>Bronze</ToggleButton>
          <ToggleButton value="silver" sx={{ '&.Mui-selected': { backgroundColor: zoneColors.silver.bg, color: zoneColors.silver.text } }}>Silver</ToggleButton>
          <ToggleButton value="gold" sx={{ '&.Mui-selected': { backgroundColor: zoneColors.gold.bg, color: zoneColors.gold.text } }}>Gold</ToggleButton>
        </ToggleButtonGroup>
        <Chip label={messageType} size="small" sx={{ ml: 'auto' }} />
      </Box>

      {isLoading ? <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}><CircularProgress /></Box> : (
        <DataGrid rows={data?.items || []} columns={columns} getRowId={getRowId} paginationModel={paginationModel} onPaginationModelChange={setPaginationModel} pageSizeOptions={[10, 25, 50]} rowCount={data?.total || 0} paginationMode="client" disableRowSelectionOnClick autoHeight sx={{ border: 'none', '& .MuiDataGrid-columnHeaders': { backgroundColor: '#f5f5f5' } }} />
      )}

      {selectedRecord && <RecordComparisonDialog open onClose={() => setSelectedRecord(null)} layer={selectedRecord.layer} recordId={selectedRecord.id} messageType={messageType} />}
      {editRecord && <EditRecordDialog open onClose={() => setEditRecord(null)} layer={editRecord.layer} recordId={editRecord.id} onSuccess={() => { setSnackbar({ open: true, message: 'Reprocessed successfully', severity: 'success' }); refetch(); }} />}
      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({ ...snackbar, open: false })} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default BatchRecordsTab;
