-- G1 Wave 3 — Production Dual Hermes runtime tables.
-- Append-only migration (never edit an applied migration).
-- Personal Hermes owns conversations + intents; CEO Hermes owns plans/tasks;
-- workers write WorkerResults. Workflow truth lives here, not in Hermes
-- memory (Book 8 reconstruction law). All rows are tenant-scoped.

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id      TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    client_actor_id      TEXT NOT NULL,
    title                TEXT,
    project_id           TEXT REFERENCES application_projects(project_id),
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS messages (
    message_id           TEXT PRIMARY KEY,
    conversation_id      TEXT NOT NULL REFERENCES conversations(conversation_id),
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    role                 TEXT NOT NULL,   -- user | personal_hermes
    content              TEXT NOT NULL,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
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
    payload              TEXT,           -- JSON: full IntentContract payload
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS task_plans (
    plan_id              TEXT PRIMARY KEY,
    intent_id            TEXT NOT NULL REFERENCES intents(intent_id),
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT REFERENCES application_projects(project_id),
    opportunity_revision_id TEXT REFERENCES opportunity_revisions(revision_id),
    objective            TEXT NOT NULL,
    steps                TEXT,           -- JSON array of {step_id, capability}
    state                TEXT NOT NULL DEFAULT 'PLANNED',
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE TABLE IF NOT EXISTS worker_results (
    result_id            TEXT PRIMARY KEY,
    task_id              TEXT NOT NULL REFERENCES tasks(task_id),
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT,
    worker_principal     TEXT NOT NULL,
    capability_id        TEXT NOT NULL,
    summary              TEXT NOT NULL,
    claims               TEXT,           -- JSON array of material claim entries
    context_refs         TEXT,           -- JSON array of bounded context refs
    model_ref            TEXT,           -- model run ref when model-backed (else NULL)
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_intents_tenant ON intents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_intents_org ON intents(organization_id);
CREATE INDEX IF NOT EXISTS idx_worker_results_task ON worker_results(task_id);
CREATE INDEX IF NOT EXISTS idx_worker_results_tenant ON worker_results(tenant_id);
