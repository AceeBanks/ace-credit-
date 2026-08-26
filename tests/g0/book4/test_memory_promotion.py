"""B4.C14-C15 — Worker statelessness and memory promotion tests.

C14: a new worker instance can repeat a task from contract/snapshots without
hidden memory.
C15: random conversational detail is rejected; explicit durable preferences
promote; conflicting preferences create a supersession flow rather than
coequal memories; operational lessons cannot bypass Book 7 eval.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.memory_lifecycle import (  # noqa: E402
    MemoryCandidate,
    MemoryLifecycleError,
    classify_candidate,
    promote_candidate,
    repeat_worker_task,
)
from tools.g0.validate_memory_lifecycle import (  # noqa: E402
    validate_promotion_policy,
)


def _candidate(statement="prefers concise explanations", **overrides) -> MemoryCandidate:
    kwargs = dict(
        candidate_id="cand-1",
        proposed_memory_class="PM-PREFERENCE",
        proposed_statement=statement,
        source_refs=["event:user-said-2026-08-26"],
        why_useful="client communication preference",
        importance="NORMAL",
        proposed_by="PERSONAL_HERMES")
    kwargs.update(overrides)
    return MemoryCandidate(**kwargs)


# --- C14 worker statelessness ------------------------------------------------

def test_new_worker_instance_repeats_task_from_contract():
    contract = {
        "task_id": "task-42",
        "capability_id": "research.funder",
        "inputs_refs": ["snapshot:georgia-opb:rev-3", "artifact:profile-1"],
    }
    snapshots = [{"content_hash": "abc123"}, {"content_hash": "def456"}]
    first = repeat_worker_task(contract, snapshots)
    # simulate a brand-new worker instance with the same contract/snapshots
    second = repeat_worker_task(contract, snapshots)
    assert first == second
    assert first["memory_used"] == "none"
    assert "snapshot:georgia-opb:rev-3" in first["inputs_used"]


def test_worker_does_not_require_hidden_memory():
    contract = {
        "task_id": "task-7",
        "capability_id": "qa.requirement_coverage",
        "inputs_refs": ["artifact:blueprint-1"],
    }
    result = repeat_worker_task(contract, [{"content_hash": "x"}])
    # correctness does not depend on any memory store
    assert result["deterministic_hash"] == repeat_worker_task(
        contract, [{"content_hash": "x"}])["deterministic_hash"]
    assert result["memory_used"] == "none"


def test_worker_determinism_changes_with_inputs():
    contract = {"task_id": "task-7", "capability_id": "qa",
                "inputs_refs": ["artifact:blueprint-1"]}
    a = repeat_worker_task(contract, [{"content_hash": "x"}])
    b = repeat_worker_task(contract, [{"content_hash": "y"}])
    assert a["deterministic_hash"] != b["deterministic_hash"]


# --- C15 promotion -----------------------------------------------------------

def test_random_conversational_detail_rejected():
    candidate = _candidate("said hi, how are you today")
    classify_candidate(candidate)
    assert candidate.classification == "REJECT"
    with pytest.raises(MemoryLifecycleError, match="REJECT"):
        promote_candidate(candidate)


def test_explicit_durable_preference_promoted():
    candidate = _candidate("prefers drafts surfaced before full package")
    classify_candidate(candidate)
    assert candidate.classification == "PROMOTE_FOR_REVIEW"
    promotion = promote_candidate(candidate)
    assert promotion.decision == "PROMOTE"
    assert promotion.validation_state == "AUTO_PROMOTED"
    assert promotion.criteria_evidence["explicit_user_statement"] is True


def test_conflicting_preference_requires_supersession():
    candidate = _candidate("wants up to 10 opportunities now")
    classify_candidate(candidate)
    with pytest.raises(MemoryLifecycleError, match="supersession"):
        promote_candidate(candidate, conflicting_active=[{"memory_id": "old-1"}])


def test_operational_lesson_cannot_bypass_eval():
    candidate = _candidate(
        proposed_memory_class="CM-LESSON-CANDIDATE",
        statement="repeated clarification on budget range",
        proposed_by="CEO_HERMES")
    classify_candidate(candidate)
    assert candidate.classification == "PROMOTE_FOR_REVIEW"
    with pytest.raises(MemoryLifecycleError, match="Book 7"):
        promote_candidate(candidate, eval_gate_passed=False)
    promotion = promote_candidate(candidate, eval_gate_passed=True)
    assert promotion.validation_state == "BOOK7_EVAL_REQUIRED"
    assert promotion.evaluator_ref == "book7-eval"


def test_low_value_detail_temporary_only():
    candidate = _candidate("the office is on the third floor",
                           proposed_memory_class="PM-EPISODIC_SUMMARY")
    classify_candidate(candidate)
    assert candidate.classification == "TEMPORARY"


# --- validator adversarial ---------------------------------------------------

def test_promotion_policy_clean():
    errors: list[str] = []
    validate_promotion_policy(errors)
    assert errors == []


def test_promotion_policy_lesson_bypass_fails(monkeypatch):
    import tools.g0.validate_memory_lifecycle as mod
    data = {
        "criteria": ["REPEATED_USE", "EXPLICIT_USER_STATEMENT",
                     "HIGH_FUTURE_UTILITY", "STABILITY_OVER_TIME",
                     "NOT_BETTER_REPRESENTED_AS_CANONICAL",
                     "NO_HIGHER_AUTHORITY_CONTRADICTION",
                     "PRIVACY_RETENTION_ALLOWED"],
        "auto_promotable_classes": ["PM-PREFERENCE", "PM-GOAL", "PM-OPEN_LOOP"],
        "review_required_classes": ["PM-IDENTITY", "PM-DECISION",
                                    "PM-RELATIONSHIP", "CM-BLOCKER",
                                    "CM-CAPABILITY"],
        "book7_eval_required_classes": ["CM-LESSON-CANDIDATE", "PM-GOAL"],
        "rules": [
            {"rule_id": f"PROMO-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 6)
        ],
        "promotion_criteria_gate": {
            "auto_promote_requires": ["EXPLICIT_USER_STATEMENT",
                                      "NO_HIGHER_AUTHORITY_CONTRADICTION",
                                      "PRIVACY_RETENTION_ALLOWED"]},
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_promotion_policy(errors)
    assert any("overlap" in e for e in errors)


def test_promotion_policy_missing_criteria_fails(monkeypatch):
    import tools.g0.validate_memory_lifecycle as mod
    data = {
        "criteria": ["REPEATED_USE"],
        "auto_promotable_classes": ["PM-PREFERENCE"],
        "review_required_classes": ["PM-IDENTITY"],
        "book7_eval_required_classes": ["CM-LESSON-CANDIDATE"],
        "rules": [
            {"rule_id": f"PROMO-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 6)
        ],
        "promotion_criteria_gate": {
            "auto_promote_requires": ["EXPLICIT_USER_STATEMENT",
                                      "NO_HIGHER_AUTHORITY_CONTRADICTION",
                                      "PRIVACY_RETENTION_ALLOWED"]},
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_promotion_policy(errors)
    assert any("criteria" in e for e in errors)


def test_lifecycle_schemas_strict():
    from tools.g0.validate_memory_lifecycle import (
        CANDIDATE_REQUIRED, RECORD_REQUIRED, PROMOTION_REQUIRED,
        SUPERSESSION_REQUIRED, _check)
    errors: list[str] = []
    _check("memory_candidate.schema.json", CANDIDATE_REQUIRED, errors)
    _check("memory_record.schema.json", RECORD_REQUIRED, errors)
    _check("memory_promotion.schema.json", PROMOTION_REQUIRED, errors)
    _check("memory_supersession.schema.json", SUPERSESSION_REQUIRED, errors)
    assert errors == []
