"""B4.C12 — Personal Memory Constitution tests.

Proves persistent relationship continuity without infinite autobiographical
storage: stable preferences survive compaction; official grant deadlines are
not duplicated as freeform memory truth; old preferences can be superseded;
user corrections produce new records/supersession. Plus adversarial
injections against the validator and memory manager.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.memory_manager import (  # noqa: E402
    MemoryManager,
    MemoryPolicyError,
    MemoryRecord,
    canonical_substitution_guard,
)
from tools.g0.validate_memory_constitutions import (  # noqa: E402
    validate_personal_classes,
)


def _pref(statement="prefers concise explanations", **overrides) -> MemoryRecord:
    kwargs = dict(
        memory_id="mem-pref-1", memory_class="PM-PREFERENCE",
        namespace="personal_hermes", statement=statement,
        importance="NORMAL", confidence_state="VERIFIED",
        source_event_refs=["event:user-said-2026-08-26"],
        created_at="2026-08-26T10:00:00Z")
    kwargs.update(overrides)
    return MemoryRecord(**kwargs)


def test_stable_preference_survives_compaction():
    mgr = MemoryManager()
    mgr.store(_pref())
    # compaction may drop episodic detail, never active preferences
    active = mgr.retrieve_active("personal_hermes")
    assert any(r.memory_id == "mem-pref-1" for r in active)


def test_grant_deadline_not_duplicated_as_freeform_truth():
    # storing a deadline without a canonical ref is a policy violation
    with pytest.raises(MemoryPolicyError, match="canonical_ref"):
        canonical_substitution_guard(
            "the grant deadline is 2026-10-15", canonical_ref=None)
    # with a canonical ref it is permitted as a pointer, not truth
    canonical_substitution_guard("the grant deadline is 2026-10-15",
                                 canonical_ref="fact:canonical:deadline-rev3")


def test_ein_and_statistic_are_canonical_only():
    with pytest.raises(MemoryPolicyError, match="canonical_ref"):
        canonical_substitution_guard("our EIN is 58-1234567", None)
    with pytest.raises(MemoryPolicyError, match="canonical_ref"):
        canonical_substitution_guard(
            "verified revenue is $1.2M per the audited statement", None)


def test_old_preference_can_be_superseded():
    mgr = MemoryManager()
    old = mgr.store(_pref("show me only top 3 grants"))
    new = _pref("I want to review up to 10 now", memory_id="mem-pref-2")
    mgr.supersede(old.memory_id, new)
    active = mgr.retrieve_active("personal_hermes")
    ids = {r.memory_id for r in active}
    assert "mem-pref-2" in ids
    assert "mem-pref-1" not in ids  # superseded excluded from active
    # historical reconstruction still sees the old record
    all_records = mgr._records["personal_hermes"]
    old_record = next(r for r in all_records if r.memory_id == "mem-pref-1")
    assert old_record.status == "SUPERSEDED"
    assert old_record.superseded_by == "mem-pref-2"


def test_user_correction_produces_supersession():
    mgr = MemoryManager()
    wrong = mgr.store(_pref("client prefers email updates weekly"))
    corrected = _pref("client prefers email updates monthly",
                      memory_id="mem-pref-3")
    mgr.supersede(wrong.memory_id, corrected)
    assert corrected.supersedes == wrong.memory_id
    active = mgr.retrieve_active("personal_hermes")
    assert [r.memory_id for r in active] == ["mem-pref-3"]


def test_unknown_class_rejected():
    mgr = MemoryManager()
    with pytest.raises(MemoryPolicyError, match="not in personal_hermes"):
        mgr.store(_pref(memory_class="CM-BLOCKER"))


def test_expired_preference_leaves_active_retrieval():
    mgr = MemoryManager()
    mgr.store(_pref(expires_at="2020-01-01T00:00:00Z"))
    active = mgr.retrieve_active("personal_hermes")
    assert active == []


def test_personal_class_catalog_is_frozen():
    from prototype.g0.agents.memory_manager import PERSONAL_CLASSES
    assert PERSONAL_CLASSES == {
        "PM-IDENTITY", "PM-PREFERENCE", "PM-GOAL", "PM-DECISION",
        "PM-RELATIONSHIP", "PM-OPEN_LOOP", "PM-EPISODIC_SUMMARY"}


# --- validator adversarial ---------------------------------------------------

def test_personal_classes_config_clean():
    errors: list[str] = []
    validate_personal_classes(errors)
    assert errors == []


def test_personal_config_namespace_collision_fails(monkeypatch):
    import tools.g0.validate_memory_constitutions as mod
    data = {
        "namespace": "ceo_hermes",
        "classes": [
            {"class_id": c, "description": "d", "store_reference_not_duplicate": False}
            for c in sorted({"PM-IDENTITY", "PM-PREFERENCE", "PM-GOAL",
                             "PM-DECISION", "PM-RELATIONSHIP", "PM-OPEN_LOOP",
                             "PM-EPISODIC_SUMMARY"})
        ],
        "canonical_substitution_rule": "rule",
        "canonical_duplicate_examples": ["EIN"],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_personal_classes(errors)
    assert any("namespace" in e for e in errors)


def test_personal_config_missing_class_fails(monkeypatch):
    import tools.g0.validate_memory_constitutions as mod
    data = {
        "namespace": "personal_hermes",
        "classes": [
            {"class_id": c, "description": "d", "store_reference_not_duplicate": False}
            for c in ["PM-IDENTITY", "PM-PREFERENCE", "PM-GOAL", "PM-DECISION",
                      "PM-RELATIONSHIP", "PM-OPEN_LOOP"]
        ],
        "canonical_substitution_rule": "rule",
        "canonical_duplicate_examples": ["EIN"],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_personal_classes(errors)
    assert any("PM-EPISODIC_SUMMARY" in e for e in errors)
