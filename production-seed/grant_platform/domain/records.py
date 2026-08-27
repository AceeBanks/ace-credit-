"""G1 Wave 1 — production domain records.

PROMOTED from G0 (`prototype/g0/domain/models.py`) into plain,
JSON-serializable records so they persist in Postgres. Contracts are
unchanged; only transport (dataclass -> durable row) is added.

All records are immutable by convention: a change creates a new revision
rather than mutating truth (Book 2 revision law).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- identity / tenant -------------------------------------------------------

@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    display_name: str
    created_at: str = ""


@dataclass(frozen=True)
class Principal:
    principal_id: str
    tenant_id: str
    principal_type: str        # USER | SERVICE | HERMES_PERSONAL | HERMES_CEO | WORKER
    authority_level: int = 1
    user_id: str | None = None
    created_at: str = ""


# --- policy / capability -----------------------------------------------------

@dataclass(frozen=True)
class Capability:
    capability_id: str
    required_level: int
    description: str = ""
    delegable: bool = False


@dataclass(frozen=True)
class Grant:
    grant_id: str
    principal_id: str
    capability_id: str
    authority_level: int
    tenant_id: str | None = None
    project_id: str | None = None
    resource_id: str | None = None
    expires_at: str | None = None
    created_at: str = ""


@dataclass(frozen=True)
class Approval:
    approval_id: str
    tenant_id: str
    capability_id: str
    resource_id: str
    action: str
    approval_class: str
    project_id: str | None = None
    resource_version: str | None = None
    status: str = "PENDING"    # PENDING | GRANTED | REVOKED | EXPIRED
    expires_at: str | None = None
    decision_ref: str | None = None
    created_at: str = ""


# --- grant domain ------------------------------------------------------------

@dataclass(frozen=True)
class Organization:
    organization_id: str
    tenant_id: str
    legal_name: str
    jurisdiction: str | None = None
    ein: str | None = None
    created_at: str = ""


@dataclass(frozen=True)
class Opportunity:
    opportunity_id: str
    tenant_id: str
    title: str
    funding_ceiling: Decimal | None = None
    deadline: str | None = None
    created_at: str = ""


@dataclass(frozen=True)
class OpportunityRevision:
    revision_id: str
    opportunity_id: str
    revision_number: int
    changed_terms: tuple[str, ...] = ()
    material: bool = False
    created_at: str = ""


@dataclass(frozen=True)
class ApplicationProject:
    project_id: str
    tenant_id: str
    organization_id: str
    opportunity_id: str
    revision_id: str
    state: str = "DRAFTING"    # DRAFTING | QA | READY_MOCK | BLOCKED
    created_at: str = ""


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    opportunity_revision_id: str
    requirement_type: str
    mandatory: bool = True
    prompt: str = ""
    word_limit: int | None = None
    state: str = "IDENTIFIED"


# --- evidence / decisions ----------------------------------------------------

@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    decision_type: str
    tenant_id: str
    actor_ref: str
    capability_id: str
    input_refs: tuple[dict, ...] = ()
    policy_ref: str = ""
    result: dict = field(default_factory=dict)
    explanation_data: dict = field(default_factory=dict)
    model_or_engine_ref: str = ""
    project_id: str | None = None
    created_at: str = ""


@dataclass(frozen=True)
class AuditEvent:
    audit_id: str
    tenant_id: str
    actor_ref: str
    event_type: str
    project_id: str | None = None
    decision_ref: str | None = None
    payload_ref: str | None = None
    created_at: str = ""


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    artifact_version_id: str
    tenant_id: str
    project_id: str | None
    kind: str
    payload_ref: str
    content_hash: str
    version_number: int
    created_at: str = ""


# --- durable task system -----------------------------------------------------

TASK_STATES = ("PENDING", "READY", "RUNNING", "BLOCKED", "SUCCEEDED",
               "FAILED", "CANCELLED", "STALE")


@dataclass(frozen=True)
class Task:
    task_id: str
    tenant_id: str
    task_type: str
    state: str = "PENDING"
    project_id: str | None = None
    worker_principal: str | None = None
    capability_id: str | None = None
    result_ref: str | None = None
    retry_count: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class TaskAttempt:
    attempt_id: str
    task_id: str
    worker_principal: str
    state: str = "RUNNING"     # RUNNING | SUCCEEDED | FAILED
    started_at: str = ""
    finished_at: str | None = None
    failure_reason: str | None = None
    result_ref: str | None = None
    lease_until: str | None = None
