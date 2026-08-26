"""B4.C17-C18 — Compaction and context budget/retrieval tests.

C17: anchors survive every stage; factual numbers/dates are preserved
($75,000 must not become $750,000); uncertainty is never converted to
certainty; compacted context reproduces the same key decision on a gold
fixture; manifests record what happened.
C18: a very recent irrelevant message does not outrank an older active
project decision; exact referenced facts are always retrieved regardless of
semantic rank.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.compactor import (  # noqa: E402
    CompactionError,
    STAGES,
    assert_facts_preserved,
    compact,
    summarize_with_uncertainty_guard,
)
from tools.g0.validate_compaction_reconstruction import (  # noqa: E402
    validate_compaction_policy,
)


def _gold_items() -> list[str]:
    return [
        "anchor:tenant-georgia-youth",
        "anchor:opp-rev-3",
        "objective: draft proposal for after-school funding",
        "fact: budget ceiling is $75,000 per official rev 3",
        "fact: deadline 2026-10-15",
        "tool output dump from research step 4",
        "episode: brainstormed program name with client",
    ]


GOLD_ANCHORS = ["anchor:tenant-georgia-youth", "anchor:opp-rev-3"]


def test_anchors_survive_every_stage():
    items = _gold_items()
    for stage in STAGES:
        kept, manifest = compact(items, stage=stage, anchors=GOLD_ANCHORS)
        for anchor in GOLD_ANCHORS:
            assert anchor in kept, stage
        assert anchor in manifest.anchors_retained


def test_stage0_is_identity():
    items = _gold_items()
    kept, manifest = compact(items, stage="STAGE0_NO_COMPACTION",
                             anchors=GOLD_ANCHORS)
    assert kept == items
    assert manifest.removed_items == []


def test_compaction_preserves_factual_numbers():
    items = _gold_items()
    kept, _ = compact(items, stage="STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                      anchors=GOLD_ANCHORS)
    assert_facts_preserved(items, kept)
    # $75,000 appears verbatim; nothing introduced $750,000
    joined = " ".join(kept)
    assert "$75,000" in joined
    assert "$750,000" not in joined
    assert "2026-10-15" in joined


def test_compaction_drops_disposable():
    items = _gold_items()
    kept, manifest = compact(items, stage="STAGE1_DROP_DISPOSABLE_REDUNDANT",
                             anchors=GOLD_ANCHORS)
    assert any("tool output dump" in k for k in manifest.removed_items)
    assert not any("tool output dump" in k for k in kept)


def test_uncertainty_never_converted_to_certainty():
    items = ["eligibility of the pilot program is not confirmed",
             "partnership letter possibly required"]
    summary = summarize_with_uncertainty_guard(items)
    assert "uncertainty preserved" in summary
    assert "not confirmed" in summary
    # and compaction at any stage cannot introduce a certainty claim
    kept, _ = compact(items, stage="STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION",
                      anchors=["eligibility of the pilot program is not confirmed"])
    assert not any("is definitely eligible" in k for k in kept)


def test_compacted_context_reproduces_same_decision():
    """Gold fixture: same decision (ceiling=75000, deadline=2026-10-15)
    derived before and after compaction."""
    items = _gold_items()
    original_decision = _decision_from(items)
    kept, _ = compact(items, stage="STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION",
                      anchors=GOLD_ANCHORS)
    compacted_decision = _decision_from(kept)
    assert original_decision == compacted_decision


def _decision_from(items: list[str]) -> tuple:
    joined = " ".join(items)
    ceiling = "$75,000" if "$75,000" in joined else None
    deadline = "2026-10-15" if "2026-10-15" in joined else None
    return (ceiling, deadline)


def test_anchor_missing_from_input_fails():
    with pytest.raises(CompactionError, match="anchor"):
        compact(["x"], stage="STAGE1_DROP_DISPOSABLE_REDUNDANT",
                anchors=["anchor:ghost"])


def test_budget_below_anchors_fails():
    with pytest.raises(CompactionError, match="anchor count"):
        compact(_gold_items(), stage="STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                anchors=GOLD_ANCHORS, budget=1)


def test_manifest_records_everything():
    items = _gold_items()
    kept, manifest = compact(items, stage="STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                             anchors=GOLD_ANCHORS)
    d = manifest.to_dict()
    assert "removed_items" in d
    assert "summarized_items" in d
    assert "anchors_retained" in d
    assert "summary_generator_version" in d
    assert "before_budget" in d
    assert "after_budget" in d
    assert d["before_budget"] > d["after_budget"] or len(kept) < len(items)


def test_unknown_stage_rejected():
    with pytest.raises(CompactionError, match="unknown stage"):
        compact(_gold_items(), stage="STAGE99_NOPE", anchors=GOLD_ANCHORS)


# --- C18 budget/retrieval ----------------------------------------------------

def test_recent_irrelevant_message_does_not_outrank_active_decision():
    # An old but active project decision is P0; a brand-new irrelevant chat
    # message is P3 — relevance class wins over recency
    from prototype.g0.agents.context_builder import build_context_bundle
    bundle = build_context_bundle(
        consumer_actor="CEO_HERMES", operation_type="DRAFT",
        tenant_id="tenant-georgia-youth", project_id="proj-after-school",
        canonical_state_refs=["state:opp-rev-3"],
        policy_refs=["policy:capability-summary"],
        task_refs=["task:draft-a"],
        recent_interaction_refs=["conv/2026-08-26/session-999#msg-1"],
        anchors=["state:opp-rev-3"],
        context_budget={"item_count": 3})
    assert "state:opp-rev-3" in bundle.anchors
    # the irrelevant recent message is only in recent_interaction_refs, and
    # drops first under budget pressure
    from prototype.g0.agents.context_builder import _apply_budget
    squeezed = _apply_budget(bundle)
    assert "state:opp-rev-3" in squeezed.canonical_state_refs


def test_exact_referenced_fact_always_retrieved():
    from prototype.g0.agents.context_builder import build_context_bundle
    bundle = build_context_bundle(
        consumer_actor="CEO_HERMES", operation_type="ELIGIBILITY",
        tenant_id="tenant-georgia-youth", project_id="proj-after-school",
        canonical_state_refs=["state:opp-rev-3", "fact:canonical:tax-exempt-verified"],
        policy_refs=["policy:eligibility"],
        task_refs=["task:eligibility-1"],
        anchors=["fact:canonical:tax-exempt-verified"],
        context_budget={"item_count": 4})
    # exact referenced fact survives regardless of semantic rank
    assert "fact:canonical:tax-exempt-verified" in bundle.canonical_state_refs


# --- validator adversarial ---------------------------------------------------

def test_compaction_policy_clean():
    errors: list[str] = []
    validate_compaction_policy(errors)
    assert errors == []


def test_compaction_policy_missing_anchor_fails(monkeypatch):
    import tools.g0.validate_compaction_reconstruction as mod
    data = {
        "stages": ["STAGE0_NO_COMPACTION", "STAGE1_DROP_DISPOSABLE_REDUNDANT",
                   "STAGE2_SNIP_HISTORICAL_LOW_VALUE",
                   "STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                   "STAGE4_COLLAPSE_INACTIVE_PROJECT_CONTEXT",
                   "STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION"],
        "stage_triggers": {},
        "mandatory_anchors": [
            "TENANT_USER_IDENTITY_REFS", "ACTIVE_INTENT_OBJECTIVE",
            "AUTHORITY_SCOPE", "EXACT_ACTIVE_OPPORTUNITY_REVISION",
            "UNRESOLVED_CRITICAL_CLARIFICATION", "ELIGIBILITY_STATE",
            "DEADLINE_CRITICAL_STATE", "ACTIVE_BLOCKERS",
            "HUMAN_APPROVALS_DENIALS",
            "SOURCE_EVIDENCE_REFS_FOR_CURRENT_TASK"],
        "rules": [
            {"rule_id": f"COMPACT-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 5)
        ],
        "manifest_fields": ["REMOVED_ITEMS", "SUMMARIZED_ITEMS",
                            "ANCHORS_RETAINED", "SUMMARY_GENERATOR_VERSION",
                            "SOURCE_REFS", "BEFORE_AFTER_BUDGET"],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_compaction_policy(errors)
    assert any("SAFETY_SECURITY_CONSTRAINTS" in e for e in errors)


def test_compaction_policy_missing_rule_fails(monkeypatch):
    import tools.g0.validate_compaction_reconstruction as mod
    data = {
        "stages": ["STAGE0_NO_COMPACTION", "STAGE1_DROP_DISPOSABLE_REDUNDANT",
                   "STAGE2_SNIP_HISTORICAL_LOW_VALUE",
                   "STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
                   "STAGE4_COLLAPSE_INACTIVE_PROJECT_CONTEXT",
                   "STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION"],
        "stage_triggers": {},
        "mandatory_anchors": [
            "TENANT_USER_IDENTITY_REFS", "ACTIVE_INTENT_OBJECTIVE",
            "AUTHORITY_SCOPE", "EXACT_ACTIVE_OPPORTUNITY_REVISION",
            "UNRESOLVED_CRITICAL_CLARIFICATION", "ELIGIBILITY_STATE",
            "DEADLINE_CRITICAL_STATE", "ACTIVE_BLOCKERS",
            "HUMAN_APPROVALS_DENIALS",
            "SOURCE_EVIDENCE_REFS_FOR_CURRENT_TASK",
            "SAFETY_SECURITY_CONSTRAINTS"],
        "rules": [
            {"rule_id": f"COMPACT-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 4)
        ],
        "manifest_fields": ["REMOVED_ITEMS", "SUMMARIZED_ITEMS",
                            "ANCHORS_RETAINED", "SUMMARY_GENERATOR_VERSION",
                            "SOURCE_REFS", "BEFORE_AFTER_BUDGET"],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_compaction_policy(errors)
    assert any("COMPACT-004" in e for e in errors)
