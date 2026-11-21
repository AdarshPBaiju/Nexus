-- ==============================================================================
-- Project Nexus PostgreSQL 16 Regional Cell Database Initialization
-- Forced RLS Tenant Isolation & Performance Primitives (PNX-REPO-ARCH-004 §5)
-- ==============================================================================

-- 1. Mandatory Core Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Create Application Non-Superuser Role (Strictly NOBYPASSRLS)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'nexus_app_rw') THEN
        CREATE ROLE nexus_app_rw WITH LOGIN PASSWORD 'nexus_dev_password' NOBYPASSRLS;
    END IF;
END
$$;

-- 3. Schema Permissions
GRANT CONNECT ON DATABASE nexus_regional TO nexus_app_rw;
GRANT USAGE, CREATE ON SCHEMA public TO nexus_app_rw;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nexus_app_rw;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nexus_app_rw;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO nexus_app_rw;

-- 4. Default Future Object Privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO nexus_app_rw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO nexus_app_rw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO nexus_app_rw;

-- 5. Set session parameter search path
ALTER ROLE nexus_app_rw SET search_path TO public;
