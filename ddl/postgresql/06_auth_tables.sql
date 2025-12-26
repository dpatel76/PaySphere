-- GPS CDM - Authentication and RBAC Tables
-- Based on SynapseDTE2 patterns

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SCHEMA
-- ============================================================================
CREATE SCHEMA IF NOT EXISTS auth;

-- ============================================================================
-- PERMISSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.permissions (
    permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    resource VARCHAR(100) NOT NULL,  -- e.g., 'exceptions', 'dq', 'pipeline'
    action VARCHAR(50) NOT NULL,     -- e.g., 'read', 'write', 'delete', 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ROLES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.roles (
    role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ROLE_PERMISSIONS (Many-to-Many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.role_permissions (
    role_id UUID NOT NULL REFERENCES auth.roles(role_id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES auth.permissions(permission_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- USER_ROLES (Many-to-Many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.user_roles (
    user_id UUID NOT NULL REFERENCES auth.users(user_id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES auth.roles(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES auth.users(user_id),
    PRIMARY KEY (user_id, role_id)
);

-- ============================================================================
-- REFRESH TOKENS TABLE (for JWT refresh)
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.refresh_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS auth.audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(user_id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON auth.users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON auth.users(is_active);
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON auth.user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON auth.user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON auth.refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON auth.refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON auth.audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON auth.audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON auth.audit_log(created_at);

-- ============================================================================
-- SEED DATA: Default Permissions
-- ============================================================================
INSERT INTO auth.permissions (name, description, resource, action) VALUES
    -- Pipeline permissions
    ('pipeline:read', 'View pipeline status and batches', 'pipeline', 'read'),
    ('pipeline:write', 'Trigger pipeline operations', 'pipeline', 'write'),
    ('pipeline:admin', 'Administer pipeline configuration', 'pipeline', 'admin'),

    -- Exception permissions
    ('exceptions:read', 'View exceptions', 'exceptions', 'read'),
    ('exceptions:write', 'Acknowledge and resolve exceptions', 'exceptions', 'write'),
    ('exceptions:admin', 'Delete and bulk manage exceptions', 'exceptions', 'admin'),

    -- Data Quality permissions
    ('dq:read', 'View DQ metrics and results', 'dq', 'read'),
    ('dq:write', 'Run DQ validations', 'dq', 'write'),
    ('dq:admin', 'Manage DQ rules', 'dq', 'admin'),

    -- Reconciliation permissions
    ('recon:read', 'View reconciliation results', 'recon', 'read'),
    ('recon:write', 'Run reconciliation', 'recon', 'write'),
    ('recon:admin', 'Resolve reconciliation issues', 'recon', 'admin'),

    -- Reprocess permissions
    ('reprocess:read', 'View stuck records', 'reprocess', 'read'),
    ('reprocess:write', 'Reprocess records', 'reprocess', 'write'),
    ('reprocess:admin', 'Force reprocess and update records', 'reprocess', 'admin'),

    -- Lineage permissions
    ('lineage:read', 'View data lineage', 'lineage', 'read'),
    ('lineage:write', 'Persist lineage data', 'lineage', 'write'),

    -- User management permissions
    ('users:read', 'View users', 'users', 'read'),
    ('users:write', 'Create and update users', 'users', 'write'),
    ('users:admin', 'Delete users and manage roles', 'users', 'admin')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- SEED DATA: Default Roles
-- ============================================================================
INSERT INTO auth.roles (name, description, is_system_role) VALUES
    ('admin', 'System administrator with full access', TRUE),
    ('operator', 'Operations team - can manage pipeline and exceptions', TRUE),
    ('analyst', 'Data analyst - read-only access to all data', TRUE),
    ('viewer', 'Read-only access to dashboards', TRUE)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- SEED DATA: Role-Permission Mappings
-- ============================================================================
-- Admin role gets all permissions
INSERT INTO auth.role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM auth.roles r, auth.permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- Operator role permissions
INSERT INTO auth.role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM auth.roles r, auth.permissions p
WHERE r.name = 'operator'
  AND p.name IN (
    'pipeline:read', 'pipeline:write',
    'exceptions:read', 'exceptions:write',
    'dq:read', 'dq:write',
    'recon:read', 'recon:write',
    'reprocess:read', 'reprocess:write',
    'lineage:read'
  )
ON CONFLICT DO NOTHING;

-- Analyst role permissions
INSERT INTO auth.role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM auth.roles r, auth.permissions p
WHERE r.name = 'analyst'
  AND p.name IN (
    'pipeline:read',
    'exceptions:read',
    'dq:read',
    'recon:read',
    'reprocess:read',
    'lineage:read'
  )
ON CONFLICT DO NOTHING;

-- Viewer role permissions
INSERT INTO auth.role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM auth.roles r, auth.permissions p
WHERE r.name = 'viewer'
  AND p.name IN ('pipeline:read', 'lineage:read')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- SEED DATA: Default Admin User (password: admin123)
-- Password hash for 'admin123' using bcrypt
-- ============================================================================
INSERT INTO auth.users (email, username, password_hash, first_name, last_name, is_active, is_superuser)
VALUES (
    'admin@gpscdm.local',
    'admin',
    '$2b$12$wzI3d71Z.BCllCV5d40VBucVNVo4ASK1hr6PnEuA3ZgtnN1Q34uJC',  -- admin123
    'System',
    'Administrator',
    TRUE,
    TRUE
)
ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash;

-- Assign admin role to admin user
INSERT INTO auth.user_roles (user_id, role_id)
SELECT u.user_id, r.role_id
FROM auth.users u, auth.roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to check if a user has a specific permission
CREATE OR REPLACE FUNCTION auth.user_has_permission(
    p_user_id UUID,
    p_permission_name VARCHAR
) RETURNS BOOLEAN AS $$
BEGIN
    -- Superusers have all permissions
    IF EXISTS (SELECT 1 FROM auth.users WHERE user_id = p_user_id AND is_superuser = TRUE) THEN
        RETURN TRUE;
    END IF;

    -- Check role-based permissions
    RETURN EXISTS (
        SELECT 1
        FROM auth.user_roles ur
        JOIN auth.role_permissions rp ON ur.role_id = rp.role_id
        JOIN auth.permissions p ON rp.permission_id = p.permission_id
        WHERE ur.user_id = p_user_id AND p.name = p_permission_name
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get all permissions for a user
CREATE OR REPLACE FUNCTION auth.get_user_permissions(p_user_id UUID)
RETURNS TABLE (permission_name VARCHAR, resource VARCHAR, action VARCHAR) AS $$
BEGIN
    -- If superuser, return all permissions
    IF EXISTS (SELECT 1 FROM auth.users WHERE user_id = p_user_id AND is_superuser = TRUE) THEN
        RETURN QUERY SELECT p.name, p.resource, p.action FROM auth.permissions p;
    ELSE
        RETURN QUERY
        SELECT DISTINCT p.name, p.resource, p.action
        FROM auth.user_roles ur
        JOIN auth.role_permissions rp ON ur.role_id = rp.role_id
        JOIN auth.permissions p ON rp.permission_id = p.permission_id
        WHERE ur.user_id = p_user_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMIT;
