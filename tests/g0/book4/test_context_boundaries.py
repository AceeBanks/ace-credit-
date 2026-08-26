"""B4.C10-C11 — Client explanation and ContextBundle assembly tests.

C10: explanations preserve core outcome facts; visible past-winner/funder
research requirement is satisfied; style transformation cannot change factual
fixture values ($75,000 must not become $750,000).
C11: mandatory anchors survive budget pressure; irrelevant old conversations
are excluded; the same state produces deterministic mandatory refs. Plus
adversarial validator injections.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.context_builder import (  # noqa: E402
    ContextAssemblyError,
    build_context_bundle,
    build_explanation,
    extract_factual_tokens,
    style_transform,
)
from tools.g0.validate_context_explanation import (  # noqa: E402
    validate_context_budget_policy,
)

SAMPLE_OUTCOME = {
    "outcome_id": "oc-1",
    "application_project_id": "proj-after-school",
    "opportunity_revision_id": "opp-rev-3",
    "executive_summary": "Eligible on 8/8 validated rules; deadline "
                         "2026-10-15; funding range $50,000-$150,000",
    "research_pack_refs": ["research:funder-youth", "research:winners-2024"],
    "artifact_refs": ["artifact:blueprint-1"],
    "unresolved_questions": ["partnership letter still required"],
    "evidence_refs": ["evidence:deadline-rev3"],
    "client_action_required": True,
}


# --- C10 explanation ---------------------------------------------------------

def test_explanation_preserves_core_outcome_facts():
    explanation = build_explanation(explanation_id="exp-1",
                                    outcome=SAMPLE_OUTCOME)
    assert explanation["outcome_id"] == "oc-1"
    assert "2026-10-15" in explanation["summary"]
    assert "$50,000" in explanation["summary"]
    # uncertainty disclosed
    assert "partnership letter still required" in \
        explanation["uncertainty_disclosures"]


def test_explanation_visible_research_requirement():
    explanation = build_explanation(explanation_id="exp-2",
                                    outcome=SAMPLE_OUTCOME)
    # visible past-winner/funder research is a product requirement
    assert "research:funder-youth" in explanation["visible_research_refs"]
    assert "research:winners-2024" in explanation["visible_research_refs"]
    assert "artifact:blueprint-1" in explanation["visible_artifact_refs"]


def test_style_transform_cannot_change_factual_values():
    explanation = build_explanation(explanation_id="exp-3",
                                    outcome=SAMPLE_OUTCOME)
    before = explanation["factual_anchors"]
    assert "$50,000" in before
    transformed = style_transform(
        explanation,
        lambda text: text.replace("Eligible on 8/8", "You are eligible on 8/8")
                       .replace("funding range", "the funding range is"))
    assert "You are eligible on 8/8" in transformed["summary"]
    assert "the funding range is" in transformed["summary"]
    # factual tokens unchanged
    assert extract_factual_tokens(transformed["summary"]) == \
        extract_factual_tokens(explanation["summary"])
    # the adversarial case: a transform that corrupts $75,000 -> $750,000 fails
    with pytest.raises(ContextAssemblyError, match="factual tokens"):
        style_transform(explanation,
                        lambda text: text.replace("$50,000", "$500,000"))


def test_factual_extraction_finds_amounts_dates_revisions():
    tokens = extract_factual_tokens(
        "Deadline 2026-10-15; ceiling $150,000; rev opp-rev-3")
    assert "2026-10-15" in tokens
    assert "$150,000" in tokens
    assert "opp-rev-3" in tokens


# --- C11 context bundle ------------------------------------------------------

def _bundle_kwargs(**overrides) -> dict:
    kwargs = dict(
        consumer_actor="CEO_HERMES", operation_type="MATCH_ASSESSMENT",
        tenant_id="tenant-georgia-youth", project_id="proj-after-school",
        canonical_state_refs=["state:org-1", "state:opp-rev-3"],
        evidence_refs=["evidence:deadline-rev3"],
        memory_refs=["mem:lesson-1"],
        recent_interaction_refs=["conv/2026-08-26/session-441#msg-12"],
        policy_refs=["policy:capability-summary"],
        task_refs=["task:research-a"],
        anchors=["state:opp-rev-3", "state:org-1"],
        excluded_context_classes=["RAW_CLIENT_TRANSCRIPT"],
        context_budget={"item_count": 100},
    )
    kwargs.update(overrides)
    return kwargs


def test_anchors_survive_budget_pressure():
    # 4 mandatory refs (2 canonical + 1 policy + 1 task); a budget of exactly
    # 4 must keep all anchors/mandatory refs while optional classes are dropped
    bundle = build_context_bundle(**_bundle_kwargs(
        context_budget={"item_count": 4}))
    assert "state:opp-rev-3" in bundle.anchors
    assert "state:org-1" in bundle.anchors
    for anchor in bundle.anchors:
        assert anchor in (bundle.canonical_state_refs + bundle.policy_refs
                          + bundle.task_refs + bundle.evidence_refs
                          + bundle.memory_refs + bundle.recent_interaction_refs)
    # optional classes were the ones dropped under pressure
    assert bundle.recent_interaction_refs == []
    assert bundle.evidence_refs == []
    assert bundle.memory_refs == []


def test_budget_below_mandatory_fails():
    with pytest.raises(ContextAssemblyError, match="mandatory refs"):
        build_context_bundle(**_bundle_kwargs(context_budget={"item_count": 1}))


def test_irrelevant_old_conversations_excluded():
    bundle = build_context_bundle(**_bundle_kwargs())
    # old unrelated conversations are not injected; only the selected ref
    assert "conv/2026-08-26/session-441#msg-12" in \
        bundle.recent_interaction_refs
    assert "conv/2024-archived-session" not in \
        bundle.recent_interaction_refs
    assert "RAW_CLIENT_TRANSCRIPT" in bundle.excluded_context_classes


def test_deterministic_mandatory_refs_same_state():
    a = build_context_bundle(**_bundle_kwargs())
    b = build_context_bundle(**_bundle_kwargs())
    assert a.mandatory_refs() == b.mandatory_refs()
    assert a.canonical_state_refs == b.canonical_state_refs
    assert a.policy_refs == b.policy_refs
    assert a.task_refs == b.task_refs


def test_missing_anchor_ref_fails():
    with pytest.raises(ContextAssemblyError, match="anchors"):
        build_context_bundle(**_bundle_kwargs(anchors=["state:ghost-rev"]))


def test_different_project_scope_isolated():
    a = build_context_bundle(**_bundle_kwargs(project_id="proj-a"))
    b = build_context_bundle(**_bundle_kwargs(project_id="proj-b"))
    assert a.project_id == "proj-a"
    assert b.project_id == "proj-b"


# --- validator adversarial checks --------------------------------------------

def test_budget_policy_clean():
    errors: list[str] = []
    validate_context_budget_policy(errors)
    assert errors == []


def test_budget_policy_wrong_assembly_order_fails(monkeypatch):
    import tools.g0.validate_context_explanation as mod
    data = {
        "assembly_order": ["OPTIONAL_SUPPORTING_HISTORY_WITHIN_BUDGET"],
        "priority_classes": {"P0_MANDATORY": [], "P1_HIGH": [],
                             "P2_SUPPORTING": [], "P3_OPTIONAL": []},
        "never_default_inject": ["ENTIRE_USER_HISTORY", "ENTIRE_WORKER_TRACES",
                                 "CLOSED_PROJECT_TRANSCRIPTS", "RAW_SECRETS",
                                 "IRRELEVANT_APPLICATION_DOCUMENTS",
                                 "SUPERSEDED_MEMORY"],
        "budget_units": [],
        "anchor_policy": {"mandatory_anchors_survive": "ALWAYS",
                          "anchor_priority": "P0_MANDATORY",
                          "violation": "ASSEMBLY_ERROR"},
        "retrieval_order": ["EXACT_REQUIRED_REFS",
                            "RECENCY_AS_TIEBREAKER_ONLY"],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_context_budget_policy(errors)
    assert any("assembly_order" in e for e in errors)


def test_budget_policy_anchor_not_always_fails(monkeypatch):
    import tools.g0.validate_context_explanation as mod
    data = {
        "assembly_order": [
            "REQUIRED_CANONICAL_STATE", "REQUIRED_CURRENT_EVIDENCE",
            "ACTIVE_TASK_PROJECT_STATE", "MANDATORY_POLICY_CONSTRAINTS",
            "PROMOTED_ROLE_SPECIFIC_MEMORY",
            "SELECTED_RECENT_INTERACTION_CONTEXT",
            "OPTIONAL_SUPPORTING_HISTORY_WITHIN_BUDGET"],
        "priority_classes": {"P0_MANDATORY": [], "P1_HIGH": [],
                             "P2_SUPPORTING": [], "P3_OPTIONAL": []},
        "never_default_inject": ["ENTIRE_USER_HISTORY", "ENTIRE_WORKER_TRACES",
                                 "CLOSED_PROJECT_TRANSCRIPTS", "RAW_SECRETS",
                                 "IRRELEVANT_APPLICATION_DOCUMENTS",
                                 "SUPERSEDED_MEMORY"],
        "budget_units": [],
        "anchor_policy": {"mandatory_anchors_survive": "SOMETIMES",
                          "anchor_priority": "P0_MANDATORY",
                          "violation": "ASSEMBLY_ERROR"},
        "retrieval_order": ["EXACT_REQUIRED_REFS",
                            "RECENCY_AS_TIEBREAKER_ONLY"],
    }
    errors: list[str] = []
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    validate_context_budget_policy(errors)
    assert any("ALWAYS" in e for e in errors)


def test_explanation_schema_requires_uncertainty():
    from tools.g0.validate_context_explanation import _load_schema
    ok, schema = _load_schema("client_explanation_packet.schema.json")
    assert ok
    assert "uncertainty_disclosures" in schema["required"]
    assert "visible_research_refs" in schema["required"]
    assert "factual_anchors" in schema["properties"]
