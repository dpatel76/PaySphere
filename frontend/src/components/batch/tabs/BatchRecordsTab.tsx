/**
 * Batch Records Tab
 * Displays paginated records for a batch with layer selector and cross-zone comparison
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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Paper,
  Divider,
  TextField,
  Button,
  Alert,
  Snackbar,
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
  Visibility as ViewIcon,
  ArrowForward as ArrowIcon,
  Edit as EditIcon,
  Replay as ReplayIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelineApi, reprocessApi } from '../../../api/client';
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

// Zone colors for visual distinction
const zoneColors = {
  bronze: { bg: colors.zones.bronze.light, border: colors.zones.bronze.main, text: colors.zones.bronze.dark },
  silver: { bg: colors.zones.silver.light, border: colors.zones.silver.main, text: colors.zones.silver.dark },
  gold: { bg: colors.zones.gold.light, border: colors.zones.gold.main, text: colors.zones.gold.dark },
};

// Field Display Component for showing key-value pairs
const FieldDisplay: React.FC<{ label: string; value: any; isHighlighted?: boolean }> = ({
  label,
  value,
  isHighlighted = false,
}) => {
  const displayValue = value === null || value === undefined
    ? '-'
    : typeof value === 'object'
    ? JSON.stringify(value, null, 2)
    : String(value);

  return (
    <Box sx={{ mb: 1.5 }}>
      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
        {label}
      </Typography>
      <Typography
        variant="body2"
        sx={{
          fontFamily: label.includes('id') || label.includes('content') ? 'monospace' : 'inherit',
          fontSize: label.includes('content') ? 11 : 13,
          backgroundColor: isHighlighted ? colors.primary.light + '20' : 'transparent',
          p: isHighlighted ? 0.5 : 0,
          borderRadius: 1,
          wordBreak: 'break-all',
          whiteSpace: label.includes('content') ? 'pre-wrap' : 'normal',
          maxHeight: label.includes('content') ? 200 : 'auto',
          overflow: 'auto',
        }}
      >
        {displayValue}
      </Typography>
    </Box>
  );
};

// Record Comparison Dialog Component - Table-based side-by-side view
const RecordComparisonDialog: React.FC<{
  open: boolean;
  onClose: () => void;
  layer: LayerType;
  recordId: string;
}> = ({ open, onClose, layer, recordId }) => {
  const [activeTab, setActiveTab] = useState(0);

  const { data: lineage, isLoading } = useQuery({
    queryKey: ['recordLineage', layer, recordId],
    queryFn: () => pipelineApi.getRecordLineage(layer, recordId),
    enabled: open && !!recordId,
  });

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Build unified field comparison table rows - grouped by CDM entity
  // Intelligently extracts values from raw_content and aligns with Silver/Gold fields
  // Uses gold_entities for denormalized party/account/agent data
  const getComparisonRows = () => {
    if (!lineage) return [];

    // Parse raw_content from bronze to show actual source data
    let rawContent: Record<string, any> = {};
    if (lineage.bronze?.raw_content) {
      try {
        rawContent = typeof lineage.bronze.raw_content === 'string'
          ? JSON.parse(lineage.bronze.raw_content)
          : lineage.bronze.raw_content;
      } catch {
        rawContent = {};
      }
    }

    // Gold entities (party, account, agent) from API
    const goldEntities = lineage.gold_entities || {};

    // Helper to get nested value from raw_content (e.g., "debtor.name" or "debtorAccount.iban")
    const getRawValue = (path: string): any => {
      const parts = path.split('.');
      let value: any = rawContent;
      for (const part of parts) {
        if (value === null || value === undefined) return undefined;
        value = value[part];
      }
      return value;
    };

    // Helper to get value from gold entities (e.g., "debtor_party.name")
    const getGoldEntityValue = (path: string): any => {
      const parts = path.split('.');
      if (parts.length !== 2) return undefined;
      const [entity, field] = parts;
      const entityData = goldEntities[entity as keyof typeof goldEntities];
      return entityData?.[field];
    };

    // Helper to format values for display
    const fmt = (val: any): string => {
      if (val === null || val === undefined) return '-';
      if (typeof val === 'object') return JSON.stringify(val);
      if (typeof val === 'boolean') return val ? 'Yes' : 'No';
      return String(val);
    };

    type RowData = {
      field: string;
      rawPath?: string;
      bronze: string;
      silver: string;
      gold: string;
      isHeader?: boolean;
    };

    const rows: RowData[] = [];

    // Helper to add a section header
    const addSection = (title: string) => {
      rows.push({ field: title, bronze: '', silver: '', gold: '', isHeader: true });
    };

    // Helper to add a mapped field row with intelligent extraction
    // goldField can be either a direct field on gold or an entity path like "debtor_party.name"
    const addRow = (
      fieldName: string,
      rawPath: string | null,  // Path in raw_content (e.g., "debtor.name", "instructedAmount")
      silverField: string | null,
      goldField: string | null  // Either direct field or entity.field path
    ) => {
      const rawVal = rawPath ? getRawValue(rawPath) : undefined;
      const silverVal = silverField ? lineage.silver?.[silverField] : undefined;

      // Check if goldField is an entity path (contains .)
      let goldVal: any;
      if (goldField) {
        if (goldField.includes('.')) {
          goldVal = getGoldEntityValue(goldField);
        } else {
          goldVal = lineage.gold?.[goldField];
        }
      }

      // Always show if Gold has a value (100% Gold coverage), or if any zone has data
      if (goldVal !== undefined || silverVal !== undefined || rawVal !== undefined) {
        rows.push({
          field: fieldName,
          rawPath: rawPath || undefined,
          bronze: fmt(rawVal),
          silver: fmt(silverVal),
          gold: fmt(goldVal),
        });
      }
    };

    // =========================================================================
    // SECTION: PAYMENT INSTRUCTION (Core CDM Entity)
    // =========================================================================
    addSection('PAYMENT INSTRUCTION');
    addRow('Instruction ID', 'instructionId', 'instruction_id', 'instruction_id');
    addRow('Payment ID', 'messageId', 'msg_id', 'payment_id');
    addRow('End-to-End ID', 'endToEndId', 'end_to_end_id', 'end_to_end_id');
    addRow('UETR', 'uetr', 'uetr', 'uetr');
    addRow('Transaction ID', null, null, 'transaction_id');
    addRow('Instruction ID (External)', null, null, 'instruction_id_ext');
    addRow('Message ID', 'messageId', 'msg_id', 'message_id');
    addRow('Related Reference', null, null, 'related_reference');
    addRow('Payment Type', null, null, 'payment_type');
    addRow('Scheme Code', 'paymentInformation.localInstrument', 'local_instrument', 'scheme_code');
    addRow('Direction', null, null, 'direction');
    addRow('Cross-Border Flag', null, null, 'cross_border_flag');
    addRow('Priority', null, null, 'priority');
    addRow('Service Level', 'paymentInformation.serviceLevel', 'service_level', 'service_level');
    addRow('Local Instrument', 'paymentInformation.localInstrument', 'local_instrument', 'local_instrument');
    addRow('Category Purpose', 'paymentInformation.categoryPurpose', 'category_purpose', 'category_purpose');

    // =========================================================================
    // SECTION: AMOUNT & CURRENCY
    // =========================================================================
    addSection('AMOUNT & CURRENCY');
    addRow('Instructed Amount', 'instructedAmount', 'instructed_amount', 'instructed_amount');
    addRow('Instructed Currency', 'instructedCurrency', 'instructed_currency', 'instructed_currency');
    addRow('Equivalent Amount', 'equivalentAmount', 'equivalent_amount', null);
    addRow('Equivalent Currency', 'equivalentCurrency', 'equivalent_currency', null);
    addRow('Interbank Settlement Amount', null, null, 'interbank_settlement_amount');
    addRow('Interbank Settlement Currency', null, null, 'interbank_settlement_currency');
    addRow('Exchange Rate', 'exchangeRate', 'exchange_rate', 'exchange_rate');
    addRow('Exchange Rate Type', null, null, 'exchange_rate_type');
    addRow('Charge Bearer', 'chargeBearer', 'charge_bearer', 'charge_bearer');

    // =========================================================================
    // SECTION: DEBTOR (Payer Party) - Gold uses cdm_party table
    // =========================================================================
    addSection('DEBTOR (PAYER)');
    addRow('Debtor ID (FK)', null, null, 'debtor_id');
    addRow('Debtor Party Type', null, null, 'debtor_party.party_type');
    addRow('Debtor Name', 'debtor.name', 'debtor_name', 'debtor_party.name');
    addRow('Debtor Street', 'debtor.streetName', 'debtor_street_name', 'debtor_party.street_name');
    addRow('Debtor Building', 'debtor.buildingNumber', 'debtor_building_number', 'debtor_party.building_number');
    addRow('Debtor Postal Code', 'debtor.postalCode', 'debtor_postal_code', 'debtor_party.post_code');
    addRow('Debtor Town', 'debtor.townName', 'debtor_town_name', 'debtor_party.town_name');
    addRow('Debtor Country', 'debtor.country', 'debtor_country', 'debtor_party.country');
    addRow('Debtor Country Sub-Division', 'debtor.countrySubDivision', 'debtor_country_sub_division', 'debtor_party.country_sub_division');
    addRow('Debtor Identification Type', 'debtor.idType', 'debtor_id_type', 'debtor_party.identification_type');
    addRow('Debtor Identification Number', 'debtor.id', 'debtor_id', 'debtor_party.identification_number');
    addRow('Debtor Tax ID', null, null, 'debtor_party.tax_id');
    addRow('Debtor Tax ID Type', null, null, 'debtor_party.tax_id_type');

    // =========================================================================
    // SECTION: DEBTOR ACCOUNT - Gold uses cdm_account table
    // =========================================================================
    addSection('DEBTOR ACCOUNT');
    addRow('Debtor Account ID (FK)', null, null, 'debtor_account_id');
    addRow('Debtor Account Type', 'debtorAccount.accountType', 'debtor_account_type', 'debtor_account.account_type');
    addRow('Debtor Account IBAN', 'debtorAccount.iban', 'debtor_account_iban', 'debtor_account.iban');
    addRow('Debtor Account Number', 'debtorAccount.other', 'debtor_account_other', 'debtor_account.account_number');
    addRow('Debtor Account Currency', 'debtorAccount.currency', 'debtor_account_currency', 'debtor_account.currency');

    // =========================================================================
    // SECTION: DEBTOR AGENT (Ordering Bank) - Gold uses cdm_financial_institution table
    // =========================================================================
    addSection('DEBTOR AGENT (ORDERING BANK)');
    addRow('Debtor Agent ID (FK)', null, null, 'debtor_agent_id');
    addRow('Debtor Agent Type', null, null, 'debtor_agent.fi_type');
    addRow('Debtor Agent Name', 'debtorAgent.name', 'debtor_agent_name', 'debtor_agent.name');
    addRow('Debtor Agent BIC', 'debtorAgent.bic', 'debtor_agent_bic', 'debtor_agent.bic');
    addRow('Debtor Agent Clearing System', 'debtorAgent.clearingSystem', 'debtor_agent_clearing_system', 'debtor_agent.clearing_system_id');
    addRow('Debtor Agent Member ID', 'debtorAgent.memberId', 'debtor_agent_member_id', 'debtor_agent.member_id');
    addRow('Debtor Agent Country', 'debtorAgent.country', 'debtor_agent_country', 'debtor_agent.country');
    addRow('Debtor Agent LEI', null, null, 'debtor_agent.lei');

    // =========================================================================
    // SECTION: CREDITOR (Payee Party) - Gold uses cdm_party table
    // =========================================================================
    addSection('CREDITOR (PAYEE)');
    addRow('Creditor ID (FK)', null, null, 'creditor_id');
    addRow('Creditor Party Type', null, null, 'creditor_party.party_type');
    addRow('Creditor Name', 'creditor.name', 'creditor_name', 'creditor_party.name');
    addRow('Creditor Street', 'creditor.streetName', 'creditor_street_name', 'creditor_party.street_name');
    addRow('Creditor Building', 'creditor.buildingNumber', 'creditor_building_number', 'creditor_party.building_number');
    addRow('Creditor Postal Code', 'creditor.postalCode', 'creditor_postal_code', 'creditor_party.post_code');
    addRow('Creditor Town', 'creditor.townName', 'creditor_town_name', 'creditor_party.town_name');
    addRow('Creditor Country', 'creditor.country', 'creditor_country', 'creditor_party.country');
    addRow('Creditor Country Sub-Division', 'creditor.countrySubDivision', 'creditor_country_sub_division', 'creditor_party.country_sub_division');
    addRow('Creditor Identification Type', 'creditor.idType', 'creditor_id_type', 'creditor_party.identification_type');
    addRow('Creditor Identification Number', 'creditor.id', 'creditor_id', 'creditor_party.identification_number');
    addRow('Creditor Tax ID', null, null, 'creditor_party.tax_id');
    addRow('Creditor Tax ID Type', null, null, 'creditor_party.tax_id_type');

    // =========================================================================
    // SECTION: CREDITOR ACCOUNT - Gold uses cdm_account table
    // =========================================================================
    addSection('CREDITOR ACCOUNT');
    addRow('Creditor Account ID (FK)', null, null, 'creditor_account_id');
    addRow('Creditor Account Type', 'creditorAccount.accountType', 'creditor_account_type', 'creditor_account.account_type');
    addRow('Creditor Account IBAN', 'creditorAccount.iban', 'creditor_account_iban', 'creditor_account.iban');
    addRow('Creditor Account Number', 'creditorAccount.other', 'creditor_account_other', 'creditor_account.account_number');
    addRow('Creditor Account Currency', 'creditorAccount.currency', 'creditor_account_currency', 'creditor_account.currency');

    // =========================================================================
    // SECTION: CREDITOR AGENT (Beneficiary Bank) - Gold uses cdm_financial_institution table
    // =========================================================================
    addSection('CREDITOR AGENT (BENEFICIARY BANK)');
    addRow('Creditor Agent ID (FK)', null, null, 'creditor_agent_id');
    addRow('Creditor Agent Type', null, null, 'creditor_agent.fi_type');
    addRow('Creditor Agent Name', 'creditorAgent.name', 'creditor_agent_name', 'creditor_agent.name');
    addRow('Creditor Agent BIC', 'creditorAgent.bic', 'creditor_agent_bic', 'creditor_agent.bic');
    addRow('Creditor Agent Clearing System', 'creditorAgent.clearingSystem', 'creditor_agent_clearing_system', 'creditor_agent.clearing_system_id');
    addRow('Creditor Agent Member ID', 'creditorAgent.memberId', 'creditor_agent_member_id', 'creditor_agent.member_id');
    addRow('Creditor Agent Country', 'creditorAgent.country', 'creditor_agent_country', 'creditor_agent.country');
    addRow('Creditor Agent LEI', null, null, 'creditor_agent.lei');

    // =========================================================================
    // SECTION: INTERMEDIARY AGENTS - Gold uses cdm_financial_institution table
    // =========================================================================
    addSection('INTERMEDIARY AGENTS');
    addRow('Intermediary Agent 1 ID (FK)', null, null, 'intermediary_agent1_id');
    addRow('Intermediary Agent 1 Name', null, null, 'intermediary_agent1.name');
    addRow('Intermediary Agent 1 BIC', null, null, 'intermediary_agent1.bic');
    addRow('Intermediary Agent 1 Country', null, null, 'intermediary_agent1.country');
    addRow('Intermediary Agent 2 ID (FK)', null, null, 'intermediary_agent2_id');
    addRow('Intermediary Agent 2 Name', null, null, 'intermediary_agent2.name');
    addRow('Intermediary Agent 2 BIC', null, null, 'intermediary_agent2.bic');

    // =========================================================================
    // SECTION: ULTIMATE PARTIES - Gold uses cdm_party table
    // =========================================================================
    addSection('ULTIMATE PARTIES');
    addRow('Ultimate Debtor ID (FK)', null, null, 'ultimate_debtor_id');
    addRow('Ultimate Debtor Name', 'ultimateDebtor.name', 'ultimate_debtor_name', 'ultimate_debtor.name');
    addRow('Ultimate Debtor Party Type', null, null, 'ultimate_debtor.party_type');
    addRow('Ultimate Debtor ID Type', 'ultimateDebtor.idType', 'ultimate_debtor_id_type', 'ultimate_debtor.identification_type');
    addRow('Ultimate Debtor ID Number', 'ultimateDebtor.id', 'ultimate_debtor_id', 'ultimate_debtor.identification_number');
    addRow('Ultimate Debtor Country', null, null, 'ultimate_debtor.country');
    addRow('Ultimate Creditor ID (FK)', null, null, 'ultimate_creditor_id');
    addRow('Ultimate Creditor Name', 'ultimateCreditor.name', 'ultimate_creditor_name', 'ultimate_creditor.name');
    addRow('Ultimate Creditor Party Type', null, null, 'ultimate_creditor.party_type');
    addRow('Ultimate Creditor ID Type', 'ultimateCreditor.idType', 'ultimate_creditor_id_type', 'ultimate_creditor.identification_type');
    addRow('Ultimate Creditor ID Number', 'ultimateCreditor.id', 'ultimate_creditor_id', 'ultimate_creditor.identification_number');
    addRow('Ultimate Creditor Country', null, null, 'ultimate_creditor.country');

    // =========================================================================
    // SECTION: DATES & TIMESTAMPS
    // =========================================================================
    addSection('DATES & TIMESTAMPS');
    addRow('Creation DateTime', 'creationDateTime', 'creation_date_time', 'creation_datetime');
    addRow('Requested Execution Date', 'paymentInformation.requestedExecutionDate', 'requested_execution_date', 'requested_execution_date');
    addRow('Value Date', null, null, 'value_date');
    addRow('Settlement Date', null, null, 'settlement_date');
    addRow('Acceptance DateTime', null, null, 'acceptance_datetime');
    addRow('Completion DateTime', null, null, 'completion_datetime');

    // =========================================================================
    // SECTION: REMITTANCE INFORMATION
    // =========================================================================
    addSection('REMITTANCE INFORMATION');
    addRow('Purpose Code', 'purposeCode', 'purpose_code', 'purpose');
    addRow('Purpose Description', null, 'purpose_proprietary', 'purpose_description');
    addRow('Remittance (Unstructured)', 'remittanceInformation.unstructured', 'remittance_information', 'remittance_unstructured');
    addRow('Remittance Reference', 'remittanceInformation.structured.creditorReference', null, 'remittance_reference');
    addRow('Remittance (Structured)', 'remittanceInformation.structured', 'structured_remittance', 'remittance_structured');

    // =========================================================================
    // SECTION: INITIATING PARTY
    // =========================================================================
    addSection('INITIATING PARTY');
    addRow('Initiating Party Name', 'initiatingParty.name', 'initiating_party_name', null);
    addRow('Initiating Party ID', 'initiatingParty.id', 'initiating_party_id', null);
    addRow('Initiating Party ID Type', 'initiatingParty.idType', 'initiating_party_id_type', null);
    addRow('Initiating Party Country', 'initiatingParty.country', 'initiating_party_country', null);

    // =========================================================================
    // SECTION: BATCH INFORMATION
    // =========================================================================
    addSection('BATCH INFORMATION');
    addRow('Number of Transactions', 'numberOfTransactions', 'number_of_transactions', null);
    addRow('Control Sum', 'controlSum', 'control_sum', null);
    addRow('Payment Info ID', 'paymentInformation.paymentInfoId', 'payment_info_id', null);
    addRow('Payment Method', 'paymentInformation.paymentMethod', 'payment_method', null);
    addRow('Batch Booking', 'paymentInformation.batchBooking', 'batch_booking', null);

    // =========================================================================
    // SECTION: STATUS & PROCESSING
    // =========================================================================
    addSection('STATUS & PROCESSING');
    addRow('Current Status', null, 'processing_status', 'current_status');
    addRow('Status Reason Code', null, null, 'status_reason_code');
    addRow('Status Reason Description', null, null, 'status_reason_description');
    addRow('Processing Error', null, 'processing_error', null);

    // =========================================================================
    // SECTION: REGULATORY & COMPLIANCE
    // =========================================================================
    addSection('REGULATORY & COMPLIANCE');
    addRow('Regulatory Reporting', 'regulatoryReporting', 'regulatory_reporting', 'regulatory_extensions');
    addRow('Sanctions Screening Status', null, null, 'sanctions_screening_status');
    addRow('Sanctions Screening Timestamp', null, null, 'sanctions_screening_timestamp');
    addRow('Fraud Score', null, null, 'fraud_score');
    addRow('Fraud Flags', null, null, 'fraud_flags');
    addRow('AML Risk Rating', null, null, 'aml_risk_rating');
    addRow('PEP Flag', null, null, 'pep_flag');
    addRow('Structuring Indicator', null, null, 'structuring_indicator');
    addRow('High Risk Country Flag', null, null, 'high_risk_country_flag');

    // =========================================================================
    // SECTION: DATA QUALITY
    // =========================================================================
    addSection('DATA QUALITY');
    addRow('Data Quality Score', null, null, 'data_quality_score');
    addRow('Data Quality Issues', null, null, 'data_quality_issues');

    // =========================================================================
    // SECTION: LINEAGE & TRACKING (System/Audit Fields)
    // =========================================================================
    addSection('LINEAGE & TRACKING');
    // Bronze tracking
    addRow('Raw ID', null, 'raw_id', 'source_raw_id');
    addRow('Bronze Batch ID', null, null, null);
    rows[rows.length - 1].bronze = fmt(lineage.bronze?._batch_id);
    rows[rows.length - 1].silver = fmt(lineage.silver?._batch_id);
    rows[rows.length - 1].gold = fmt(lineage.gold?.lineage_batch_id);

    addRow('Source STG ID', null, null, 'source_stg_id');
    addRow('Source STG Table', null, null, 'source_stg_table');
    addRow('Source Message Type', null, null, 'source_message_type');
    addRow('Source System', null, null, 'source_system');
    addRow('Lineage Pipeline Run ID', null, null, 'lineage_pipeline_run_id');

    // Temporal tracking
    addRow('Valid From', null, null, 'valid_from');
    addRow('Valid To', null, null, 'valid_to');
    addRow('Is Current', null, null, 'is_current');

    // Partition info
    addRow('Partition Year', null, null, 'partition_year');
    addRow('Partition Month', null, null, 'partition_month');
    addRow('Region', null, null, 'region');

    // Audit fields
    addRow('Created At', null, null, 'created_at');
    addRow('Updated At', null, null, 'updated_at');
    addRow('Updated By', null, null, 'updated_by');
    addRow('Record Version', null, null, 'record_version');
    addRow('Is Deleted', null, null, 'is_deleted');

    // Bronze/Silver timestamps
    addRow('Ingested At', null, null, null);
    rows[rows.length - 1].bronze = fmt(lineage.bronze?._ingested_at);
    rows[rows.length - 1].silver = '-';
    rows[rows.length - 1].gold = '-';

    addRow('Processed To Silver At', null, null, null);
    rows[rows.length - 1].bronze = fmt(lineage.bronze?.processed_to_silver_at);
    rows[rows.length - 1].silver = fmt(lineage.silver?._processed_at);
    rows[rows.length - 1].gold = '-';

    addRow('Processed To Gold At', null, 'processed_to_gold_at', null);

    // Filter out sections that have no data rows after them
    const filteredRows: RowData[] = [];
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      if (row.isHeader) {
        // Check if there are any non-header rows after this header before the next header
        let hasData = false;
        for (let j = i + 1; j < rows.length && !rows[j].isHeader; j++) {
          if (rows[j].bronze !== '-' || rows[j].silver !== '-' || rows[j].gold !== '-') {
            hasData = true;
            break;
          }
        }
        if (hasData) {
          filteredRows.push(row);
        }
      } else {
        // Only add non-header rows if they have some data
        if (row.bronze !== '-' || row.silver !== '-' || row.gold !== '-') {
          filteredRows.push(row);
        }
      }
    }

    return filteredRows;
  };

  const formatValue = (value: any, isDefault?: boolean): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'object') return JSON.stringify(value);
    const strVal = String(value);
    return isDefault ? `${strVal} (default)` : strVal;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth PaperProps={{ sx: { minHeight: '80vh' } }}>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CompareIcon />
            <Typography variant="h6" fontWeight={600}>
              Cross-Zone Record Comparison
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="Table Comparison" />
          <Tab label="Raw Content" />
        </Tabs>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : activeTab === 0 ? (
          <Box>
            {/* Table-based comparison */}
            <Paper sx={{ overflow: 'auto', maxHeight: 600 }}>
              <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse' }}>
                <Box component="thead">
                  <Box component="tr">
                    <Box
                      component="th"
                      sx={{
                        p: 1.5,
                        textAlign: 'left',
                        fontWeight: 600,
                        backgroundColor: colors.grey[100],
                        borderBottom: `2px solid ${colors.grey[300]}`,
                        position: 'sticky',
                        top: 0,
                        width: '20%',
                      }}
                    >
                      Field
                    </Box>
                    <Box
                      component="th"
                      sx={{
                        p: 1.5,
                        textAlign: 'left',
                        fontWeight: 600,
                        backgroundColor: zoneColors.bronze.bg,
                        borderBottom: `2px solid ${zoneColors.bronze.border}`,
                        color: zoneColors.bronze.text,
                        position: 'sticky',
                        top: 0,
                        width: '26.6%',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: zoneColors.bronze.border }} />
                        Bronze (Raw)
                      </Box>
                    </Box>
                    <Box
                      component="th"
                      sx={{
                        p: 1.5,
                        textAlign: 'left',
                        fontWeight: 600,
                        backgroundColor: zoneColors.silver.bg,
                        borderBottom: `2px solid ${zoneColors.silver.border}`,
                        color: zoneColors.silver.text,
                        position: 'sticky',
                        top: 0,
                        width: '26.6%',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ArrowIcon sx={{ fontSize: 14, color: colors.grey[400] }} />
                        <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: zoneColors.silver.border }} />
                        Silver (Staged)
                      </Box>
                    </Box>
                    <Box
                      component="th"
                      sx={{
                        p: 1.5,
                        textAlign: 'left',
                        fontWeight: 600,
                        backgroundColor: zoneColors.gold.bg,
                        borderBottom: `2px solid ${zoneColors.gold.border}`,
                        color: zoneColors.gold.text,
                        position: 'sticky',
                        top: 0,
                        width: '26.6%',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ArrowIcon sx={{ fontSize: 14, color: colors.grey[400] }} />
                        <Box sx={{ width: 10, height: 10, borderRadius: '50%', backgroundColor: zoneColors.gold.border }} />
                        Gold (CDM)
                      </Box>
                    </Box>
                  </Box>
                </Box>
                <Box component="tbody">
                  {getComparisonRows().map((row, idx) => (
                    <Box
                      component="tr"
                      key={idx}
                      sx={{
                        '&:hover': { backgroundColor: row.isHeader ? 'inherit' : colors.grey[50] },
                        backgroundColor: row.isHeader
                          ? colors.primary.main + '15'
                          : row.rawPath
                          ? zoneColors.bronze.bg + '30'
                          : 'transparent',
                      }}
                    >
                      {row.isHeader ? (
                        <Box
                          component="td"
                          colSpan={4}
                          sx={{
                            p: 1.5,
                            py: 1,
                            borderBottom: `2px solid ${colors.primary.main}`,
                            borderTop: idx > 0 ? `1px solid ${colors.grey[300]}` : 'none',
                            fontWeight: 700,
                            fontSize: 11,
                            textTransform: 'uppercase',
                            letterSpacing: 1,
                            color: colors.primary.main,
                            backgroundColor: colors.primary.main + '10',
                          }}
                        >
                          {row.field}
                        </Box>
                      ) : (
                        <>
                          <Box
                            component="td"
                            sx={{
                              p: 1.5,
                              py: 1,
                              borderBottom: `1px solid ${colors.grey[200]}`,
                              fontWeight: 500,
                              fontSize: 12,
                              color: row.field.includes('(FK)') ? colors.grey[500] : 'inherit',
                            }}
                          >
                            {row.field}
                            {row.rawPath && row.bronze !== '-' && (
                              <Tooltip title={`Source path: ${row.rawPath}`}>
                                <Chip
                                  label="MAPPED"
                                  size="small"
                                  sx={{ ml: 1, height: 16, fontSize: 8, backgroundColor: colors.success.light, color: colors.success.dark }}
                                />
                              </Tooltip>
                            )}
                          </Box>
                          <Box
                            component="td"
                            sx={{
                              p: 1.5,
                              py: 1,
                              borderBottom: `1px solid ${colors.grey[200]}`,
                              fontFamily: 'monospace',
                              fontSize: 11,
                              backgroundColor: row.bronze !== '-' ? zoneColors.bronze.bg + '40' : 'transparent',
                              wordBreak: 'break-all',
                              maxWidth: 250,
                            }}
                          >
                            {row.bronze}
                          </Box>
                          <Box
                            component="td"
                            sx={{
                              p: 1.5,
                              py: 1,
                              borderBottom: `1px solid ${colors.grey[200]}`,
                              fontFamily: 'monospace',
                              fontSize: 11,
                              backgroundColor: row.silver !== '-' ? zoneColors.silver.bg + '40' : 'transparent',
                              wordBreak: 'break-all',
                              maxWidth: 250,
                            }}
                          >
                            {row.silver}
                          </Box>
                          <Box
                            component="td"
                            sx={{
                              p: 1.5,
                              py: 1,
                              borderBottom: `1px solid ${colors.grey[200]}`,
                              fontFamily: 'monospace',
                              fontSize: 11,
                              backgroundColor: row.gold !== '-' ? zoneColors.gold.bg + '40' : 'transparent',
                              wordBreak: 'break-all',
                              maxWidth: 250,
                            }}
                          >
                            {row.gold}
                          </Box>
                        </>
                      )}
                    </Box>
                  ))}
                </Box>
              </Box>
            </Paper>

            {/* Lineage Warning */}
            {lineage && (!lineage.silver || !lineage.gold) && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Some zone data is missing. This may indicate the record hasn't been fully processed through the pipeline.
              </Alert>
            )}

            {/* Field Mappings */}
            {lineage?.field_mappings && lineage.field_mappings.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
                  Schema Field Mappings (from Neo4j)
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {lineage.field_mappings.slice(0, 20).map((mapping: any, idx: number) => (
                    <Chip
                      key={idx}
                      label={`${mapping.source || mapping.source_field} → ${mapping.target || mapping.target_field}`}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: 11 }}
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Box>
        ) : (
          <Box>
            {/* Raw content view */}
            <Alert severity="info" sx={{ mb: 2 }}>
              This shows the original raw_content from Bronze. Silver and Gold fields are derived from this data.
            </Alert>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
              Bronze Raw Content
            </Typography>
            <Paper
              sx={{
                p: 2,
                backgroundColor: zoneColors.bronze.bg,
                border: `2px solid ${zoneColors.bronze.border}`,
                maxHeight: 400,
                overflow: 'auto',
              }}
            >
              <Typography
                component="pre"
                sx={{ fontFamily: 'monospace', fontSize: 12, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}
              >
                {lineage?.bronze?.raw_content
                  ? typeof lineage.bronze.raw_content === 'string'
                    ? (() => { try { return JSON.stringify(JSON.parse(lineage.bronze.raw_content), null, 2); } catch { return lineage.bronze.raw_content; } })()
                    : JSON.stringify(lineage.bronze.raw_content, null, 2)
                  : 'No raw content available'}
              </Typography>
            </Paper>

            {/* Show what Silver extracted */}
            {lineage?.silver && (
              <>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1, mt: 3 }}>
                  Silver Extracted Fields
                </Typography>
                <Paper
                  sx={{
                    p: 2,
                    backgroundColor: zoneColors.silver.bg,
                    border: `2px solid ${zoneColors.silver.border}`,
                    maxHeight: 300,
                    overflow: 'auto',
                  }}
                >
                  <Typography
                    component="pre"
                    sx={{ fontFamily: 'monospace', fontSize: 12, whiteSpace: 'pre-wrap' }}
                  >
                    {JSON.stringify({
                      stg_id: lineage.silver.stg_id,
                      msg_id: lineage.silver.msg_id,
                      debtor_name: lineage.silver.debtor_name,
                      creditor_name: lineage.silver.creditor_name,
                      instructed_amount: lineage.silver.instructed_amount,
                      instructed_currency: lineage.silver.instructed_currency,
                      processing_status: lineage.silver.processing_status,
                    }, null, 2)}
                  </Typography>
                </Paper>
              </>
            )}

            {/* Show what Gold has */}
            {lineage?.gold && (
              <>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1, mt: 3 }}>
                  Gold CDM Fields
                </Typography>
                <Paper
                  sx={{
                    p: 2,
                    backgroundColor: zoneColors.gold.bg,
                    border: `2px solid ${zoneColors.gold.border}`,
                    maxHeight: 300,
                    overflow: 'auto',
                  }}
                >
                  <Typography
                    component="pre"
                    sx={{ fontFamily: 'monospace', fontSize: 12, whiteSpace: 'pre-wrap' }}
                  >
                    {JSON.stringify({
                      instruction_id: lineage.gold.instruction_id,
                      payment_id: lineage.gold.payment_id,
                      payment_type: lineage.gold.payment_type,
                      source_message_type: lineage.gold.source_message_type,
                      instructed_amount: lineage.gold.instructed_amount,
                      instructed_currency: lineage.gold.instructed_currency,
                      current_status: lineage.gold.current_status,
                    }, null, 2)}
                  </Typography>
                </Paper>
              </>
            )}
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};

