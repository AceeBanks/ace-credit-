"""B4.C13 — CEO Memory Constitution tests.

Proves lean operational continuity: closed task detail expires without losing
the promoted lesson; project summaries are reconstructable from canonical
state; transient provider outages expire after TTL. Plus adversarial
injections.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.memory_manager import (  # noqa: E402
    MemoryManager,
    MemoryPolicyError,
    MemoryRecord,
    lesson_candidate_to_promoted,
    project_summary_from_canonical,
)
from tools.g0.validate_memory_constitutions import (  # noqa: E402
    validate_ceo_classes,
    validate_ttl_policy,
)


def _record(memory_id="mem-1", memory_class="CM-BLOCKER",
            statement="georgia source X requires browser fallback",
            namespace="ceo_hermes", **overrides) -> MemoryRecord:
    kwargs = dict(
        memory_id=memory_id, memory_class=memory_class, namespace=namespace,
        statement=statement, importance="NORMAL", confidence_state="PROVISIONAL",
        created_at="2026-08-26T10:00:00Z")
    kwargs.update(overrides)
    return MemoryRecord(**kwargs)


def test_closed_task_detail_expires_but_lesson_survives():
    mgr = MemoryManager()
    # the transient detail (raw retry chatter) expires quickly
    mgr.store(_record(
        memory_id="mem-detail", memory_class="CM-BLOCKER",
        statement="attempt 3 timed out on source X",
        expires_at="2026-08-27T00:00:00Z"))
    # the promoted lesson has a long TTL
    mgr.store(_record(
        memory_id="mem-lesson", memory_class="CM-PROMOTED-LESSON",
        statement="georgia source X frequently requires browser fallback "
                  "after API failure",
        expires_at="2028-01-01T00:00:00Z"))
    later = datetime(2026, 9, 1, tzinfo=timezone.utc)
    active = mgr.retrieve_active("ceo_hermes", now=later)
    ids = {r.memory_id for r in active}
    assert "mem-lesson" in ids
    assert "mem-detail" not in ids


def test_project_summary_reconstructable_from_canonical_state():
    state = {
        "project_id": "proj-after-school",
        "opportunity_revision_id": "opp-rev-3",
        "eligibility_state": "ELIGIBLE",
        "deadline": "2026-10-15",
        "task_statuses": ["task:research-a SUCCEEDED"],
    }
    summary = project_summary_from_canonical(state)
    assert summary["project_id"] == "proj-after-school"
    assert summary["opportunity_revision_id"] == "opp-rev-3"
    assert summary["reconstructed_from"] == "canonical_state"
    # no memory required; a fresh manager has nothing stored
    assert MemoryManager().retrieve_active("ceo_hermes") == []


def test_transient_provider_outage_expires_after_ttl():
    mgr = MemoryManager()
    outage = _record(
        memory_id="mem-outage", memory_class="CM-HEALTH-DEGRADATION",
        statement="georgia-opb API degraded",
        expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).isoformat())
    mgr.store(outage)
    active = mgr.retrieve_active("ceo_hermes")
    assert any(r.memory_id == "mem-outage" for r in active)
    later = datetime.now(timezone.utc) + timedelta(days=8)
    assert mgr.retrieve_active("ceo_hermes", now=later) == []


def test_lesson_candidate_requires_book7_gate():
    mgr = MemoryManager()
    candidate = _record(
        memory_id="mem-cand", memory_class="CM-LESSON-CANDIDATE",
        statement="repeated clarification on budget range")
    mgr.store(candidate)
    with pytest.raises(MemoryPolicyError, match="Book 7"):
        lesson_candidate_to_promoted(candidate, eval_gate_passed=False)
    promoted = lesson_candidate_to_promoted(candidate, eval_gate_passed=True)
    assert promoted.memory_class == "CM-PROMOTED-LESSON"


def test_non_lesson_cannot_promote():
    blocker = _record(memory_class="CM-BLOCKER")
    with pytest.raises(MemoryPolicyError, match="CM-LESSON-CANDIDATE"):
        lesson_candidate_to_promoted(blocker, eval_gate_passed=True)


def test_raw_worker_logs_not_durable():
    # raw worker logs are not a durable class; the catalog has no such class
    mgr = MemoryManager()
    with pytest.raises(MemoryPolicyError, match="not in ceo_hermes"):
        mgr.store(_record(memory_class="RAW_WORKER_LOG",
                          statement="raw worker log line",
                          memory_id="mem-log"))


def test_ceo_class_catalog_is_frozen():
    from prototype.g0.agents.memory_manager import CEO_CLASSES
    assert CEO_CLASSES == {
        "CM-SYSTEM-DOCTRINE", "CM-ACTIVE-PROJECT", "CM-BLOCKER",
        "CM-CAPABILITY", "CM-LESSON-CANDIDATE", "CM-PROMOTED-LESSON",
        "CM-HEALTH-DEGRADATION"}


# --- validator adversarial ---------------------------------------------------

def test_ceo_classes_config_clean():
    errors: list[str] = []
    validate_ceo_classes(errors)
    assert errors == []


def test_ceo_config_missing_non_durable_fails(monkeypatch):
    import tools.g0.validate_memory_constitutions as mod
    data = {
        "namespace": "ceo_hermes",
        "classes": [
            {"class_id": c, "description": "d", "store_reference_not_duplicate": False}
            for c in sorted({"CM-SYSTEM-DOCTRINE", "CM-ACTIVE-PROJECT",
                             "CM-BLOCKER", "CM-CAPABILITY", "CM-LESSON-CANDIDATE",
                             "CM-PROMOTED-LESSON", "CM-HEALTH-DEGRADATION"})
        ],
        "non_durable_by_default": ["RAW_WORKER_LOGS", "ONE_OFF_RETRY_DETAILS",
                                   "ENTIRE_PROMPTS", "EVERY_GRANT_RESEARCHED",
                                   "CLOSED_TASK_CHATTER"],
        "lesson_promotion_flow": "requires Book 7 evaluation",
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_ceo_classes(errors)
    assert any("VERBOSE_TOOL_OUTPUT" in e for e in errors)


def test_ttl_policy_clean():
    errors: list[str] = []
    validate_ttl_policy(errors)
    assert errors == []


def test_ttl_policy_missing_class_fails(monkeypatch):
    import tools.g0.validate_memory_constitutions as mod
    data = {
        "default_ttl_days": 90,
        "class_ttls": {
            "PM-IDENTITY": 730, "PM-PREFERENCE": 730, "PM-GOAL": 365,
            "PM-DECISION": 365, "PM-RELATIONSHIP": 365, "PM-OPEN_LOOP": 180,
            "PM-EPISODIC_SUMMARY": 30, "CM-SYSTEM-DOCTRINE": 3650,
            "CM-ACTIVE-PROJECT": 30, "CM-BLOCKER": 30, "CM-CAPABILITY": 365,
            "CM-LESSON-CANDIDATE": 90, "CM-PROMOTED-LESSON": 730,
        },
        "ttl_rules": [
            "expires_at overrides class TTL",
            "promoted lesson outlives closed task detail",
            "CM-HEALTH-DEGRADATION outages expire",
        ],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_ttl_policy(errors)
    assert any("CM-HEALTH-DEGRADATION" in e for e in errors)
