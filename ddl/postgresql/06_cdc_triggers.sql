-- GPS CDM - CDC (Change Data Capture) Triggers
-- ==============================================
-- Trigger-based CDC for PostgreSQL to capture changes for downstream sync (Neo4j, etc.)

-- Create CDC trigger function
CREATE OR REPLACE FUNCTION observability.cdc_capture_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changed_fields TEXT[];
    v_record_id VARCHAR(100);
    v_batch_id VARCHAR(36);
BEGIN
    -- Convert record to JSONB first, then extract ID
    IF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_changed_fields := NULL;
        v_batch_id := NULL;
        -- Extract record ID from JSONB
        v_record_id := COALESCE(
            v_old_data->>'instruction_id',
            v_old_data->>'party_id',
            v_old_data->>'account_id',
            v_old_data->>'fi_id',
            v_old_data->>'stg_id',
            v_old_data->>'raw_id',
            gen_random_uuid()::TEXT
        );
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        -- Extract record ID from JSONB
        v_record_id := COALESCE(
            v_new_data->>'instruction_id',
            v_new_data->>'party_id',
            v_new_data->>'account_id',
            v_new_data->>'fi_id',
            v_new_data->>'stg_id',
            v_new_data->>'raw_id',
            gen_random_uuid()::TEXT
        );
        -- Calculate changed fields as TEXT array
        SELECT ARRAY_AGG(key)
        INTO v_changed_fields
        FROM jsonb_each(v_new_data) new_vals
        WHERE v_old_data->key IS DISTINCT FROM value;
        -- Get batch_id if available
        v_batch_id := COALESCE(v_new_data->>'lineage_batch_id', v_new_data->>'_batch_id');
    ELSIF TG_OP = 'INSERT' THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        -- Extract record ID from JSONB
        v_record_id := COALESCE(
            v_new_data->>'instruction_id',
            v_new_data->>'party_id',
            v_new_data->>'account_id',
            v_new_data->>'fi_id',
            v_new_data->>'stg_id',
            v_new_data->>'raw_id',
            gen_random_uuid()::TEXT
        );
        -- All fields are new
        SELECT ARRAY_AGG(key)
        INTO v_changed_fields
        FROM jsonb_each(v_new_data);
        -- Get batch_id if available
        v_batch_id := COALESCE(v_new_data->>'lineage_batch_id', v_new_data->>'_batch_id');
    END IF;

    -- Insert into CDC tracking table (matching actual schema)
    INSERT INTO observability.obs_cdc_tracking (
        cdc_id,
        layer,
        table_name,
        record_id,
        operation,
        old_data,
        new_data,
        changed_fields,
        change_timestamp,
        batch_id,
        sync_status,
        synced_to,
        sync_attempt_count
    ) VALUES (
        gen_random_uuid()::TEXT,
        CASE
            WHEN TG_TABLE_SCHEMA = 'bronze' THEN 'bronze'
            WHEN TG_TABLE_SCHEMA = 'silver' THEN 'silver'
            WHEN TG_TABLE_SCHEMA = 'gold' THEN 'gold'
            WHEN TG_TABLE_SCHEMA = 'analytical' THEN 'analytical'
            ELSE TG_TABLE_SCHEMA
        END,
        TG_TABLE_NAME,
        v_record_id,
        TG_OP,
        v_old_data,
        v_new_data,
        v_changed_fields,
        CURRENT_TIMESTAMP,
        v_batch_id,
        'PENDING',
        ARRAY[]::TEXT[],
        0
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
EXCEPTION WHEN OTHERS THEN
    -- Log error but don't fail the transaction
    RAISE WARNING 'CDC trigger error: %', SQLERRM;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for Gold layer tables (most important for downstream sync)
DROP TRIGGER IF EXISTS cdc_payment_instruction ON gold.cdm_payment_instruction;
CREATE TRIGGER cdc_payment_instruction
    AFTER INSERT OR UPDATE OR DELETE ON gold.cdm_payment_instruction
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

DROP TRIGGER IF EXISTS cdc_party ON gold.cdm_party;
CREATE TRIGGER cdc_party
    AFTER INSERT OR UPDATE OR DELETE ON gold.cdm_party
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

DROP TRIGGER IF EXISTS cdc_account ON gold.cdm_account;
CREATE TRIGGER cdc_account
    AFTER INSERT OR UPDATE OR DELETE ON gold.cdm_account
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

DROP TRIGGER IF EXISTS cdc_financial_institution ON gold.cdm_financial_institution;
CREATE TRIGGER cdc_financial_institution
    AFTER INSERT OR UPDATE OR DELETE ON gold.cdm_financial_institution
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

DROP TRIGGER IF EXISTS cdc_charge ON gold.cdm_charge;
CREATE TRIGGER cdc_charge
    AFTER INSERT OR UPDATE OR DELETE ON gold.cdm_charge
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

-- Create triggers for Silver layer tables (optional - for lineage tracking)
DROP TRIGGER IF EXISTS cdc_stg_pain001 ON silver.stg_pain001;
CREATE TRIGGER cdc_stg_pain001
    AFTER INSERT OR UPDATE OR DELETE ON silver.stg_pain001
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

DROP TRIGGER IF EXISTS cdc_stg_mt103 ON silver.stg_mt103;
CREATE TRIGGER cdc_stg_mt103
    AFTER INSERT OR UPDATE OR DELETE ON silver.stg_mt103
    FOR EACH ROW EXECUTE FUNCTION observability.cdc_capture_changes();

-- Index for efficient CDC polling
CREATE INDEX IF NOT EXISTS idx_cdc_pending_change
    ON observability.obs_cdc_tracking(sync_status, change_timestamp)
    WHERE sync_status = 'PENDING';

CREATE INDEX IF NOT EXISTS idx_cdc_table_change
    ON observability.obs_cdc_tracking(table_name, change_timestamp);

-- Function to get pending CDC events for sync
CREATE OR REPLACE FUNCTION observability.get_pending_cdc_events(
    p_target_system VARCHAR(100) DEFAULT NULL,
    p_limit INT DEFAULT 1000
)
RETURNS TABLE (
    cdc_id VARCHAR(36),
    layer VARCHAR(20),
    table_name VARCHAR(100),
    record_id VARCHAR(100),
    operation VARCHAR(10),
    new_data JSONB,
    changed_fields TEXT[],
    change_timestamp TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.cdc_id,
        c.layer,
        c.table_name,
        c.record_id,
        c.operation,
        c.new_data,
        c.changed_fields,
        c.change_timestamp
    FROM observability.obs_cdc_tracking c
    WHERE c.sync_status = 'PENDING'
      AND (p_target_system IS NULL OR NOT (p_target_system = ANY(c.synced_to)))
    ORDER BY c.change_timestamp
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to mark CDC events as synced
CREATE OR REPLACE FUNCTION observability.mark_cdc_synced(
    p_cdc_ids TEXT[],
    p_target_system VARCHAR(100)
)
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    UPDATE observability.obs_cdc_tracking
    SET
        synced_to = array_append(COALESCE(synced_to, ARRAY[]::TEXT[]), p_target_system),
        sync_status = 'SYNCED',
        last_sync_attempt = CURRENT_TIMESTAMP
    WHERE cdc_id = ANY(p_cdc_ids);

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION observability.cdc_capture_changes() IS 'Trigger function to capture changes for CDC';
COMMENT ON FUNCTION observability.get_pending_cdc_events(VARCHAR, INT) IS 'Get pending CDC events for downstream sync';
COMMENT ON FUNCTION observability.mark_cdc_synced(TEXT[], VARCHAR) IS 'Mark CDC events as synced to a target system';
