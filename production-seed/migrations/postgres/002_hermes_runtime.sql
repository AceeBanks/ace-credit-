-- G0-FINAL-REPAIR-01 — Postgres Hermes runtime tables (production).
-- Mirror of migrations/002_hermes_runtime.sql with Postgres primitives.
-- Append-only; never edit an applied migration.

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id      TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    client_actor_id      TEXT NOT NULL,
    title                TEXT,
    project_id           TEXT REFERENCES application_projects(project_id),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS messages (
    message_id           TEXT PRIMARY KEY,
    conversation_id      TEXT NOT NULL REFERENCES conversations(conversation_id),
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    role                 TEXT NOT NULL,
    content              TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS intents (
    intent_id            TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    client_actor_id      TEXT NOT NULL,
    organization_id      TEXT NOT NULL REFERENCES organizations(organization_id),
    intent_type          TEXT NOT NULL,
    objective            TEXT NOT NULL,
    authority_scope      TEXT NOT NULL,
    confidence_state     TEXT NOT NULL,
    version              INTEGER NOT NULL DEFAULT 1,
    supersedes_intent_id TEXT,
    source_conversation_ref TEXT,
    payload              JSONB,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS task_plans (
    plan_id              TEXT PRIMARY KEY,
    intent_id            TEXT NOT NULL REFERENCES intents(intent_id),
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT REFERENCES application_projects(project_id),
    opportunity_revision_id TEXT REFERENCES opportunity_revisions(revision_id),
    objective            TEXT NOT NULL,
    steps                JSONB,
    state                TEXT NOT NULL DEFAULT 'PLANNED',
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS worker_results (
    result_id            TEXT PRIMARY KEY,
    task_id              TEXT NOT NULL REFERENCES tasks(task_id),
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    worker_principal     TEXT NOT NULL,
    capability_id        TEXT NOT NULL,
    summary              TEXT NOT NULL,
    claims               JSONB,
    context_refs         JSONB,
    model_ref            TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_intents_tenant ON intents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_intents_org ON intents(organization_id);
CREATE INDEX IF NOT EXISTS idx_worker_results_task ON worker_results(task_id);
CREATE INDEX IF NOT EXISTS idx_worker_results_tenant ON worker_results(tenant_id);
