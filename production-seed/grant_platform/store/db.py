"""G1 Wave 1 — durable store.

SQLite-backed implementation of the canonical tables from the migration
seed (`migrations/001_initial_schema.sql`), used for dev/CI. The schema is
portable; the Postgres adapter (G1.2 production) uses the same table
layout and the same repository interface.

Repositories are thin: they persist the domain records and enforce
tenant/project scope keys. They do NOT decide policy — authorization stays
in the G0 Authorizer / gateway layer.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from grant_platform.domain.records import (
    ApplicationProject,
    Approval,
    Artifact,
    AuditEvent,
    Capability,
    DecisionRecord,
    Grant,
    Opportunity,
    OpportunityRevision,
    Organization,
    Principal,
    Requirement,
    Task,
    TaskAttempt,
    Tenant,
)

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"
MIGRATION_FILES = sorted(MIGRATIONS_DIR.glob("*.sql"))  # append-only, ordered


class StoreError(Exception):
    pass


class TenantMismatch(StoreError):
    pass


class Store:
    """Canonical persistence. Every write carries tenant scope; project
    scope is enforced where the row is project-bound."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    # -- schema ---------------------------------------------------------
    @classmethod
    def open(cls, path: str = ":memory:") -> "Store":
        # check_same_thread=False: the dev/CI SQLite store is shared with
        # threaded servers (FastAPI TestClient/uvicorn). Production uses
        # Postgres, which has no such affinity.
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys=ON")
        store = cls(conn)
        store.migrate()
        return store

    def migrate(self) -> None:
        if not MIGRATION_FILES:
            raise StoreError("no migrations found")
        for path in MIGRATION_FILES:
            sql = path.read_text(encoding="utf-8")
            self.conn.executescript(sql)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # -- tenants / principals -------------------------------------------
    def create_tenant(self, t: Tenant) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO tenants (tenant_id, display_name)"
            " VALUES (?, ?)", (t.tenant_id, t.display_name))
        self.conn.commit()

    def get_tenant(self, tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM tenants WHERE tenant_id=?", (tenant_id,)).fetchone()
        return dict(row) if row else None

    def create_principal(self, p: Principal) -> None:
        if self.get_tenant(p.tenant_id) is None:
            raise StoreError(f"unknown tenant {p.tenant_id}")
        self.conn.execute(
            "INSERT OR REPLACE INTO principals (principal_id, tenant_id,"
            " principal_type, authority_level, user_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (p.principal_id, p.tenant_id, p.principal_type,
             p.authority_level, p.user_id))
        self.conn.commit()

    def get_principal(self, principal_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM principals WHERE principal_id=?",
            (principal_id,)).fetchone()
        return dict(row) if row else None

    # -- capabilities / grants -------------------------------------------
    def create_capability(self, c: Capability) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO capabilities (capability_id,"
            " required_level, description, delegable) VALUES (?, ?, ?, ?)",
            (c.capability_id, c.required_level, c.description,
             int(c.delegable)))
        self.conn.commit()

    def create_grant(self, g: Grant) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO grants (grant_id, principal_id,"
            " capability_id, authority_level, tenant_id, project_id,"
            " resource_id, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (g.grant_id, g.principal_id, g.capability_id, g.authority_level,
             g.tenant_id, g.project_id, g.resource_id, g.expires_at))
        self.conn.commit()

    def grants_for(self, principal_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM grants WHERE principal_id=?", (principal_id,))
        return [dict(r) for r in rows]

    # -- approvals ---------------------------------------------------------
    def create_approval(self, a: Approval) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO approvals (approval_id, tenant_id,"
            " project_id, capability_id, resource_id, resource_version,"
            " action, approval_class, status, expires_at, decision_ref)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (a.approval_id, a.tenant_id, a.project_id, a.capability_id,
             a.resource_id, a.resource_version, a.action, a.approval_class,
             a.status, a.expires_at, a.decision_ref))
        self.conn.commit()

    def get_approval(self, approval_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM approvals WHERE approval_id=?",
            (approval_id,)).fetchone()
        return dict(row) if row else None

    def set_approval_status(self, approval_id: str, status: str) -> None:
        self.conn.execute(
            "UPDATE approvals SET status=? WHERE approval_id=?",
            (status, approval_id))
        self.conn.commit()

    # -- organizations -----------------------------------------------------
    def create_organization(self, o: Organization) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO organizations (organization_id,"
            " tenant_id, legal_name, jurisdiction, ein)"
            " VALUES (?, ?, ?, ?, ?)",
            (o.organization_id, o.tenant_id, o.legal_name, o.jurisdiction,
             o.ein))
        self.conn.commit()

    def get_organization(self, organization_id: str,
                         tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM organizations WHERE organization_id=? AND"
            " tenant_id=?", (organization_id, tenant_id)).fetchone()
        return dict(row) if row else None

    # -- opportunities / revisions -----------------------------------------
    def create_opportunity(self, o: Opportunity) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO opportunities (opportunity_id,"
            " tenant_id, title, funding_ceiling, deadline)"
            " VALUES (?, ?, ?, ?, ?)",
            (o.opportunity_id, o.tenant_id, o.title,
             str(o.funding_ceiling) if o.funding_ceiling else None,
             o.deadline))
        self.conn.commit()

    def get_opportunity(self, opportunity_id: str,
                        tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM opportunities WHERE opportunity_id=? AND"
            " tenant_id=?", (opportunity_id, tenant_id)).fetchone()
        return dict(row) if row else None

    def create_revision(self, r: OpportunityRevision) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO opportunity_revisions (revision_id,"
            " opportunity_id, revision_number, changed_terms, material)"
            " VALUES (?, ?, ?, ?, ?)",
            (r.revision_id, r.opportunity_id, r.revision_number,
             json.dumps(list(r.changed_terms)), int(r.material)))
        self.conn.commit()

    def revisions_for(self, opportunity_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM opportunity_revisions WHERE opportunity_id=?"
            " ORDER BY revision_number", (opportunity_id,))
        return [dict(r) for r in rows]

    def get_revision(self, revision_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM opportunity_revisions WHERE revision_id=?",
            (revision_id,)).fetchone()
        return dict(row) if row else None

    # -- application projects ----------------------------------------------
    def create_project(self, p: ApplicationProject) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO application_projects (project_id,"
            " tenant_id, organization_id, opportunity_id, revision_id, state)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (p.project_id, p.tenant_id, p.organization_id, p.opportunity_id,
             p.revision_id, p.state))
        self.conn.commit()

    def get_project(self, project_id: str, tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM application_projects WHERE project_id=? AND"
            " tenant_id=?", (project_id, tenant_id)).fetchone()
        return dict(row) if row else None

    def set_project_state(self, project_id: str, state: str) -> None:
        self.conn.execute(
            "UPDATE application_projects SET state=? WHERE project_id=?",
            (state, project_id))
        self.conn.commit()

    # -- requirements -------------------------------------------------------
    def create_requirement(self, r: Requirement) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO requirements (requirement_id,"
            " opportunity_revision_id, requirement_type, mandatory, prompt,"
            " word_limit, state) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (r.requirement_id, r.opportunity_revision_id,
             r.requirement_type, int(r.mandatory), r.prompt,
             r.word_limit, r.state))
        self.conn.commit()

    def requirements_for(self, revision_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM requirements WHERE opportunity_revision_id=?",
            (revision_id,))
        return [dict(r) for r in rows]

    # -- decisions / audit / artifacts --------------------------------------
    def create_decision(self, d: DecisionRecord) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO decision_records (decision_id,"
            " decision_type, tenant_id, project_id, actor_ref, capability_id,"
            " input_refs, policy_ref, result, explanation_data,"
            " model_or_engine_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (d.decision_id, d.decision_type, d.tenant_id, d.project_id,
             d.actor_ref, d.capability_id, json.dumps(list(d.input_refs)),
             d.policy_ref, json.dumps(d.result),
             json.dumps(d.explanation_data), d.model_or_engine_ref))
        self.conn.commit()

    def get_decision(self, decision_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM decision_records WHERE decision_id=?",
            (decision_id,)).fetchone()
        return dict(row) if row else None

    def create_audit(self, a: AuditEvent) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO audit_events (audit_id, tenant_id,"
            " project_id, actor_ref, event_type, decision_ref, payload_ref)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (a.audit_id, a.tenant_id, a.project_id, a.actor_ref,
             a.event_type, a.decision_ref, a.payload_ref))
        self.conn.commit()

    def audit_for(self, tenant_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM audit_events WHERE tenant_id=? ORDER BY"
            " created_at DESC", (tenant_id,))
        return [dict(r) for r in rows]

    def create_artifact(self, a: Artifact) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO artifacts (artifact_id,"
            " artifact_version_id, tenant_id, project_id, kind, payload_ref,"
            " content_hash, version_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (a.artifact_id, a.artifact_version_id, a.tenant_id, a.project_id,
             a.kind, a.payload_ref, a.content_hash, a.version_number))
        self.conn.commit()

    def artifacts_for(self, project_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM artifacts WHERE project_id=? ORDER BY"
            " version_number", (project_id,))
        return [dict(r) for r in rows]

    # -- source snapshots --------------------------------------------------
    def create_snapshot(self, snap: dict) -> None:
        """Persist an immutable source snapshot. content_hash is unique;
        re-capturing identical content is idempotent."""
        self.conn.execute(
            "INSERT OR IGNORE INTO source_snapshots (snapshot_id,"
            " source_uri, fetched_at, content_hash, tenant_id, revision_id,"
            " payload_ref) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (snap["snapshot_id"], snap["canonical_url"],
             snap["retrieved_at"], snap["content_hash"],
             snap["tenant_id"], snap.get("revision_id"),
             snap["payload_ref"]))
        self.conn.commit()

    def latest_snapshot(self, source_id: str,
                        tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM source_snapshots WHERE tenant_id=? AND"
            " source_uri LIKE ? ORDER BY fetched_at DESC LIMIT 1",
            (tenant_id, f"%{source_id}%")).fetchone()
        return dict(row) if row else None

    def snapshots_for(self, tenant_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM source_snapshots WHERE tenant_id=? ORDER BY"
            " fetched_at", (tenant_id,))
        return [dict(r) for r in rows]

    # -- durable tasks ------------------------------------------------------
    def create_task(self, t: Task) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO tasks (task_id, tenant_id, project_id,"
            " task_type, state, worker_principal, capability_id, result_ref,"
            " retry_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (t.task_id, t.tenant_id, t.project_id, t.task_type, t.state,
             t.worker_principal, t.capability_id, t.result_ref,
             t.retry_count))
        self.conn.commit()

    def get_task(self, task_id: str, tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM tasks WHERE task_id=? AND tenant_id=?",
            (task_id, tenant_id)).fetchone()
        return dict(row) if row else None

    def set_task_state(self, task_id: str, state: str,
                       result_ref: str | None = None,
                       worker: str | None = None) -> None:
        self.conn.execute(
            "UPDATE tasks SET state=?, result_ref=COALESCE(?, result_ref),"
            " worker_principal=COALESCE(?, worker_principal)"
            " WHERE task_id=?", (state, result_ref, worker, task_id))
        self.conn.commit()

    def increment_task_retry(self, task_id: str) -> None:
        self.conn.execute(
            "UPDATE tasks SET retry_count=retry_count+1 WHERE task_id=?",
            (task_id,))
        self.conn.commit()

    def claim_task(self, task_id: str, tenant_id: str,
                   worker: str, lease_seconds: int = 300) -> bool:
        """Atomic claim: READY/PENDING task becomes RUNNING under a worker.
        Returns False on concurrent claim (the idempotency gate)."""
        cur = self.conn.execute(
            "UPDATE tasks SET state='RUNNING', worker_principal=?"
            " WHERE task_id=? AND tenant_id=? AND state IN"
            " ('PENDING','READY')", (worker, task_id, tenant_id))
        self.conn.commit()
        return cur.rowcount == 1

    def complete_task(self, task_id: str, tenant_id: str,
                      worker: str, result_ref: str) -> bool:
        cur = self.conn.execute(
            "UPDATE tasks SET state='SUCCEEDED', result_ref=?,"
            " worker_principal=? WHERE task_id=? AND tenant_id=? AND"
            " worker_principal=? AND state='RUNNING'",
            (result_ref, worker, task_id, tenant_id, worker))
        self.conn.commit()
        return cur.rowcount == 1

    def fail_task(self, task_id: str, tenant_id: str, worker: str,
                  reason: str) -> None:
        self.conn.execute(
            "UPDATE tasks SET state='FAILED', worker_principal=?"
            " WHERE task_id=? AND tenant_id=?",
            (worker, task_id, tenant_id))
        self.conn.commit()

    def mark_stale_tasks(self, stale_after_seconds: int = 600) -> int:
        """Lease expiry: RUNNING tasks whose lease has expired become STALE
        (recoverable by a new worker)."""
        cur = self.conn.execute(
            "UPDATE tasks SET state='STALE' WHERE state='RUNNING' AND"
            " created_at < datetime('now', ?)",
            (f"-{stale_after_seconds} seconds",))
        self.conn.commit()
        return cur.rowcount

    def tasks_for(self, tenant_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE tenant_id=? ORDER BY created_at",
            (tenant_id,))
        return [dict(r) for r in rows]

    # -- G1 Wave 3: conversations / intents / plans / worker results --------
    def create_conversation(self, c: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO conversations (conversation_id,"
            " tenant_id, client_actor_id, title, project_id)"
            " VALUES (?, ?, ?, ?, ?)",
            (c["conversation_id"], c["tenant_id"], c["client_actor_id"],
             c.get("title"), c.get("project_id")))
        self.conn.commit()

    def get_conversation(self, conversation_id: str,
                         tenant_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM conversations WHERE conversation_id=? AND"
            " tenant_id=?", (conversation_id, tenant_id)).fetchone()
        return dict(row) if row else None

    def create_message(self, m: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO messages (message_id, conversation_id,"
            " tenant_id, role, content) VALUES (?, ?, ?, ?, ?)",
            (m["message_id"], m["conversation_id"], m["tenant_id"],
             m["role"], m["content"]))
        self.conn.commit()

    def messages_for(self, conversation_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM messages WHERE conversation_id=? ORDER BY"
            " created_at", (conversation_id,))
        return [dict(r) for r in rows]

    def create_intent(self, i: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO intents (intent_id, tenant_id,"
            " client_actor_id, organization_id, intent_type, objective,"
            " authority_scope, confidence_state, version,"
            " supersedes_intent_id, source_conversation_ref, payload)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (i["intent_id"], i["tenant_id"], i["client_actor_id"],
             i["organization_id"], i["intent_type"], i["objective"],
             i["authority_scope"], i["confidence_state"], i["version"],
             i.get("supersedes_intent_id"),
             i.get("source_conversation_ref"),
             json.dumps(i.get("payload", {}))))
        self.conn.commit()

    def get_intent(self, intent_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM intents WHERE intent_id=?", (intent_id,)).fetchone()
        return dict(row) if row else None

    def intents_for(self, tenant_id: str, organization_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM intents WHERE tenant_id=? AND organization_id=?"
            " ORDER BY created_at", (tenant_id, organization_id))
        return [dict(r) for r in rows]

    def create_plan(self, p: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO task_plans (plan_id, intent_id,"
            " tenant_id, project_id, opportunity_revision_id, objective,"
            " steps, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (p["plan_id"], p["intent_id"], p["tenant_id"],
             p.get("project_id"), p.get("opportunity_revision_id"),
             p["objective"], json.dumps(p.get("steps", [])),
             p.get("state", "PLANNED")))
        self.conn.commit()

    def get_plan(self, plan_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM task_plans WHERE plan_id=?", (plan_id,)).fetchone()
        return dict(row) if row else None

    def create_worker_result(self, r: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO worker_results (result_id, task_id,"
            " tenant_id, project_id, worker_principal, capability_id,"
            " summary, claims, context_refs, model_ref)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (r["result_id"], r["task_id"], r["tenant_id"],
             r.get("project_id"), r["worker_principal"], r["capability_id"],
             r["summary"], json.dumps(r.get("claims", [])),
             json.dumps(r.get("context_refs", [])), r.get("model_ref")))
        self.conn.commit()

    def worker_results_for(self, project_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM worker_results WHERE project_id=? ORDER BY"
            " created_at", (project_id,))
        return [dict(r) for r in rows]

    def get_worker_result(self, task_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM worker_results WHERE task_id=?",
            (task_id,)).fetchone()
        return dict(row) if row else None
