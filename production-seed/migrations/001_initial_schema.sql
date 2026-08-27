-- G0-B9-C13 — Initial Database / Migration Seed
-- Canonical tables from Books 2–6 contracts (C7 ownership matrix).
-- Portable SQL: TEXT primary keys (G0 contracts use string ids), no
-- server-specific types, so the same file runs from an EMPTY database in
-- CI (sqlite) and Postgres. JSON payloads stored as TEXT.
-- Migrations are append-only; never edit an applied migration.

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id            TEXT PRIMARY KEY,
    display_name         TEXT NOT NULL,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS users (
    user_id              TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    display_name         TEXT NOT NULL,
    email                TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS principals (
    principal_id         TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    principal_type       TEXT NOT NULL,   -- USER | SERVICE | HERMES_PERSONAL | HERMES_CEO | WORKER
    authority_level      INTEGER NOT NULL DEFAULT 1,
    user_id              TEXT REFERENCES users(user_id),
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS capabilities (
    capability_id        TEXT PRIMARY KEY,
    required_level       INTEGER NOT NULL,
    description          TEXT,
    delegable            INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS grants (
    grant_id             TEXT PRIMARY KEY,
    principal_id         TEXT NOT NULL REFERENCES principals(principal_id),
    capability_id        TEXT NOT NULL REFERENCES capabilities(capability_id),
    authority_level      INTEGER NOT NULL,
    tenant_id            TEXT,
    project_id           TEXT,
    resource_id          TEXT,
    expires_at           TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id          TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL,
    project_id           TEXT,
    capability_id        TEXT NOT NULL,
    resource_id          TEXT NOT NULL,
    resource_version     TEXT,
    action               TEXT NOT NULL,
    approval_class       TEXT NOT NULL,
    status               TEXT NOT NULL DEFAULT 'PENDING',  -- PENDING | GRANTED | REVOKED | EXPIRED
    expires_at           TEXT,
    decision_ref         TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS organizations (
    organization_id      TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    legal_name           TEXT NOT NULL,
    jurisdiction         TEXT,
    ein                  TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id       TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    title                TEXT NOT NULL,
    funding_ceiling      TEXT,
    deadline             TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS opportunity_revisions (
    revision_id          TEXT PRIMARY KEY,
    opportunity_id       TEXT NOT NULL REFERENCES opportunities(opportunity_id),
    revision_number      INTEGER NOT NULL,
    changed_terms        TEXT,          -- JSON array
    material             INTEGER NOT NULL DEFAULT 0,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS application_projects (
    project_id           TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    organization_id      TEXT NOT NULL REFERENCES organizations(organization_id),
    opportunity_id       TEXT NOT NULL REFERENCES opportunities(opportunity_id),
    revision_id          TEXT NOT NULL REFERENCES opportunity_revisions(revision_id),
    state                TEXT NOT NULL DEFAULT 'DRAFTING',
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS requirements (
    requirement_id       TEXT PRIMARY KEY,
    opportunity_revision_id TEXT NOT NULL REFERENCES opportunity_revisions(revision_id),
    requirement_type     TEXT NOT NULL,
    mandatory            INTEGER NOT NULL DEFAULT 1,
    prompt               TEXT,
    word_limit           INTEGER,
    state                TEXT NOT NULL DEFAULT 'IDENTIFIED'
);

CREATE TABLE IF NOT EXISTS source_snapshots (
    snapshot_id          TEXT PRIMARY KEY,
    source_uri           TEXT NOT NULL,
    fetched_at           TEXT NOT NULL,
    content_hash         TEXT NOT NULL,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    revision_id          TEXT REFERENCES opportunity_revisions(revision_id),
    payload_ref          TEXT            -- object storage ref (immutable payload)
);

CREATE TABLE IF NOT EXISTS decision_records (
    decision_id          TEXT PRIMARY KEY,
    decision_type        TEXT NOT NULL,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    actor_ref            TEXT NOT NULL,
    capability_id        TEXT NOT NULL,
    input_refs           TEXT,           -- JSON array of DecisionInputRef
    policy_ref           TEXT,
    result               TEXT,           -- JSON
    explanation_data     TEXT,
    model_or_engine_ref  TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS audit_events (
    audit_id             TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    actor_ref            TEXT NOT NULL,
    event_type           TEXT NOT NULL,
    decision_ref         TEXT REFERENCES decision_records(decision_id),
    payload_ref          TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id          TEXT PRIMARY KEY,
    artifact_version_id  TEXT NOT NULL,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    kind                 TEXT NOT NULL,  -- draft | budget | snapshot | evidence
    payload_ref          TEXT NOT NULL,  -- object storage ref
    content_hash         TEXT NOT NULL,
    version_number       INTEGER NOT NULL,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id              TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    task_type            TEXT NOT NULL,
    state                TEXT NOT NULL DEFAULT 'ACCEPTED',  -- ACCEPTED | RUNNING | COMPLETED | FAILED
    worker_principal     TEXT,
    capability_id        TEXT,
    result_ref           TEXT,
    retry_count          INTEGER NOT NULL DEFAULT 0,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_grants_principal ON grants(principal_id);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_decisions_tenant ON decision_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
