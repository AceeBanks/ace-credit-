"""B4.C20-C21 — Co-adaptation and client feedback loop tests.

C20: simulated repeated clarification produces a lesson candidate; no
co-adaptation change promotes without Book 7 evaluation governance.
C21: a client changing target geography invalidates the relevant grant
search/match plan; "I don't like this tone" updates preference/artifact
request, never canonical grant facts. Plus validator adversarial checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.feedback import (  # noqa: E402
    FeedbackError,
    apply_feedback,
    classify_feedback,
    coadaptation_lesson,
)
from tools.g0.validate_feedback_loop import main as _validator_main  # noqa: F401


def test_geography_change_invalidates_match_plan():
    result = apply_feedback(
        feedback_id="fb-1", client_actor_id="user-7",
        tenant_id="tenant-georgia-youth",
        raw_text="Actually, let's focus on Tennessee now instead of Georgia",
        active_plan_ids=["plan:grant-search-1", "plan:match-2"])
    assert result.feedback_type == "PRIORITY_CHANGE"
    assert result.invalidated_plan_ids == ["plan:grant-search-1", "plan:match-2"]
    assert result.operational_impact is True
    assert result.canonical_fact_mutation is False


def test_tone_feedback_updates_preference_not_facts():
    result = apply_feedback(
        feedback_id="fb-2", client_actor_id="user-7",
        tenant_id="tenant-georgia-youth",
        raw_text="I don't like this tone — we talk more casually")
    assert result.feedback_type == "PREFERENCE_CORRECTION"
    assert result.preference_supersession["class"] == "PM-PREFERENCE"
    assert result.artifact_revision_request is not None
    # canonical grant facts are untouched
    assert result.canonical_fact_mutation is False
    assert result.invalidated_plan_ids == []


def test_factual_correction_is_proposal_not_mutation():
    result = apply_feedback(
        feedback_id="fb-3", client_actor_id="user-7",
        tenant_id="tenant-georgia-youth",
        raw_text="Our revenue number is incorrect — it's 1.2M now")
    assert result.feedback_type == "FACTUAL_CORRECTION"
    assert result.routing == "FACT_PROPOSAL"
    assert result.fact_proposal["status"] == "ASSERTION"
    assert result.canonical_fact_mutation is False


def test_intent_misunderstood_amends_intent():
    result = apply_feedback(
        feedback_id="fb-4", client_actor_id="user-7",
        tenant_id="tenant-georgia-youth",
        raw_text="No, that's not what I wanted — I meant a pilot program")
    assert result.feedback_type == "INTENT_MISUNDERSTOOD"
    assert result.routing == "INTENT_AMENDMENT"
    assert result.operational_impact is True


def test_repeated_clarification_produces_lesson_candidate():
    lesson = coadaptation_lesson(
        "CLARIFICATION_RATE",
        "client repeatedly clarifies budget range after intent")
    assert lesson["memory_class"] == "CM-LESSON-CANDIDATE"
    assert lesson["book7_eval_required"] is True
    assert lesson["classification"] == "PROMOTE_FOR_REVIEW"


def test_coadaptation_lesson_cannot_promote_without_book7():
    from prototype.g0.agents.memory_lifecycle import (
        MemoryCandidate, MemoryLifecycleError, classify_candidate,
        promote_candidate)
    candidate = MemoryCandidate(
        candidate_id="cand-adapt", proposed_memory_class="CM-LESSON-CANDIDATE",
        proposed_statement="co-adaptation: clarify budget range earlier",
        source_refs=["metric:CLARIFICATION_RATE"], proposed_by="CEO_HERMES")
    classify_candidate(candidate)
    with pytest.raises(MemoryLifecycleError, match="Book 7"):
        promote_candidate(candidate, eval_gate_passed=False)


def test_unclassifiable_feedback_rejected():
    with pytest.raises(FeedbackError, match="unclassifiable"):
        apply_feedback(feedback_id="fb-x", client_actor_id="u",
                       tenant_id="t", raw_text="good morning!!!")


def test_project_cancellation_pauses():
    result = apply_feedback(
        feedback_id="fb-5", client_actor_id="user-7",
        tenant_id="tenant-georgia-youth",
        raw_text="Let's pause this project for now")
    assert result.feedback_type == "PROJECT_CANCELLATION_PAUSE"
    assert result.operational_impact is True


# --- validator adversarial ---------------------------------------------------

def test_feedback_policy_clean():
    import subprocess
    proc = subprocess.run([sys.executable, "tools/g0/validate_feedback_loop.py"],
                          cwd=_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout
    assert '"status": "PASS"' in proc.stdout


def test_feedback_routing_factual_correction_must_be_proposal(monkeypatch):
    import tools.g0.validate_feedback_loop as mod
    data = {
        "feedback_types": ["INTENT_MISUNDERSTOOD", "FACTUAL_CORRECTION",
                            "PREFERENCE_CORRECTION",
                            "ARTIFACT_REVISION_REQUEST", "PRIORITY_CHANGE",
                            "PROJECT_CANCELLATION_PAUSE",
                            "RESULT_DISAGREEMENT"],
        "flow": ["CLIENT_CORRECTION", "PERSONAL_HERMES",
                  "CLASSIFY_FEEDBACK",
                  "ROUTE_TO_AMENDMENT_OR_PROPOSAL_OR_SUPERSESSION",
                  "CEO_NOTIFY_IF_OPERATIONAL_IMPACT",
                  "SELECTIVE_REPLAN_RECOMPUTE"],
        "routing": {"INTENT_MISUNDERSTOOD": "INTENT_AMENDMENT",
                    "FACTUAL_CORRECTION": "CANONICAL_MUTATION",
                    "PREFERENCE_CORRECTION": "MEMORY_SUPERSESSION",
                    "ARTIFACT_REVISION_REQUEST": "ARTIFACT_REVISION_REQUEST",
                    "PRIORITY_CHANGE": "INTENT_AMENDMENT",
                    "PROJECT_CANCELLATION_PAUSE": "PROJECT_STATE_CHANGE",
                    "RESULT_DISAGREEMENT": "EXPLANATION_REVIEW"},
        "rules": [
            {"rule_id": f"FEEDBACK-{n:03d}", "title": "t", "rule": "r",
             "enforcement": "MUST"} for n in range(1, 5)
        ],
        "coadaptation_metrics": ["CLARIFICATION_RATE",
                                  "REPEATED_MISSING_INTENT_FIELDS",
                                  "CEO_REPLANNING_RATE",
                                  "CLIENT_REJECTION_OF_INTENT_INTERPRETATION",
                                  "AVOIDABLE_CEO_QUESTIONS",
                                  "WORKER_FAILURES_FROM_INCOMPLETE_TASK_CONTRACTS",
                                  "CLIENT_CONFUSION_AFTER_EXPLANATION"],
    }
    monkeypatch.setattr(mod, "load_yaml", lambda _path: data)
    assert mod.main() == 1  # fail closed on CANONICAL_MUTATION routing
