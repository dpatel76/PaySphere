-- =============================================================================
-- GPS CDM - Fix Mapping Path Alignment
-- =============================================================================
-- This script fixes the path alignment issue between standard_fields and
-- silver_field_mappings so they can be properly joined for reconciliation.
--
-- The solution:
-- 1. Update silver_field_mappings.source_path to use full paths (with root element)
-- 2. Update views to properly join on matching paths
-- 3. For formats that use different path notations (SWIFT MT, FEDWIRE),
--    the field_tag column provides an alternative join key
-- =============================================================================

-- =============================================================================
-- Step 1: Update silver_field_mappings for pain.001 to use full XPath
-- =============================================================================
-- pain.001 uses XPath. Current paths like "GrpHdr/MsgId" should be
-- "CstmrCdtTrfInitn/GrpHdr/MsgId" to match standard_fields

UPDATE mapping.silver_field_mappings
SET source_path = 'CstmrCdtTrfInitn/' || source_path
WHERE format_id = 'pain.001'
  AND source_path NOT LIKE 'CstmrCdtTrfInitn/%'
  AND source_path LIKE '%/%'  -- Only update XPath-style paths
  AND source_path NOT LIKE '{%'  -- Not tag-style
  AND source_path NOT LIKE '%.%' -- Not dot-notation (old data to clean up)
  AND is_user_modified = FALSE;

