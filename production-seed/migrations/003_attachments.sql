-- G1 Wave 5 — attachments table, SQLite DEV_FAST_PATH (TEST_ONLY).
-- Supports PDF, DOCX, TXT uploads with governed metadata.
-- Append-only migration.

CREATE TABLE IF NOT EXISTS attachments (
    attachment_id        TEXT PRIMARY KEY,
    tenant_id            TEXT NOT NULL REFERENCES tenants(tenant_id),
    project_id           TEXT REFERENCES application_projects(project_id),
    conversation_id      TEXT REFERENCES conversations(conversation_id),
    filename             TEXT NOT NULL,
    mime_type            TEXT NOT NULL,
    content_hash         TEXT NOT NULL,
    file_size_bytes      INTEGER NOT NULL,
    object_key           TEXT NOT NULL,
    parser_status        TEXT NOT NULL DEFAULT 'PENDING',
    content_text         TEXT,
    uploaded_by          TEXT NOT NULL,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_attachments_tenant ON attachments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_attachments_project ON attachments(project_id);
CREATE INDEX IF NOT EXISTS idx_attachments_hash ON attachments(content_hash);
