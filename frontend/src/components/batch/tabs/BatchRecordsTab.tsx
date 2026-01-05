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
  Edit as EditIcon,
  Replay as ReplayIcon,
  Error as ErrorIcon,
  AccountBalance as BankIcon,
  Person as PersonIcon,
  AccountBalanceWallet as AccountIcon,
  Payment as PaymentIcon,
  Extension as ExtensionIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelineApi, reprocessApi } from '../../../api/client';

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
  'EXTENSION DATA': { icon: ExtensionIcon, color: '#0097a7', bg: '#e0f7fa' },
  'LINEAGE & METADATA': { icon: HistoryIcon, color: '#455a64', bg: '#eceff1' },
};

/**
 * Cross-Zone Comparison Dialog
 * Shows fields organized by CDM entity structure
 */
const RecordComparisonDialog: React.FC<{
  open: boolean;
  onClose: () => void;
  layer: LayerType;
  recordId: string;
  messageType: string;
}> = ({ open, onClose, layer, recordId, messageType }) => {
  const [activeTab, setActiveTab] = useState(0);

  const { data: lineage, isLoading } = useQuery({
    queryKey: ['recordLineage', layer, recordId],
    queryFn: () => pipelineApi.getRecordLineage(layer, recordId),
    enabled: open && !!recordId,
  });

  // Format value for display
  const fmt = (val: any): string => {
    if (val === null || val === undefined) return '';
    if (typeof val === 'object') return JSON.stringify(val, null, 2);
    if (typeof val === 'boolean') return val ? 'Yes' : 'No';
    return String(val);
  };

  // Build comparison data organized by CDM entities
  const comparisonData = useMemo(() => {
    if (!lineage) return [];

    const bronze = lineage.bronze || {};
    const bronzeParsed = (lineage as any).bronze_parsed || {};
    const silver = lineage.silver || {};
    const gold = lineage.gold || {};
    const goldEntities = lineage.gold_entities || {};
    const goldExtension = (lineage as any).gold_extension || {};

    // Helper to create a row - consolidated Bronze column shows parsed data or raw
    const row = (category: string, field: string, bronzeVal: string, silver: string, gold: string, fkInfo?: string) =>
      ({ category, field, bronze: bronzeVal, silver, gold, fkInfo });

    const rows: ReturnType<typeof row>[] = [];

    // ==========================================
    // ENTITY 1: CDM_PAYMENT_INSTRUCTION
    // Core payment record fields
    // ==========================================
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'instruction_id', '', '', fmt(gold.instruction_id)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'payment_id', fmt(bronzeParsed.messageId || bronze.message_type), fmt(silver.message_id), fmt(gold.payment_id)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'message_id', fmt(bronzeParsed.messageId), fmt(silver.message_id), fmt(gold.message_id)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'instruction_id_ext', fmt(bronzeParsed.instructionId), fmt(silver.instruction_id), fmt(gold.instruction_id_ext)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'end_to_end_id', fmt(bronzeParsed.endToEndId), fmt(silver.end_to_end_id), fmt(gold.end_to_end_id)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'uetr', fmt(bronzeParsed.uetr), fmt(silver.uetr), fmt(gold.uetr)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'transaction_id', '', '', fmt(gold.transaction_id)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'related_reference', '', '', fmt(gold.related_reference)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'source_message_type', fmt(bronze.message_type || bronzeParsed.messageType), fmt(silver.message_type), fmt(gold.source_message_type)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'message_format', fmt(bronze.message_format), '', ''));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'payment_type', '', '', fmt(gold.payment_type)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'scheme_code', '', '', fmt(gold.scheme_code)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'direction', '', '', fmt(gold.direction)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'cross_border_flag', '', '', fmt(gold.cross_border_flag)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'priority', '', '', fmt(gold.priority)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'service_level', '', '', fmt(gold.service_level)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'local_instrument', '', '', fmt(gold.local_instrument)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'category_purpose', '', '', fmt(gold.category_purpose)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'instructed_amount', fmt(bronzeParsed.amount), fmt(silver.amount), fmt(gold.instructed_amount)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'instructed_currency', fmt(bronzeParsed.currency), fmt(silver.currency), fmt(gold.instructed_currency)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'interbank_settlement_amount', '', '', fmt(gold.interbank_settlement_amount)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'interbank_settlement_currency', '', '', fmt(gold.interbank_settlement_currency)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'exchange_rate', '', '', fmt(gold.exchange_rate)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'exchange_rate_type', '', '', fmt(gold.exchange_rate_type)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'creation_datetime', fmt(bronzeParsed.creationDateTime), fmt(silver.creation_date_time), fmt(gold.creation_datetime)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'requested_execution_date', '', '', fmt(gold.requested_execution_date)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'value_date', '', '', fmt(gold.value_date)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'settlement_date', fmt(bronzeParsed.settlementDate), fmt(silver.settlement_date), fmt(gold.settlement_date)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'acceptance_datetime', '', '', fmt(gold.acceptance_datetime)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'completion_datetime', '', '', fmt(gold.completion_datetime)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'purpose', '', '', fmt(gold.purpose)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'purpose_description', '', '', fmt(gold.purpose_description)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'charge_bearer', fmt(bronzeParsed.chargeBearer), '', fmt(gold.charge_bearer)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'remittance_unstructured', fmt(bronzeParsed.remittanceInfo), fmt(silver.remittance_info), fmt(gold.remittance_unstructured)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'remittance_reference', '', '', fmt(gold.remittance_reference)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'remittance_structured', '', '', fmt(gold.remittance_structured)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'sender_to_receiver_info', fmt(bronzeParsed.senderToReceiverInfo), '', fmt(gold.sender_to_receiver_info)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'current_status', fmt(bronze.processing_status), fmt(silver.processing_status), fmt(gold.current_status)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'status_reason_code', '', '', fmt(gold.status_reason_code)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'status_reason_description', '', '', fmt(gold.status_reason_description)));
    // Compliance fields
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'sanctions_screening_status', '', '', fmt(gold.sanctions_screening_status)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'fraud_score', '', '', fmt(gold.fraud_score)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'aml_risk_rating', '', '', fmt(gold.aml_risk_rating)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'pep_flag', '', '', fmt(gold.pep_flag)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'structuring_indicator', '', '', fmt(gold.structuring_indicator)));
    rows.push(row('CDM_PAYMENT_INSTRUCTION', 'high_risk_country_flag', '', '', fmt(gold.high_risk_country_flag)));

    // ==========================================
    // ENTITY 2: CDM_PARTY (DEBTOR)
    // Debtor party entity
    // ==========================================
    const debtorParty = goldEntities.debtor_party || {};
    rows.push(row('CDM_PARTY (DEBTOR)', 'party_id', '', '', fmt(debtorParty.party_id), fmt(gold.debtor_id)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'party_type', '', '', fmt(debtorParty.party_type)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'name', fmt(bronzeParsed.debtorName), fmt(silver.debtor_name), fmt(debtorParty.name)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'street_name', fmt(bronzeParsed.debtorStreetName), fmt(silver.debtor_street_name), fmt(debtorParty.street_name)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'building_number', '', '', fmt(debtorParty.building_number)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'post_code', fmt(bronzeParsed.debtorPostCode), fmt(silver.debtor_post_code), fmt(debtorParty.post_code)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'town_name', fmt(bronzeParsed.debtorTownName), fmt(silver.debtor_town_name), fmt(debtorParty.town_name)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'country_sub_division', '', '', fmt(debtorParty.country_sub_division)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'country', fmt(bronzeParsed.debtorCountry), fmt(silver.debtor_country), fmt(debtorParty.country)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'address (combined)', fmt(bronzeParsed.debtorAddress), fmt(silver.debtor_address), fmt(debtorParty.address)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'identification_type', '', '', fmt(debtorParty.identification_type)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'identification_number', '', '', fmt(debtorParty.identification_number)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'tax_id', '', '', fmt(debtorParty.tax_id)));
    rows.push(row('CDM_PARTY (DEBTOR)', 'tax_id_type', '', '', fmt(debtorParty.tax_id_type)));

    // ==========================================
    // ENTITY 3: CDM_PARTY (CREDITOR)
    // Creditor party entity
    // ==========================================
    const creditorParty = goldEntities.creditor_party || {};
    rows.push(row('CDM_PARTY (CREDITOR)', 'party_id', '', '', fmt(creditorParty.party_id), fmt(gold.creditor_id)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'party_type', '', '', fmt(creditorParty.party_type)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'name', fmt(bronzeParsed.creditorName), fmt(silver.creditor_name), fmt(creditorParty.name)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'street_name', fmt(bronzeParsed.creditorStreetName), fmt(silver.creditor_street_name), fmt(creditorParty.street_name)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'building_number', '', '', fmt(creditorParty.building_number)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'post_code', fmt(bronzeParsed.creditorPostCode), fmt(silver.creditor_post_code), fmt(creditorParty.post_code)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'town_name', fmt(bronzeParsed.creditorTownName), fmt(silver.creditor_town_name), fmt(creditorParty.town_name)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'country_sub_division', '', '', fmt(creditorParty.country_sub_division)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'country', fmt(bronzeParsed.creditorCountry), fmt(silver.creditor_country), fmt(creditorParty.country)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'address (combined)', fmt(bronzeParsed.creditorAddress), fmt(silver.creditor_address), fmt(creditorParty.address)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'identification_type', '', '', fmt(creditorParty.identification_type)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'identification_number', '', '', fmt(creditorParty.identification_number)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'tax_id', '', '', fmt(creditorParty.tax_id)));
    rows.push(row('CDM_PARTY (CREDITOR)', 'tax_id_type', '', '', fmt(creditorParty.tax_id_type)));

    // ==========================================
    // ENTITY 4: CDM_PARTY (ULTIMATE)
    // Ultimate debtor/creditor parties
    // ==========================================
    const ultimateDebtor = goldEntities.ultimate_debtor || {};
    const ultimateCreditor = goldEntities.ultimate_creditor || {};
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_debtor_id', '', '', fmt(ultimateDebtor.party_id), fmt(gold.ultimate_debtor_id)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_debtor_name', '', '', fmt(ultimateDebtor.name)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_debtor_party_type', '', '', fmt(ultimateDebtor.party_type)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_debtor_country', '', '', fmt(ultimateDebtor.country)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_creditor_id', '', '', fmt(ultimateCreditor.party_id), fmt(gold.ultimate_creditor_id)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_creditor_name', '', '', fmt(ultimateCreditor.name)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_creditor_party_type', '', '', fmt(ultimateCreditor.party_type)));
    rows.push(row('CDM_PARTY (ULTIMATE)', 'ultimate_creditor_country', '', '', fmt(ultimateCreditor.country)));

    // ==========================================
    // ENTITY 5: CDM_ACCOUNT (DEBTOR)
    // Debtor account entity
    // ==========================================
    const debtorAccount = goldEntities.debtor_account || {};
    rows.push(row('CDM_ACCOUNT (DEBTOR)', 'account_id', '', '', fmt(debtorAccount.account_id), fmt(gold.debtor_account_id)));
    rows.push(row('CDM_ACCOUNT (DEBTOR)', 'account_type', '', '', fmt(debtorAccount.account_type)));
    rows.push(row('CDM_ACCOUNT (DEBTOR)', 'iban', '', '', fmt(debtorAccount.iban)));
    rows.push(row('CDM_ACCOUNT (DEBTOR)', 'account_number', fmt(bronzeParsed.debtorAccount), fmt(silver.debtor_account), fmt(debtorAccount.account_number)));
    rows.push(row('CDM_ACCOUNT (DEBTOR)', 'sort_code', fmt(bronzeParsed.debtorSortCode), fmt(silver.debtor_sort_code), ''));
    rows.push(row('CDM_ACCOUNT (DEBTOR)', 'currency', '', '', fmt(debtorAccount.currency)));

    // ==========================================
    // ENTITY 6: CDM_ACCOUNT (CREDITOR)
    // Creditor account entity
    // ==========================================
    const creditorAccount = goldEntities.creditor_account || {};
    rows.push(row('CDM_ACCOUNT (CREDITOR)', 'account_id', '', '', fmt(creditorAccount.account_id), fmt(gold.creditor_account_id)));
    rows.push(row('CDM_ACCOUNT (CREDITOR)', 'account_type', '', '', fmt(creditorAccount.account_type)));
    rows.push(row('CDM_ACCOUNT (CREDITOR)', 'iban', '', '', fmt(creditorAccount.iban)));
    rows.push(row('CDM_ACCOUNT (CREDITOR)', 'account_number', fmt(bronzeParsed.creditorAccount), fmt(silver.creditor_account), fmt(creditorAccount.account_number)));
    rows.push(row('CDM_ACCOUNT (CREDITOR)', 'sort_code', fmt(bronzeParsed.creditorSortCode), fmt(silver.creditor_sort_code), ''));
    rows.push(row('CDM_ACCOUNT (CREDITOR)', 'currency', '', '', fmt(creditorAccount.currency)));

    // ==========================================
    // ENTITY 7: CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)
    // Debtor agent (ordering bank)
    // ==========================================
    const debtorAgent = goldEntities.debtor_agent || {};
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'fi_id', '', '', fmt(debtorAgent.fi_id), fmt(gold.debtor_agent_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'fi_type', '', '', fmt(debtorAgent.fi_type)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'institution_name', '', '', fmt(debtorAgent.name)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'bic', fmt(bronzeParsed.debtorAgentBic), fmt(silver.debtor_agent_bic), fmt(debtorAgent.bic)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'clearing_system_id', '', fmt(silver.debtor_clearing_system || 'GBDSC'), fmt(debtorAgent.clearing_system_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'member_id (sort_code)', fmt(bronzeParsed.debtorSortCode), fmt(silver.debtor_sort_code), fmt(debtorAgent.member_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'country', fmt(bronzeParsed.debtorCountry || 'GB'), fmt(silver.debtor_country || 'GB'), fmt(debtorAgent.country)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (DEBTOR_AGENT)', 'lei', '', '', fmt(debtorAgent.lei)));

    // ==========================================
    // ENTITY 8: CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)
    // Creditor agent (beneficiary bank)
    // ==========================================
    const creditorAgent = goldEntities.creditor_agent || {};
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'fi_id', '', '', fmt(creditorAgent.fi_id), fmt(gold.creditor_agent_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'fi_type', '', '', fmt(creditorAgent.fi_type)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'institution_name', '', '', fmt(creditorAgent.name)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'bic', fmt(bronzeParsed.creditorAgentBic), fmt(silver.creditor_agent_bic), fmt(creditorAgent.bic)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'clearing_system_id', '', fmt(silver.creditor_clearing_system || 'GBDSC'), fmt(creditorAgent.clearing_system_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'member_id (sort_code)', fmt(bronzeParsed.creditorSortCode), fmt(silver.creditor_sort_code), fmt(creditorAgent.member_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'country', fmt(bronzeParsed.creditorCountry || 'GB'), fmt(silver.creditor_country || 'GB'), fmt(creditorAgent.country)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (CREDITOR_AGENT)', 'lei', '', '', fmt(creditorAgent.lei)));

    // ==========================================
    // ENTITY 9: CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)
    // Intermediary agents
    // ==========================================
    const intermediary1 = goldEntities.intermediary_agent1 || {};
    const intermediary2 = goldEntities.intermediary_agent2 || {};
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary_agent1_id', '', '', fmt(intermediary1.fi_id), fmt(gold.intermediary_agent1_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary1_name', '', '', fmt(intermediary1.name)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary1_bic', '', '', fmt(intermediary1.bic)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary1_country', '', '', fmt(intermediary1.country)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary_agent2_id', '', '', fmt(intermediary2.fi_id), fmt(gold.intermediary_agent2_id)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary2_name', '', '', fmt(intermediary2.name)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary2_bic', '', '', fmt(intermediary2.bic)));
    rows.push(row('CDM_FINANCIAL_INSTITUTION (INTERMEDIARIES)', 'intermediary2_country', '', '', fmt(intermediary2.country)));

    // ==========================================
    // ENTITY 10: EXTENSION DATA
    // Format-specific extension fields
    // ==========================================
    if (Object.keys(goldExtension).length > 0) {
      const extTable = goldExtension._table || 'extension';
      // Add extension table name as header info
      rows.push(row('EXTENSION DATA', `[Table: gold.${extTable}]`, '', '', ''));
      Object.entries(goldExtension).forEach(([key, value]) => {
        if (key === '_table' || key === 'instruction_id' || key === 'extension_id' || key === 'created_at' || key === 'updated_at') return;
        rows.push(row('EXTENSION DATA', key, '', '', fmt(value)));
      });
    } else {
      rows.push(row('EXTENSION DATA', '(no extension data)', '', '', ''));
    }

    // ==========================================
    // ENTITY 11: LINEAGE & METADATA
    // Processing lineage and audit fields
    // ==========================================
    rows.push(row('LINEAGE & METADATA', 'raw_id (Bronze PK)', fmt(bronze.raw_id), fmt(silver.raw_id), fmt(gold.source_raw_id)));
    rows.push(row('LINEAGE & METADATA', 'stg_id (Silver PK)', '', fmt(silver.stg_id), fmt(gold.source_stg_id)));
    rows.push(row('LINEAGE & METADATA', 'source_stg_table', '', fmt(silver.source_table), fmt(gold.source_stg_table)));
    rows.push(row('LINEAGE & METADATA', 'batch_id', fmt(bronze._batch_id), fmt(silver._batch_id), fmt(gold.lineage_batch_id)));
    rows.push(row('LINEAGE & METADATA', 'pipeline_run_id', '', '', fmt(gold.lineage_pipeline_run_id)));
    rows.push(row('LINEAGE & METADATA', 'source_system', fmt(bronze.source_system), '', fmt(gold.source_system)));
    rows.push(row('LINEAGE & METADATA', '_ingested_at', fmt(bronze._ingested_at), '', ''));
    rows.push(row('LINEAGE & METADATA', '_processed_at', '', fmt(silver._processed_at), ''));
    rows.push(row('LINEAGE & METADATA', 'processed_to_gold_at', '', fmt(silver.processed_to_gold_at), ''));
    rows.push(row('LINEAGE & METADATA', 'created_at', '', '', fmt(gold.created_at)));
    rows.push(row('LINEAGE & METADATA', 'updated_at', '', '', fmt(gold.updated_at)));
    rows.push(row('LINEAGE & METADATA', 'valid_from', '', '', fmt(gold.valid_from)));
    rows.push(row('LINEAGE & METADATA', 'valid_to', '', '', fmt(gold.valid_to)));
    rows.push(row('LINEAGE & METADATA', 'updated_by', '', '', fmt(gold.updated_by)));
    rows.push(row('LINEAGE & METADATA', 'record_version', '', '', fmt(gold.record_version)));
    rows.push(row('LINEAGE & METADATA', 'is_current', '', '', fmt(gold.is_current)));
    rows.push(row('LINEAGE & METADATA', 'is_deleted', '', '', fmt(gold.is_deleted)));
    rows.push(row('LINEAGE & METADATA', 'partition_year', '', '', fmt(gold.partition_year)));
    rows.push(row('LINEAGE & METADATA', 'partition_month', '', '', fmt(gold.partition_month)));
    rows.push(row('LINEAGE & METADATA', 'region', '', '', fmt(gold.region)));
    rows.push(row('LINEAGE & METADATA', 'data_quality_score', '', '', fmt(gold.data_quality_score)));
    rows.push(row('LINEAGE & METADATA', 'data_quality_issues', '', '', fmt(gold.data_quality_issues)));

    return rows;
  }, [lineage]);

  // Group rows by category
  const groupedData = useMemo(() => {
    const groups: { category: string; rows: typeof comparisonData }[] = [];
    let currentCategory = '';
    let currentRows: typeof comparisonData = [];

    comparisonData.forEach(row => {
      if (row.category !== currentCategory) {
        if (currentRows.length > 0) {
          groups.push({ category: currentCategory, rows: currentRows });
        }
        currentCategory = row.category;
        currentRows = [];
      }
      currentRows.push(row);
    });
    if (currentRows.length > 0) {
      groups.push({ category: currentCategory, rows: currentRows });
    }
    return groups;
  }, [comparisonData]);

  // Count non-empty values per zone
  const stats = useMemo(() => {
    let bronze = 0, silver = 0, gold = 0;
    comparisonData.forEach(row => {
      if (row.bronze) bronze++;
      if (row.silver) silver++;
      if (row.gold) gold++;
    });
    return { bronze, silver, gold, total: comparisonData.length };
  }, [comparisonData]);

  // Count entities with data
  const entityCounts = useMemo(() => {
    const counts: Record<string, { fields: number; populated: number }> = {};
    groupedData.forEach(group => {
      const populated = group.rows.filter(r => r.bronze || r.silver || r.gold).length;
      counts[group.category] = { fields: group.rows.length, populated };
    });
    return counts;
  }, [groupedData]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth PaperProps={{ sx: { height: '90vh' } }}>
      <DialogTitle sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CompareIcon />
            <Typography variant="h6" fontWeight={600}>
              Cross-Zone Comparison by CDM Entity
            </Typography>
            <Chip label={messageType} size="small" color="primary" variant="outlined" />
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
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ px: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Tab label={`CDM Entities (${groupedData.length})`} />
          <Tab label="Raw JSON" />
        </Tabs>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>
        ) : activeTab === 0 ? (
          <Box sx={{ height: 'calc(90vh - 140px)', overflow: 'auto' }}>
            <Box component="table" sx={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <Box component="thead" sx={{ position: 'sticky', top: 0, zIndex: 10 }}>
                <Box component="tr">
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: '#f5f5f5', borderBottom: '2px solid #ccc', width: '25%' }}>
                    CDM Field
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: zoneColors.bronze.bg, borderBottom: `2px solid ${zoneColors.bronze.border}`, width: '20%' }}>
                    Bronze (Parsed)
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: zoneColors.silver.bg, borderBottom: `2px solid ${zoneColors.silver.border}`, width: '25%' }}>
                    Silver (stg_*)
                  </Box>
                  <Box component="th" sx={{ p: 1, textAlign: 'left', fontWeight: 700, backgroundColor: zoneColors.gold.bg, borderBottom: `2px solid ${zoneColors.gold.border}`, width: '30%' }}>
                    Gold (CDM Entity)
                  </Box>
                </Box>
              </Box>
              <Box component="tbody">
                {groupedData.map((group, gIdx) => {
                  const style = entityStyles[group.category as keyof typeof entityStyles] || { icon: PaymentIcon, color: '#666', bg: '#f5f5f5' };
                  const IconComponent = style.icon;
                  const counts = entityCounts[group.category] || { fields: 0, populated: 0 };

                  return (
                    <React.Fragment key={gIdx}>
                      {/* Entity Category Header - spans all 4 columns */}
                      <Box component="tr">
                        <Box component="td" colSpan={4} sx={{
                          p: 1, py: 0.75, fontWeight: 700, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5,
                          backgroundColor: style.bg, color: style.color, borderTop: gIdx > 0 ? `2px solid ${style.color}40` : 'none',
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <IconComponent sx={{ fontSize: 16 }} />
                            {group.category}
                            <Chip label={`${counts.populated}/${counts.fields}`} size="small" sx={{ ml: 1, height: 18, fontSize: 10, backgroundColor: 'white' }} />
                          </Box>
                        </Box>
                      </Box>
                      {/* Data Rows */}
                      {group.rows.map((row, rIdx) => {
                        const hasAnyData = row.bronze || row.silver || row.gold;
                        const bronzeHasData = row.bronze;
                        const silverMissing = !!(bronzeHasData && !row.silver);
                        const isHeaderRow = row.field.startsWith('[');
                        const hasFkInfo = row.fkInfo;

                        return (
                          <Box component="tr" key={rIdx} sx={{
                            '&:hover': { backgroundColor: '#f5f5f5' },
                            backgroundColor: silverMissing ? '#ffebee' : isHeaderRow ? '#fafafa' : 'transparent',
                            opacity: hasAnyData ? 1 : 0.5,
                          }}>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontWeight: isHeaderRow ? 600 : 500,
                              fontStyle: isHeaderRow ? 'italic' : 'normal', color: isHeaderRow ? '#666' : 'inherit',
                              fontFamily: 'monospace', fontSize: 11
                            }}>
                              {row.field}
                              {hasFkInfo && <Tooltip title={`FK: ${row.fkInfo}`}><Chip label="FK" size="small" sx={{ ml: 0.5, height: 14, fontSize: 8, backgroundColor: '#e3f2fd' }} /></Tooltip>}
                              {silverMissing && <Tooltip title="Data parsed from Bronze but missing in Silver"><ErrorIcon sx={{ fontSize: 12, color: 'error.main', ml: 0.5 }} /></Tooltip>}
                            </Box>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10,
                              backgroundColor: row.bronze ? zoneColors.bronze.bg + '80' : 'transparent',
                              wordBreak: 'break-word', maxWidth: 180
                            }}>
                              {row.bronze || '-'}
                            </Box>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10,
                              backgroundColor: row.silver ? zoneColors.silver.bg + '80' : silverMissing ? '#ffcdd2' : 'transparent',
                              wordBreak: 'break-word', maxWidth: 220
                            }}>
                              {row.silver || (silverMissing ? '⚠️ MISSING' : '-')}
                            </Box>
                            <Box component="td" sx={{
                              p: 0.75, borderBottom: '1px solid #eee', fontFamily: 'monospace', fontSize: 10,
                              backgroundColor: row.gold ? zoneColors.gold.bg + '80' : 'transparent',
                              wordBreak: 'break-word', maxWidth: 280
                            }}>
                              {row.gold || '-'}
                              {hasFkInfo && row.gold && <Chip label={row.fkInfo} size="small" sx={{ ml: 0.5, height: 14, fontSize: 8, backgroundColor: '#e3f2fd' }} />}
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
          <Box sx={{ p: 2, height: 'calc(90vh - 140px)', overflow: 'auto' }}>
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
