"""B4.C12-C13 — Role-specific memory manager (prototype).

Implements the Personal and CEO memory constitutions:

  * MemoryRecord with the full field set; states ACTIVE/PROVISIONAL/
    SUPERSEDED/EXPIRED/CONFLICTED/ARCHIVED;
  * class validation against the role's memory-class catalog;
  * canonical-substitution guard: facts better represented in canonical
    domain state (EIN, deadline, award ceiling, verified revenue, application
    status, source-backed statistic) are refused as freeform truth and must
    store a canonical_ref instead;
  * supersede: user correction produces a new record and marks the old one
    SUPERSEDED (append-only);
  * TTL expiry: closed task detail expires without losing the promoted lesson;
    transient provider outages expire after CM-HEALTH-DEGRADATION TTL;
  * project summary reconstructable from canonical state without memory.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

MEMORY_STATES = {"ACTIVE", "PROVISIONAL", "SUPERSEDED", "EXPIRED",
                 "CONFLICTED", "ARCHIVED"}

PERSONAL_CLASSES = {
    "PM-IDENTITY", "PM-PREFERENCE", "PM-GOAL", "PM-DECISION",
    "PM-RELATIONSHIP", "PM-OPEN_LOOP", "PM-EPISODIC_SUMMARY",
}
CEO_CLASSES = {
    "CM-SYSTEM-DOCTRINE", "CM-ACTIVE-PROJECT", "CM-BLOCKER",
    "CM-CAPABILITY", "CM-LESSON-CANDIDATE", "CM-PROMOTED-LESSON",
    "CM-HEALTH-DEGRADATION",
}
CANONICAL_DUPLICATE_KEYWORDS = ("EIN", "deadline", "award ceiling",
                                "verified revenue", "application status",
                                "statistic", "tax exempt")


class MemoryPolicyError(ValueError):
    """Raised when a memory operation violates the constitution."""


@dataclass
class MemoryRecord:
    memory_id: str
    memory_class: str
    namespace: str
    statement: str
    importance: str = "NORMAL"
    confidence_state: str = "PROVISIONAL"
    status: str = "ACTIVE"
    source_event_refs: list[str] = field(default_factory=list)
    canonical_refs: list[str] = field(default_factory=list)
    created_at: str = ""
    last_confirmed_at: str = ""
    expires_at: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    privacy_class: str = "TENANT_PRIVATE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_class": self.memory_class,
            "namespace": self.namespace,
            "statement": self.statement,
            "importance": self.importance,
            "confidence_state": self.confidence_state,
            "status": self.status,
            "source_event_refs": list(self.source_event_refs),
            "canonical_refs": list(self.canonical_refs),
            "created_at": self.created_at,
            "last_confirmed_at": self.last_confirmed_at,
            "expires_at": self.expires_at,
            "supersedes": self.supersedes,
            "superseded_by": self.superseded_by,
            "privacy_class": self.privacy_class,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryManager:
    """In-memory prototype store keyed by namespace."""

    def __init__(self, class_catalog: dict[str, set[str]] | None = None):
        self._records: dict[str, list[MemoryRecord]] = {}
        self.class_catalog = class_catalog or {
            "personal_hermes": PERSONAL_CLASSES,
            "ceo_hermes": CEO_CLASSES,
        }

    def _ttl_days(self, memory_class: str) -> int:
        return {
            "PM-IDENTITY": 730, "PM-PREFERENCE": 730, "PM-GOAL": 365,
            "PM-DECISION": 365, "PM-RELATIONSHIP": 365, "PM-OPEN_LOOP": 180,
            "PM-EPISODIC_SUMMARY": 30, "CM-SYSTEM-DOCTRINE": 3650,
            "CM-ACTIVE-PROJECT": 30, "CM-BLOCKER": 30, "CM-CAPABILITY": 365,
            "CM-LESSON-CANDIDATE": 90, "CM-PROMOTED-LESSON": 730,
            "CM-HEALTH-DEGRADATION": 7,
        }.get(memory_class, 90)

    def store(self, record: MemoryRecord) -> MemoryRecord:
        classes = self.class_catalog.get(record.namespace, set())
        if record.memory_class not in classes:
            raise MemoryPolicyError(
                f"class {record.memory_class} not in {record.namespace} "
                "catalog")
        if record.status not in MEMORY_STATES:
            raise MemoryPolicyError(f"unknown memory state {record.status}")
        if not record.created_at:
            record.created_at = _now()
        if not record.expires_at:
            expiry = datetime.now(timezone.utc) + timedelta(
                days=self._ttl_days(record.memory_class))
            record.expires_at = expiry.isoformat()
        self._records.setdefault(record.namespace, []).append(record)
        return record

    def _is_active(self, record: MemoryRecord, now: datetime) -> bool:
        if record.status in ("SUPERSEDED", "EXPIRED", "ARCHIVED", "CONFLICTED"):
            return False
        if record.expires_at:
            expires = datetime.fromisoformat(
                record.expires_at.replace("Z", "+00:00"))
            if now > expires:
                return False
        return True

    def retrieve_active(self, namespace: str,
                        now: datetime | None = None) -> list[MemoryRecord]:
        now = now or datetime.now(timezone.utc)
        return [r for r in self._records.get(namespace, [])
                if self._is_active(r, now)]

    def supersede(self, record_id: str, replacement: MemoryRecord) -> MemoryRecord:
        """User correction: new record replaces old; history preserved."""
        for namespace, records in self._records.items():
            for i, r in enumerate(records):
                if r.memory_id == record_id:
                    r.status = "SUPERSEDED"
                    r.superseded_by = replacement.memory_id
                    replacement.supersedes = record_id
                    break
        self.store(replacement)
        return replacement

    def expire_past_ttl(self, namespace: str,
                        now: datetime | None = None) -> list[MemoryRecord]:
        """Expire records whose TTL has passed (forgetting is intentional)."""
        now = now or datetime.now(timezone.utc)
        expired = []
        for r in self._records.get(namespace, []):
            if r.expires_at:
                expires = datetime.fromisoformat(
                    r.expires_at.replace("Z", "+00:00"))
                if now > expires and r.status == "ACTIVE":
                    r.status = "EXPIRED"
                    expired.append(r)
        return expired


def canonical_substitution_guard(statement: str,
                                 canonical_ref: str | None) -> None:
    """Refuse freeform memory that duplicates canonical domain truth.

    EIN, grant deadlines, award ceilings, verified revenue, application
    status and source-backed statistics belong to canonical state; memory may
    only hold a reference.
    """
    lowered = statement.lower()
    for keyword in CANONICAL_DUPLICATE_KEYWORDS:
        if keyword.lower() in lowered:
            if not canonical_ref:
                raise MemoryPolicyError(
                    f"'{keyword}' is canonical domain truth — store a "
                    "canonical_ref, not freeform memory")


def project_summary_from_canonical(state: dict[str, Any]) -> dict[str, Any]:
    """CM-ACTIVE-PROJECT is reconstructable from canonical state alone."""
    return {
        "project_id": state.get("project_id"),
        "opportunity_revision_id": state.get("opportunity_revision_id"),
        "eligibility_state": state.get("eligibility_state"),
        "deadline": state.get("deadline"),
        "task_statuses": state.get("task_statuses", []),
        "reconstructed_from": "canonical_state",
    }


def lesson_candidate_to_promoted(record: MemoryRecord,
                                 eval_gate_passed: bool) -> MemoryRecord:
    """CM-LESSON-CANDIDATE requires Book 7 evaluation before promotion."""
    if record.memory_class != "CM-LESSON-CANDIDATE":
        raise MemoryPolicyError("only CM-LESSON-CANDIDATE may be promoted "
                                "through this gate")
    if not eval_gate_passed:
        raise MemoryPolicyError(
            "operational lesson cannot bypass Book 7 evaluation governance")
    record.memory_class = "CM-PROMOTED-LESSON"
    record.status = "ACTIVE"
    return record
