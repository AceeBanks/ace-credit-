-- G0-FINAL-REPAIR-01 — Production Postgres migration (canonical).
--
-- Postgres is the canonical production database. This file is the
-- production migration path; the SQLite files under migrations/ are
-- TEST_ONLY / DEV_FAST_PATH and are NOT evidence that this SQL works.
--
-- Semantics mirror the domain contracts from Books 2–6:
--   * IDs stay provider-independent strings (G0 domain contract);
--   * created_at is TIMESTAMPTZ DEFAULT now();
--   * FK integrity enforced;
--   * revision semantics are append-only at the application layer
--     (new rows, never mutation of prior revision rows);
--   * JSON payloads stored as jsonb for audit/decision payloads.
--
-- Migrations are append-only; never edit an applied migration.

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id            TEXT PRIMARY KEY,
    display_name         TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    user_id              TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    display_name         TEXT NOT NULL,
    email                TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS principals (
    principal_id         TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    principal_type       TEXT NOT NULL
        CHECK (principal_type IN
               ('USER','SERVICE','HERMES_PERSONAL','HERMES_CEO','WORKER')),
    authority_level      INTEGER NOT NULL DEFAULT 1,
    user_id              TEXT REFERENCES users(user_id),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS capabilities (
    capability_id        TEXT PRIMARY KEY,
    required_level       INTEGER NOT NULL,
    description          TEXT,
    delegable            BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS grants (
    grant_id             TEXT PRIMARY KEY,
    principal_id         TEXT NOT NULL REFERENCES principals(principal_id),
    capability_id        TEXT NOT NULL REFERENCES capabilities(capability_id),
    authority_level      INTEGER NOT NULL,
    tenant_id            TEXT,
    project_id           TEXT,
    resource_id          TEXT,
    expires_at           TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
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
    status               TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING','GRANTED','REVOKED','EXPIRED')),
    expires_at           TIMESTAMPTZ,
    decision_ref         TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS organizations (
    organization_id      TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    legal_name           TEXT NOT NULL,
    jurisdiction         TEXT,
    ein                  TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id       TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    title                TEXT NOT NULL,
    funding_ceiling      NUMERIC(14,2),
    deadline             DATE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS opportunity_revisions (
    revision_id          TEXT PRIMARY KEY,
    opportunity_id       TEXT NOT NULL REFERENCES opportunities(opportunity_id),
    revision_number      INTEGER NOT NULL,
    changed_terms        JSONB,
    material             BOOLEAN NOT NULL DEFAULT FALSE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- append-only: revision numbers are unique per opportunity and only
    -- ever increase; application layer never mutates a prior revision row
    UNIQUE (opportunity_id, revision_number)
);

CREATE TABLE IF NOT EXISTS application_projects (
    project_id           TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    organization_id      TEXT NOT NULL REFERENCES organizations(organization_id),
    opportunity_id       TEXT NOT NULL REFERENCES opportunities(opportunity_id),
    revision_id          TEXT NOT NULL REFERENCES opportunity_revisions(revision_id),
    state                TEXT NOT NULL DEFAULT 'DRAFTING'
        CHECK (state IN ('DRAFTING','QA','READY_MOCK','BLOCKED')),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS requirements (
    requirement_id       TEXT PRIMARY KEY,
    opportunity_revision_id TEXT NOT NULL
        REFERENCES opportunity_revisions(revision_id),
    requirement_type     TEXT NOT NULL,
    mandatory            BOOLEAN NOT NULL DEFAULT TRUE,
    prompt               TEXT,
    word_limit           INTEGER,
    state                TEXT NOT NULL DEFAULT 'IDENTIFIED'
);

CREATE TABLE IF NOT EXISTS source_snapshots (
    snapshot_id          TEXT PRIMARY KEY,
    source_uri           TEXT NOT NULL,
    fetched_at           TIMESTAMPTZ NOT NULL,
    content_hash         TEXT NOT NULL,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    revision_id          TEXT REFERENCES opportunity_revisions(revision_id),
    payload_ref          TEXT,            -- object storage ref (immutable payload)
    UNIQUE (content_hash, tenant_id)      -- immutable snapshots: same content
);                                        -- is idempotent, never re-inserted

CREATE TABLE IF NOT EXISTS decision_records (
    decision_id          TEXT PRIMARY KEY,
    decision_type        TEXT NOT NULL,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    actor_ref            TEXT NOT NULL,
    capability_id        TEXT NOT NULL,
    input_refs           JSONB,
    policy_ref           TEXT,
    result               JSONB,
    explanation_data     JSONB,
    model_or_engine_ref  TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
    audit_id             TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    actor_ref            TEXT NOT NULL,
    event_type           TEXT NOT NULL,
    decision_ref         TEXT REFERENCES decision_records(decision_id),
    payload_ref          TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id          TEXT PRIMARY KEY,
    artifact_version_id  TEXT NOT NULL,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    kind                 TEXT NOT NULL,
    payload_ref          TEXT NOT NULL,
    content_hash         TEXT NOT NULL,
    version_number       INTEGER NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id              TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    task_type            TEXT NOT NULL,
    state                TEXT NOT NULL DEFAULT 'ACCEPTED'
        CHECK (state IN ('ACCEPTED','PENDING','READY','RUNNING','BLOCKED',
                         'SUCCEEDED','FAILED','CANCELLED','STALE')),
    worker_principal     TEXT,
    capability_id        TEXT,
    result_ref           TEXT,
    retry_count          INTEGER NOT NULL DEFAULT 0,
    lease_until          TIMESTAMPTZ,
    failure_reason       TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_grants_principal ON grants(principal_id);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_decisions_tenant ON decision_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