// Edit Record Dialog Component
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

  // Fetch record details
  const { data: recordData, isLoading } = useQuery({
    queryKey: ['recordDetail', layer, recordId],
    queryFn: () => pipelineApi.getRecordDetails(layer, recordId),
    enabled: open && !!recordId,
  });

  // Set initial content when data loads
  React.useEffect(() => {
    if (recordData?.raw_content) {
      const content = typeof recordData.raw_content === 'string'
        ? recordData.raw_content
        : JSON.stringify(recordData.raw_content, null, 2);
      setEditedContent(content);
    }
  }, [recordData]);

  // Reprocess mutation
  const reprocessMutation = useMutation({
    mutationFn: async () => {
      // Update the record content and trigger reprocess
      const parsedContent = JSON.parse(editedContent);
      return reprocessApi.updateRecord(
        layer,
        layer === 'bronze' ? 'raw_payment_messages' : layer === 'silver' ? 'stg_payment' : 'cdm_payment_instruction',
        recordId,
        { raw_content: parsedContent },
        true
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batchRecords'] });
      queryClient.invalidateQueries({ queryKey: ['recordLineage'] });
      onSuccess();
      onClose();
    },
    onError: (err: any) => {
      setError(err.message || 'Failed to reprocess record');
    },
  });

  const handleReprocess = () => {
    setError(null);
    try {
      // Validate JSON
      JSON.parse(editedContent);
      reprocessMutation.mutate();
    } catch {
      setError('Invalid JSON format');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <EditIcon />
            <Typography variant="h6" fontWeight={600}>
              Edit & Reprocess Record
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ mt: 1 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Edit the record content below and click "Reprocess" to update and re-run the pipeline.
            </Alert>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
              Record Content (JSON)
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={15}
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              sx={{
                '& .MuiInputBase-input': {
                  fontFamily: 'monospace',
                  fontSize: 12,
                },
              }}
            />
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          color="primary"
          startIcon={<ReplayIcon />}
          onClick={handleReprocess}
          disabled={reprocessMutation.isPending || isLoading}
        >
          {reprocessMutation.isPending ? 'Reprocessing...' : 'Reprocess'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const BatchRecordsTab: React.FC<BatchRecordsTabProps> = ({ batchId, messageType }) => {
  const queryClient = useQueryClient();
  const [selectedLayer, setSelectedLayer] = useState<LayerType>('bronze');
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 25,
  });
  const [selectedRecord, setSelectedRecord] = useState<{ layer: LayerType; id: string } | null>(null);
  const [editRecord, setEditRecord] = useState<{ layer: LayerType; id: string } | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Fetch records for selected layer
  const { data, isLoading, refetch } = useQuery({
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
        total: records.length,
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

  const handleViewRecord = (recordId: string) => {
    setSelectedRecord({ layer: selectedLayer, id: recordId });
  };

  // Dynamic columns based on layer
  const columns: GridColDef[] = useMemo(() => {
    const baseColumns: GridColDef[] = [];

    // Add actions column first
    baseColumns.push({
      field: 'actions',
      headerName: 'Actions',
      width: 140,
      sortable: false,
      filterable: false,
      renderCell: (params: GridRenderCellParams) => {
        const recordId =
          selectedLayer === 'bronze'
            ? params.row.raw_id
            : selectedLayer === 'silver'
            ? params.row.stg_id
            : params.row.instruction_id;
        const isFailed = params.row.processing_status === 'FAILED' || params.row.current_status === 'FAILED';
        return (
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="View Details">
              <IconButton size="small" onClick={() => handleViewRecord(recordId)}>
                <ViewIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Compare Across Zones">
              <IconButton size="small" onClick={() => handleViewRecord(recordId)} color="primary">
                <CompareIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title={isFailed ? "Edit & Reprocess (Failed)" : "Edit & Reprocess"}>
              <IconButton
                size="small"
                onClick={() => setEditRecord({ layer: selectedLayer, id: recordId })}
                color={isFailed ? "error" : "default"}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        );
      },
    });

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
          field: 'processing_status',
          headerName: 'Status',
          width: 100,
          renderCell: (params: GridRenderCellParams) => (
            <Chip
              label={params.value || 'N/A'}
              size="small"
              color={statusColors[params.value] || 'default'}
              sx={{ fontSize: 11 }}
            />
          ),
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
          field: 'current_status',
          headerName: 'Status',
          width: 100,
          renderCell: (params: GridRenderCellParams) => (
            <Chip
              label={params.value || 'N/A'}
              size="small"
              color={statusColors[params.value] || 'default'}
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

      {/* Record Comparison Dialog */}
      {selectedRecord && (
        <RecordComparisonDialog
          open={!!selectedRecord}
          onClose={() => setSelectedRecord(null)}
          layer={selectedRecord.layer}
          recordId={selectedRecord.id}
        />
      )}

      {/* Edit Record Dialog */}
      {editRecord && (
        <EditRecordDialog
          open={!!editRecord}
          onClose={() => setEditRecord(null)}
          layer={editRecord.layer}
          recordId={editRecord.id}
          onSuccess={() => {
            setSnackbar({ open: true, message: 'Record updated and reprocessed successfully', severity: 'success' });
            refetch();
          }}
        />
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default BatchRecordsTab;