-- =============================================================================
-- Step 2: Clean up dot-notation paths (legacy data that shouldn't exist)
-- =============================================================================
-- These are old paths using dot notation like "debtor.name" that don't match
-- any standard. They should be replaced with proper XPath.

-- First, let's see what we have
-- SELECT source_path FROM mapping.silver_field_mappings
-- WHERE format_id = 'pain.001' AND source_path LIKE '%.%';

-- Map common dot-notation paths to proper XPath for pain.001
UPDATE mapping.silver_field_mappings
SET source_path = CASE source_path
    -- Header mappings
    WHEN 'messageId' THEN 'CstmrCdtTrfInitn/GrpHdr/MsgId'
    WHEN 'creationDateTime' THEN 'CstmrCdtTrfInitn/GrpHdr/CreDtTm'
    WHEN 'numberOfTransactions' THEN 'CstmrCdtTrfInitn/GrpHdr/NbOfTxs'
    WHEN 'controlSum' THEN 'CstmrCdtTrfInitn/GrpHdr/CtrlSum'
    WHEN 'initiatingParty.name' THEN 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Nm'
    WHEN 'initiatingParty.id' THEN 'CstmrCdtTrfInitn/GrpHdr/InitgPty/Id'

    -- Payment Info
    WHEN 'paymentInformation.paymentInfoId' THEN 'CstmrCdtTrfInitn/PmtInf/PmtInfId'
    WHEN 'paymentMethod' THEN 'CstmrCdtTrfInitn/PmtInf/PmtMtd'
    WHEN 'batchBooking' THEN 'CstmrCdtTrfInitn/PmtInf/BtchBookg'
    WHEN 'requestedExecutionDate' THEN 'CstmrCdtTrfInitn/PmtInf/ReqdExctnDt'

    -- Debtor mappings
    WHEN 'debtor.name' THEN 'CstmrCdtTrfInitn/PmtInf/Dbtr/Nm'
    WHEN 'debtor.streetName' THEN 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/StrtNm'
    WHEN 'debtor.townName' THEN 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/TwnNm'
    WHEN 'debtor.postalCode' THEN 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/PstCd'
    WHEN 'debtor.country' THEN 'CstmrCdtTrfInitn/PmtInf/Dbtr/PstlAdr/Ctry'
    WHEN 'debtor.id' THEN 'CstmrCdtTrfInitn/PmtInf/Dbtr/Id'
    WHEN 'debtorAccount.iban' THEN 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/IBAN'
    WHEN 'debtorAccount.other' THEN 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Id/Othr/Id'
    WHEN 'debtorAccount.currency' THEN 'CstmrCdtTrfInitn/PmtInf/DbtrAcct/Ccy'
    WHEN 'debtorAgent.bic' THEN 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/BICFI'
    WHEN 'debtorAgent.name' THEN 'CstmrCdtTrfInitn/PmtInf/DbtrAgt/FinInstnId/Nm'

    -- Creditor mappings
    WHEN 'creditor.name' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Nm'
    WHEN 'creditor.streetName' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/StrtNm'
    WHEN 'creditor.townName' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/TwnNm'
    WHEN 'creditor.postalCode' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/PstCd'
    WHEN 'creditor.country' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/PstlAdr/Ctry'
    WHEN 'creditor.id' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Cdtr/Id'
    WHEN 'creditorAccount.iban' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/IBAN'
    WHEN 'creditorAccount.other' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Id/Othr/Id'
    WHEN 'creditorAccount.currency' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAcct/Ccy'
    WHEN 'creditorAgent.bic' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/BICFI'
    WHEN 'creditorAgent.name' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/CdtrAgt/FinInstnId/Nm'

    -- Amount
    WHEN 'instructedAmount' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt'
    WHEN 'instructedCurrency' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/InstdAmt/@Ccy'
    WHEN 'equivalentAmount' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Amt/EqvtAmt/Amt'
    WHEN 'exchangeRate' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/XchgRateInf/XchgRt'

    -- Transaction
    WHEN 'instructionId' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/InstrId'
    WHEN 'endToEndId' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/EndToEndId'
    WHEN 'uetr' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/PmtId/UETR'

    -- Purpose/Remittance
    WHEN 'purposeCode' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/Purp/Cd'
    WHEN 'chargeBearer' THEN 'CstmrCdtTrfInitn/PmtInf/ChrgBr'
    WHEN 'remittanceInformation.unstructured' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Ustrd'
    WHEN 'remittanceInformation.structured' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RmtInf/Strd'
    WHEN 'regulatoryReporting' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/RgltryRptg'

    -- Ultimate parties
    WHEN 'ultimateDebtor.name' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtDbtr/Nm'
    WHEN 'ultimateCreditor.name' THEN 'CstmrCdtTrfInitn/PmtInf/CdtTrfTxInf/UltmtCdtr/Nm'

    ELSE source_path -- Keep as-is if not in mapping
END
WHERE format_id = 'pain.001'
  AND source_path LIKE '%.%'  -- Only update dot-notation paths
  AND source_path NOT LIKE '%/%'  -- Not already XPath
  AND is_user_modified = FALSE;

-- =============================================================================
-- Step 3: Update MT103 paths to use standardized format
-- =============================================================================
-- MT103 uses SWIFT block structure. Paths should be like "Block4/Tag20"
-- to match standard_fields

UPDATE mapping.silver_field_mappings
SET source_path = CASE
    WHEN source_path = '20' THEN 'Block4/Tag20'
    WHEN source_path = '21' THEN 'Block4/Tag21'
    WHEN source_path = '23B' THEN 'Block4/Tag23B'
    WHEN source_path = '23E' THEN 'Block4/Tag23E'
    WHEN source_path = '32A' THEN 'Block4/Tag32A'
    WHEN source_path = '33B' THEN 'Block4/Tag33B'
    WHEN source_path = '36' THEN 'Block4/Tag36'
    WHEN source_path = '50A' THEN 'Block4/Tag50A'
    WHEN source_path = '50F' THEN 'Block4/Tag50F'
    WHEN source_path = '50K' THEN 'Block4/Tag50K'
    WHEN source_path = '52A' THEN 'Block4/Tag52A'
    WHEN source_path = '52D' THEN 'Block4/Tag52D'
    WHEN source_path = '53A' THEN 'Block4/Tag53A'
    WHEN source_path = '53B' THEN 'Block4/Tag53B'
    WHEN source_path = '53D' THEN 'Block4/Tag53D'
    WHEN source_path = '54A' THEN 'Block4/Tag54A'
    WHEN source_path = '54B' THEN 'Block4/Tag54B'
    WHEN source_path = '54D' THEN 'Block4/Tag54D'
    WHEN source_path = '55A' THEN 'Block4/Tag55A'
    WHEN source_path = '56A' THEN 'Block4/Tag56A'
    WHEN source_path = '56C' THEN 'Block4/Tag56C'
    WHEN source_path = '56D' THEN 'Block4/Tag56D'
    WHEN source_path = '57A' THEN 'Block4/Tag57A'
    WHEN source_path = '57B' THEN 'Block4/Tag57B'
    WHEN source_path = '57C' THEN 'Block4/Tag57C'
    WHEN source_path = '57D' THEN 'Block4/Tag57D'
    WHEN source_path = '59' THEN 'Block4/Tag59'
    WHEN source_path = '59A' THEN 'Block4/Tag59A'
    WHEN source_path = '59F' THEN 'Block4/Tag59F'
    WHEN source_path = '70' THEN 'Block4/Tag70'
    WHEN source_path = '71A' THEN 'Block4/Tag71A'
    WHEN source_path = '71F' THEN 'Block4/Tag71F'
    WHEN source_path = '71G' THEN 'Block4/Tag71G'
    WHEN source_path = '72' THEN 'Block4/Tag72'
    WHEN source_path = '77B' THEN 'Block4/Tag77B'
    WHEN source_path = '77T' THEN 'Block4/Tag77T'
    WHEN source_path LIKE 'block1.%' THEN 'Block1/' || REPLACE(source_path, 'block1.', '')
    WHEN source_path LIKE 'block2.%' THEN 'Block2/' || REPLACE(source_path, 'block2.', '')
    WHEN source_path LIKE 'block3.%' THEN 'Block3/' || REPLACE(source_path, 'block3.', '')
    ELSE source_path
END
WHERE format_id = 'MT103'
  AND source_path NOT LIKE 'Block%'  -- Not already in Block format
  AND is_user_modified = FALSE;

-- =============================================================================
-- Step 4: Update FEDWIRE paths to use standardized format
-- =============================================================================
-- FEDWIRE uses tag numbers like {1510}, {2000}. Paths should match standard_fields

UPDATE mapping.silver_field_mappings
SET source_path = CASE
    WHEN source_path = '{1510}' THEN 'TypeSubType/TypeCode'
    WHEN source_path = '{1520}' THEN 'MessageDisposition/IMAD'
    WHEN source_path = '{1530}' THEN 'MessageDisposition/OMAD'
    WHEN source_path = '{2000}' THEN 'Amount/Value'
    WHEN source_path = '{3100}' THEN 'Sender/RoutingNumber'
    WHEN source_path LIKE '{3100}.%' THEN 'Sender/' || REPLACE(source_path, '{3100}.', '')
    WHEN source_path = '{3400}' THEN 'Receiver/RoutingNumber'
    WHEN source_path LIKE '{3400}.%' THEN 'Receiver/' || REPLACE(source_path, '{3400}.', '')
    WHEN source_path = '{3320}' THEN 'SenderReference'
    WHEN source_path = '{3600}' THEN 'BusinessFunctionCode'
    WHEN source_path = '{3700}' THEN 'ChargeDetails'
    WHEN source_path = '{4000}' THEN 'Beneficiary/Name'
    WHEN source_path LIKE '{4000}.%' THEN 'Beneficiary/' || REPLACE(source_path, '{4000}.', '')
    WHEN source_path = '{4100}' THEN 'BeneficiaryFI/RoutingNumber'
    WHEN source_path LIKE '{4100}.%' THEN 'BeneficiaryFI/' || REPLACE(source_path, '{4100}.', '')
    WHEN source_path = '{4200}' THEN 'Beneficiary/Name'
    WHEN source_path LIKE '{4200}.%' THEN 'Beneficiary/' || REPLACE(source_path, '{4200}.', '')
    WHEN source_path = '{5000}' THEN 'Originator/Name'
    WHEN source_path LIKE '{5000}.%' THEN 'Originator/' || REPLACE(source_path, '{5000}.', '')
    WHEN source_path = '{5100}' THEN 'OriginatorFI/RoutingNumber'
    WHEN source_path LIKE '{5100}.%' THEN 'OriginatorFI/' || REPLACE(source_path, '{5100}.', '')
    WHEN source_path = '{5200}' THEN 'InstructingFI/RoutingNumber'
    WHEN source_path LIKE '{5200}.%' THEN 'InstructingFI/' || REPLACE(source_path, '{5200}.', '')
    WHEN source_path = '{6000}' THEN 'OriginatorToBeneficiaryInfo'
    WHEN source_path = '{6100}' THEN 'FIToFIInfo'
    WHEN source_path = '{6200}' THEN 'FIToFIInfo'
    ELSE source_path
END
WHERE format_id = 'FEDWIRE'
  AND source_path LIKE '{%'  -- Only update tag-style paths
  AND is_user_modified = FALSE;

-- =============================================================================
-- Step 5: Link silver_field_mappings to standard_fields via standard_field_id
-- =============================================================================
-- Now that paths are aligned, we can link them

UPDATE mapping.silver_field_mappings sm
SET standard_field_id = sf.standard_field_id
FROM mapping.standard_fields sf
WHERE sm.format_id = sf.format_id
  AND sm.source_path = sf.field_path
  AND sm.standard_field_id IS NULL;

-- =============================================================================
-- Step 6: Recreate the unified documentation view with better join logic
-- =============================================================================
DROP VIEW IF EXISTS mapping.v_mappings_documentation CASCADE;

CREATE OR REPLACE VIEW mapping.v_mappings_documentation AS
SELECT
    -- Standard/Format Info
    mf.standard_name,
    mf.country,
    mf.format_id AS message_format,
    mf.format_name AS message_format_description,
    mf.format_category,
    mf.governing_body,

    -- Standard Field Info
    sf.standard_field_id,
    sf.field_name AS standard_field_name,
    sf.field_description AS standard_field_description,
    sf.data_type AS standard_field_data_type,
    sf.allowed_values AS standard_field_allowed_values,
    sf.field_path AS standard_field_path,
    sf.field_tag AS standard_field_tag,
    sf.is_mandatory AS standard_field_mandatory,
    sf.field_category,

    -- Bronze Info
    mf.bronze_table,
    sf.field_path AS bronze_source_path,

    -- Silver Mapping Info
    sm.mapping_id AS silver_mapping_id,
    'silver.' || mf.silver_table AS silver_table,
    sm.target_column AS silver_column,
    sm.data_type AS silver_data_type,
    sm.max_length AS silver_max_length,
    sm.source_path AS silver_source_path,
    sm.transform_function AS silver_transform,
    sm.is_required AS silver_is_required,
    CASE WHEN sm.mapping_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_mapped_to_silver,

    -- Gold Mapping Info
    gm.mapping_id AS gold_mapping_id,
    'gold.' || gm.gold_table AS gold_table,
    gm.gold_column,
    gm.data_type AS gold_data_type,
    gm.entity_role AS gold_entity_role,
    gm.purpose_code AS gold_purpose_code,
    gm.source_expression AS gold_source_expression,
    gm.transform_expression AS gold_transform,
    CASE WHEN gm.mapping_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_mapped_to_gold,

    -- Metadata
    sf.is_active,
    GREATEST(
        COALESCE(sf.updated_at, '1970-01-01'),
        COALESCE(sm.updated_at, '1970-01-01'),
        COALESCE(gm.updated_at, '1970-01-01')
    ) AS last_updated

FROM mapping.message_formats mf
LEFT JOIN mapping.standard_fields sf
    ON mf.format_id = sf.format_id
    AND sf.is_active = TRUE
LEFT JOIN mapping.silver_field_mappings sm
    ON sf.format_id = sm.format_id
    AND (
        -- Primary join: use standard_field_id if available
        sm.standard_field_id = sf.standard_field_id
        -- Fallback: match on path
        OR sm.source_path = sf.field_path
    )
    AND sm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gm
    ON sm.format_id = gm.format_id
    AND sm.target_column = gm.source_expression
    AND gm.entity_role IS NULL  -- Main payment fields, not entity-specific
    AND gm.is_active = TRUE
WHERE mf.is_active = TRUE
ORDER BY mf.format_category, mf.format_id, sf.field_category, sf.field_name;

-- =============================================================================
-- Step 7: Recreate coverage view
-- =============================================================================
DROP VIEW IF EXISTS mapping.v_mapping_coverage CASCADE;

CREATE OR REPLACE VIEW mapping.v_mapping_coverage AS
SELECT
    mf.format_id,
    mf.format_name,
    mf.standard_name,
    mf.country,
    COUNT(DISTINCT sf.standard_field_id) AS total_standard_fields,
    COUNT(DISTINCT CASE WHEN sf.is_mandatory THEN sf.standard_field_id END) AS mandatory_fields,
    COUNT(DISTINCT sm.mapping_id) AS mapped_to_silver,
    COUNT(DISTINCT gm.mapping_id) AS mapped_to_gold,
    ROUND(
        COUNT(DISTINCT sm.mapping_id)::NUMERIC / NULLIF(COUNT(DISTINCT sf.standard_field_id), 0) * 100,
        1
    ) AS silver_coverage_pct,
    ROUND(
        COUNT(DISTINCT gm.mapping_id)::NUMERIC / NULLIF(COUNT(DISTINCT sm.mapping_id), 0) * 100,
        1
    ) AS gold_coverage_pct,
    COUNT(DISTINCT sf.standard_field_id) - COUNT(DISTINCT sm.mapping_id) AS unmapped_fields
FROM mapping.message_formats mf
LEFT JOIN mapping.standard_fields sf
    ON mf.format_id = sf.format_id
    AND sf.is_active = TRUE
LEFT JOIN mapping.silver_field_mappings sm
    ON sf.format_id = sm.format_id
    AND (sm.standard_field_id = sf.standard_field_id OR sm.source_path = sf.field_path)
    AND sm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gm
    ON sm.format_id = gm.format_id
    AND sm.target_column = gm.source_expression
    AND gm.entity_role IS NULL
    AND gm.is_active = TRUE
WHERE mf.is_active = TRUE
GROUP BY mf.format_id, mf.format_name, mf.standard_name, mf.country
ORDER BY mf.format_category, mf.format_id;

-- =============================================================================
-- Step 8: Recreate unmapped fields view
-- =============================================================================
DROP VIEW IF EXISTS mapping.v_unmapped_fields CASCADE;

CREATE OR REPLACE VIEW mapping.v_unmapped_fields AS
SELECT
    mf.format_id,
    mf.format_name,
    sf.field_name,
    sf.field_path,
    sf.field_description,
    sf.data_type,
    sf.is_mandatory,
    sf.field_category,
    'NOT_MAPPED_TO_SILVER' AS gap_type
FROM mapping.message_formats mf
JOIN mapping.standard_fields sf
    ON mf.format_id = sf.format_id
    AND sf.is_active = TRUE
LEFT JOIN mapping.silver_field_mappings sm
    ON sf.format_id = sm.format_id
    AND (sm.standard_field_id = sf.standard_field_id OR sm.source_path = sf.field_path)
    AND sm.is_active = TRUE
WHERE mf.is_active = TRUE
  AND sm.mapping_id IS NULL

UNION ALL

SELECT
    mf.format_id,
    mf.format_name,
    sm.target_column AS field_name,
    sm.source_path AS field_path,
    sm.field_description,
    sm.data_type,
    sm.is_required AS is_mandatory,
    NULL AS field_category,
    'NOT_MAPPED_TO_GOLD' AS gap_type
FROM mapping.message_formats mf
JOIN mapping.silver_field_mappings sm
    ON mf.format_id = sm.format_id
    AND sm.is_active = TRUE
LEFT JOIN mapping.gold_field_mappings gm
    ON sm.format_id = gm.format_id
    AND sm.target_column = gm.source_expression
    AND gm.entity_role IS NULL
    AND gm.is_active = TRUE
WHERE mf.is_active = TRUE
  AND gm.mapping_id IS NULL

ORDER BY format_id, gap_type, field_name;

-- =============================================================================
-- Verify the fix
-- =============================================================================
-- Check how many silver_field_mappings now have standard_field_id linked
-- SELECT format_id,
--        COUNT(*) as total,
--        COUNT(standard_field_id) as linked,
--        COUNT(*) - COUNT(standard_field_id) as unlinked
-- FROM mapping.silver_field_mappings
-- WHERE is_active = TRUE
-- GROUP BY format_id
-- ORDER BY format_id;
