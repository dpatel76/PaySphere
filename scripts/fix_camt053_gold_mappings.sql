-- Fix Silver→Gold coverage for camt.053 to 100%
-- Each silver column maps to at least one gold table

BEGIN;

-- Get starting ordinal position
DO $$
DECLARE
    v_ord INTEGER;
BEGIN
    SELECT COALESCE(MAX(ordinal_position), 0) + 1 INTO v_ord FROM mapping.gold_field_mappings WHERE format_id = 'camt.053';

    -- ========================================
    -- cdm_party mappings for DEBTOR (from transaction details)
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_dbtr_nm', 'DEBTOR', v_ord, true),
        ('camt.053', 'cdm_party', 'building_number', 'tx_dtls_rltd_pties_dbtr_pstl_adr_bldg_nb', 'DEBTOR', v_ord+1, true),
        ('camt.053', 'cdm_party', 'country', 'tx_dtls_rltd_pties_dbtr_pstl_adr_ctry', 'DEBTOR', v_ord+2, true),
        ('camt.053', 'cdm_party', 'post_code', 'tx_dtls_rltd_pties_dbtr_pstl_adr_pst_cd', 'DEBTOR', v_ord+3, true),
        ('camt.053', 'cdm_party', 'street_name', 'tx_dtls_rltd_pties_dbtr_pstl_adr_strt_nm', 'DEBTOR', v_ord+4, true),
        ('camt.053', 'cdm_party', 'town_name', 'tx_dtls_rltd_pties_dbtr_pstl_adr_twn_nm', 'DEBTOR', v_ord+5, true),
        ('camt.053', 'cdm_party', 'registration_number', 'tx_dtls_rltd_pties_dbtr_id_org_id_othr_id', 'DEBTOR', v_ord+6, true),
        ('camt.053', 'cdm_party', 'tax_id', 'tx_dtls_tax_dbtr_tax_id', 'DEBTOR', v_ord+7, true),
        ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'DEBTOR', v_ord+8, true),
        ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'DEBTOR', v_ord+9, true),
        ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'DEBTOR', v_ord+10, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 11;

    -- ========================================
    -- cdm_party mappings for CREDITOR
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_cdtr_nm', 'CREDITOR', v_ord, true),
        ('camt.053', 'cdm_party', 'building_number', 'tx_dtls_rltd_pties_cdtr_pstl_adr_bldg_nb', 'CREDITOR', v_ord+1, true),
        ('camt.053', 'cdm_party', 'country', 'tx_dtls_rltd_pties_cdtr_pstl_adr_ctry', 'CREDITOR', v_ord+2, true),
        ('camt.053', 'cdm_party', 'post_code', 'tx_dtls_rltd_pties_cdtr_pstl_adr_pst_cd', 'CREDITOR', v_ord+3, true),
        ('camt.053', 'cdm_party', 'street_name', 'tx_dtls_rltd_pties_cdtr_pstl_adr_strt_nm', 'CREDITOR', v_ord+4, true),
        ('camt.053', 'cdm_party', 'town_name', 'tx_dtls_rltd_pties_cdtr_pstl_adr_twn_nm', 'CREDITOR', v_ord+5, true),
        ('camt.053', 'cdm_party', 'tax_id', 'tx_dtls_tax_cdtr_tax_id', 'CREDITOR', v_ord+6, true),
        ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'CREDITOR', v_ord+7, true),
        ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'CREDITOR', v_ord+8, true),
        ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'CREDITOR', v_ord+9, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 10;

    -- ========================================
    -- cdm_party mappings for INITIATING_PARTY
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_initg_pty_nm', 'INITIATING_PARTY', v_ord, true),
        ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'INITIATING_PARTY', v_ord+1, true),
        ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'INITIATING_PARTY', v_ord+2, true),
        ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'INITIATING_PARTY', v_ord+3, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 4;

    -- ========================================
    -- cdm_party mappings for ULTIMATE_DEBTOR
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_ultmt_dbtr_nm', 'ULTIMATE_DEBTOR', v_ord, true),
        ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'ULTIMATE_DEBTOR', v_ord+1, true),
        ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'ULTIMATE_DEBTOR', v_ord+2, true),
        ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_DEBTOR', v_ord+3, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 4;

    -- ========================================
    -- cdm_party mappings for ULTIMATE_CREDITOR
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_party', 'name', 'tx_dtls_rltd_pties_ultmt_cdtr_nm', 'ULTIMATE_CREDITOR', v_ord, true),
        ('camt.053', 'cdm_party', 'party_type', '''ORGANISATION''', 'ULTIMATE_CREDITOR', v_ord+1, true),
        ('camt.053', 'cdm_party', 'source_message_type', '''camt.053''', 'ULTIMATE_CREDITOR', v_ord+2, true),
        ('camt.053', 'cdm_party', 'source_stg_id', 'stg_id', 'ULTIMATE_CREDITOR', v_ord+3, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 4;

    -- ========================================
    -- cdm_account mappings for DEBTOR account
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_account', 'iban', 'tx_dtls_rltd_pties_dbtr_acct_id_iban', 'DEBTOR', v_ord, true),
        ('camt.053', 'cdm_account', 'account_number', 'tx_dtls_rltd_pties_dbtr_acct_id_othr_id', 'DEBTOR', v_ord+1, true),
        ('camt.053', 'cdm_account', 'currency', 'tx_dtls_rltd_pties_dbtr_acct_ccy', 'DEBTOR', v_ord+2, true),
        ('camt.053', 'cdm_account', 'account_type', '''CACC''', 'DEBTOR', v_ord+3, true),
        ('camt.053', 'cdm_account', 'source_message_type', '''camt.053''', 'DEBTOR', v_ord+4, true),
        ('camt.053', 'cdm_account', 'source_stg_id', 'stg_id', 'DEBTOR', v_ord+5, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 6;

    -- ========================================
    -- cdm_account mappings for CREDITOR account
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_account', 'iban', 'tx_dtls_rltd_pties_cdtr_acct_id_iban', 'CREDITOR', v_ord, true),
        ('camt.053', 'cdm_account', 'account_number', 'tx_dtls_rltd_pties_cdtr_acct_id_othr_id', 'CREDITOR', v_ord+1, true),
        ('camt.053', 'cdm_account', 'currency', 'tx_dtls_rltd_pties_cdtr_acct_ccy', 'CREDITOR', v_ord+2, true),
        ('camt.053', 'cdm_account', 'account_type', '''CACC''', 'CREDITOR', v_ord+3, true),
        ('camt.053', 'cdm_account', 'source_message_type', '''camt.053''', 'CREDITOR', v_ord+4, true),
        ('camt.053', 'cdm_account', 'source_stg_id', 'stg_id', 'CREDITOR', v_ord+5, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 6;

    -- ========================================
    -- cdm_financial_institution for DEBTOR_AGENT
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_bicfi', 'DEBTOR_AGENT', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'institution_name', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_nm', 'DEBTOR_AGENT', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'lei', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_lei', 'DEBTOR_AGENT', v_ord+2, true),
        ('camt.053', 'cdm_financial_institution', 'national_clearing_code', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'DEBTOR_AGENT', v_ord+3, true),
        ('camt.053', 'cdm_financial_institution', 'country', 'tx_dtls_rltd_agts_dbtr_agt_fin_instn_id_pstl_adr_ctry', 'DEBTOR_AGENT', v_ord+4, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'DEBTOR_AGENT', v_ord+5, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'DEBTOR_AGENT', v_ord+6, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 7;

    -- ========================================
    -- cdm_financial_institution for CREDITOR_AGENT
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_bicfi', 'CREDITOR_AGENT', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'institution_name', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_nm', 'CREDITOR_AGENT', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'lei', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_lei', 'CREDITOR_AGENT', v_ord+2, true),
        ('camt.053', 'cdm_financial_institution', 'national_clearing_code', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_clr_sys_mmb_id_mmb_id', 'CREDITOR_AGENT', v_ord+3, true),
        ('camt.053', 'cdm_financial_institution', 'country', 'tx_dtls_rltd_agts_cdtr_agt_fin_instn_id_pstl_adr_ctry', 'CREDITOR_AGENT', v_ord+4, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'CREDITOR_AGENT', v_ord+5, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'CREDITOR_AGENT', v_ord+6, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 7;

    -- ========================================
    -- cdm_financial_institution for INTERMEDIARY_AGENT1
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_intrmy_agt1_fin_instn_id_bicfi', 'INTERMEDIARY_AGENT1', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'INTERMEDIARY_AGENT1', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT1', v_ord+2, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 3;

    -- ========================================
    -- cdm_financial_institution for INTERMEDIARY_AGENT2
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_intrmy_agt2_fin_instn_id_bicfi', 'INTERMEDIARY_AGENT2', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'INTERMEDIARY_AGENT2', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT2', v_ord+2, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 3;

    -- ========================================
    -- cdm_financial_institution for INTERMEDIARY_AGENT3
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_intrmy_agt3_fin_instn_id_bicfi', 'INTERMEDIARY_AGENT3', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'INTERMEDIARY_AGENT3', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'INTERMEDIARY_AGENT3', v_ord+2, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 3;

    -- ========================================
    -- cdm_financial_institution for DELIVERING_AGENT
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_dlvrg_agt_fin_instn_id_bicfi', 'DELIVERING_AGENT', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'DELIVERING_AGENT', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'DELIVERING_AGENT', v_ord+2, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 3;

    -- ========================================
    -- cdm_financial_institution for RECEIVING_AGENT
    -- ========================================
    INSERT INTO mapping.gold_field_mappings (format_id, gold_table, gold_column, source_expression, entity_role, ordinal_position, is_active)
    VALUES
        ('camt.053', 'cdm_financial_institution', 'bic', 'tx_dtls_rltd_agts_rcvg_agt_fin_instn_id_bicfi', 'RECEIVING_AGENT', v_ord, true),
        ('camt.053', 'cdm_financial_institution', 'source_system', '''camt.053''', 'RECEIVING_AGENT', v_ord+1, true),
        ('camt.053', 'cdm_financial_institution', 'is_current', 'true', 'RECEIVING_AGENT', v_ord+2, true)
    ON CONFLICT DO NOTHING;

    v_ord := v_ord + 3;

END $$;

COMMIT;
