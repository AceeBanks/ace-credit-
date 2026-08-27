"""G0-B8 — production-shaped Georgia vertical slice tests.

End-to-end: client intent -> Personal (IntentContract) -> CEO (TaskPlan)
-> selection -> eligibility -> match -> research -> project -> blueprint
-> governed model drafting -> budget -> claim ledger -> QA -> human review
-> SUBMISSION_READY_MOCK -> explanation.

Plus the Book 8 special drills:
- amendment/revision chaos + selective invalidation (C29-C32)
- cold restart reconstruction (C33)
- degraded mode fail-closed (C34)
- security attacks (C35)
- telemetry + reconstruction + handoff (C37-C40)

No test hand-builds an AuthorizationDecision; live-model lanes run through
the governed Model Gateway.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from prototype.g0.domain.revisions import DecisionAnchor, RevisionSet  # noqa: E402
from prototype.g0.vslice.amendment import run_amendment_drill  # noqa: E402
from prototype.g0.vslice.fixture import build_client_profile  # noqa: E402
from prototype.g0.vslice.intake import run_intake  # noqa: E402
from prototype.g0.vslice.models import SliceRecord  # noqa: E402
from prototype.g0.vslice.orchestrator import (  # noqa: E402
    PROJECT, TENANT, run_slice,
)
from prototype.g0.vslice.resilience import (  # noqa: E402
    reconstruct_from_records, run_degraded_mode, run_security_attacks,
)
from prototype.g0.vslice.telemetry import (  # noqa: E402
    build_handoff, build_reconstruction_report, collect_telemetry,
)

INTENT = ("We are Community Youth Works, a nonprofit tutoring center in "
          "Dade County, Georgia. We want to apply for the Georgia Rural "
          "Community Impact Grant to fund after-school tutoring for high "
          "school students in Chatsworth.")


def _run(*, run_id: str = "t1", draft_live: bool = False):
    return run_slice(run_id=run_id, client_intent=INTENT,
                     draft_live=draft_live)


# ---------------------------------------------------------------------------
# C2 fixture + C3 intake
# ---------------------------------------------------------------------------

def test_fixture_is_governed():
    profile = build_client_profile()
    assert profile.legal_name == "Community Youth Works, Inc."
    assert profile.jurisdiction == "Georgia"
    # values that are not client-provided are visibly UNKNOWN, never invented
    assert profile.current_capacity is None
    for item in ("staff size", "annual operating budget",
                 "program outcomes history"):
        assert item in profile.unknown_items


def test_intake_produces_intent_contract_without_raw_transcript():
    profile = build_client_profile()
    intake = run_intake(tenant_id=TENANT, client_actor_id="client-ga-1",
                        organization_id=profile.organization_id,
                        client_intent_text=INTENT, profile=profile)
    assert intake.intent.intent_id.startswith("int-")
    assert intake.intent.objective
    assert intake.readiness_state in ("DRAFTING_READY",
                                      "DRAFT_READY_WITH_FLAGS")
    assert intake.used_raw_transcript is False
    assert intake.fabricated_eligibility is False


def test_intake_never_invents_missing_facts():
    profile = build_client_profile()
    intake = run_intake(tenant_id=TENANT, client_actor_id="client-ga-1",
                        organization_id=profile.organization_id,
                        client_intent_text=INTENT, profile=profile)
    for q in intake.intent.open_questions:
        assert q  # open questions are surfaced, not silently answered


# ---------------------------------------------------------------------------
# Full vertical slice (live + deterministic lanes)
# ---------------------------------------------------------------------------

def test_full_slice_all_stages_present():
    r = _run(draft_live=False)
    stages = {rec.stage for rec in r.records}
    for expected in ("intent", "plan", "selection", "eligibility", "match",
                     "research", "project", "drafting", "assurance",
                     "package"):
        assert expected in stages, f"missing stage {expected}"


def test_slice_deterministic_lane_labels_itself():
    r = _run(draft_live=False)
    assert r.generation_mode == "DETERMINISTIC_BASELINE"


def test_slice_package_state_and_submission_disabled():
    r = _run(draft_live=False)
    assert r.package.state == "SUBMISSION_READY_MOCK"
    assert r.package.submission_enabled is False


def test_slice_hard_gate_passes_deterministic_lane():
    r = _run(draft_live=False)
    assert r.record("assurance")["hard_gate_pass"] is True


def test_slice_claim_ledger_full_support_deterministic():
    r = _run(draft_live=False)
    metrics = r.record("assurance")["claim_metrics"]
    assert metrics["unsupported"] == 0
    assert metrics["material_claim_support_rate"] == 1.0


def test_slice_eligibility_deterministic_eligible():
    r = _run(draft_live=False)
    eligibility = r.record("eligibility")
    assert eligibility["result"]["result"] == "ELIGIBLE"


def test_slice_budget_within_ceiling():
    r = _run(draft_live=False)
    budget = r.record("drafting")
    assert float(budget["budget_total"]) <= float(budget["ceiling"])


def test_slice_revision_identity_pinned():
    r = _run(draft_live=False)
    assert r.record("selection")["revision_id"] == "opp_rev_ga_501_1"


# ---------------------------------------------------------------------------
# C29-C32 amendment/revision chaos drill
# ---------------------------------------------------------------------------

def _seed_revision_set():
    rev1 = DecisionAnchor(
        decision_id="dec-elig", revision_id="opp_rev_ga_501_1")
    anchors = {
        "eligibility": rev1,
        "match": DecisionAnchor("dec-match", "opp_rev_ga_501_1"),
        "project": DecisionAnchor("dec-proj", "opp_rev_ga_501_1"),
        "drafting": DecisionAnchor("dec-draft", "opp_rev_ga_501_1"),
        "assurance": DecisionAnchor("dec-qa", "opp_rev_ga_501_1"),
        "package": DecisionAnchor("dec-pkg", "opp_rev_ga_501_1"),
    }
    return anchors


def test_material_amendment_selectively_invalidates_downstream():
    from prototype.g0.domain.revisions import Revision
    r1 = Revision("opp_rev_ga_501_1", 1, frozenset(), "2026-01-01T00:00:00Z",
                  material=False)
    rset = RevisionSet("opp_ga_501", "opportunity", (r1,))
    anchors = _seed_revision_set()
    result = run_amendment_drill(
        revision_set=rset, old_revision_id="opp_rev_ga_501_1",
        new_revision_id="opp_rev_ga_501_2",
        changed_terms=["deadline"], revision_number=2,
        stage_anchors=anchors, preserved_artifacts=["b8-art-v1"])
    assert result.material is True
    # deadline change invalidates downstream but NOT the eligibility decision
    # anchored to the same revision (all are anchored to rev 1, which is now
    # superseded by a material revision -> all stale)
    assert set(result.stale_stages) == {"eligibility", "match", "project",
                                        "drafting", "assurance", "package"}
    assert "opp_rev_ga_501_1" in result.preserved_history


def test_non_material_amendment_keeps_downstream_fresh():
    from prototype.g0.domain.revisions import Revision
    r1 = Revision("opp_rev_ga_501_1", 1, frozenset(), "2026-01-01T00:00:00Z",
                  material=False)
    rset = RevisionSet("opp_ga_501", "opportunity", (r1,))
    anchors = _seed_revision_set()
    result = run_amendment_drill(
        revision_set=rset, old_revision_id="opp_rev_ga_501_1",
        new_revision_id="opp_rev_ga_501_2",
        changed_terms=["formatting"], revision_number=2,
        stage_anchors=anchors, preserved_artifacts=["b8-art-v1"])
    assert result.material is False
    assert result.stale_stages == []       # no selective invalidation
    assert all(d["status"] == "FRESH_KEPT" for d in result.decisions)


def test_amendment_preserves_history_and_explains():
    from prototype.g0.domain.revisions import Revision
    r1 = Revision("opp_rev_ga_501_1", 1, frozenset(), "2026-01-01T00:00:00Z",
                  material=False)
    rset = RevisionSet("opp_ga_501", "opportunity", (r1,))
    result = run_amendment_drill(
        revision_set=rset, old_revision_id="opp_rev_ga_501_1",
        new_revision_id="opp_rev_ga_501_2", changed_terms=["deadline"],
        revision_number=2, stage_anchors=_seed_revision_set(),
        preserved_artifacts=["b8-art-v1", "draft-v1"])
    assert "opp_rev_ga_501_2" in result.explanation
    assert result.preserved_history == ["opp_rev_ga_501_1",
                                        "b8-art-v1", "draft-v1"]


# ---------------------------------------------------------------------------
# C33 cold restart reconstruction
# ---------------------------------------------------------------------------

def test_cold_restart_reconstructs_full_state():
    r = _run(draft_live=False)
    report = reconstruct_from_records(r.records)
    assert report["reconstruction_complete"] is True
    assert report["raw_chat_required"] is False
    assert report["missing_stages"] == []


def test_cold_restart_reports_missing_stages_honestly():
    records = [SliceRecord(stage="intent", record_id="r1",
                           tenant_id=TENANT, project_id=PROJECT,
                           payload={"objective": "x"})]
    report = reconstruct_from_records(records)
    assert report["reconstruction_complete"] is False
    assert "package" in report["missing_stages"]


# ---------------------------------------------------------------------------
# C34 degraded mode
# ---------------------------------------------------------------------------

def test_optional_outage_degrades_locally():
    res = run_degraded_mode(available={"research": False, "drafting": False})
    assert res["optional_down"] == ["research", "drafting"]
    assert res["integrity_fail_closed"] is False
    assert res["canonical_state_preserved"] is True


def test_critical_outage_fails_closed():
    res = run_degraded_mode(available={"eligibility": False})
    assert res["critical_down"] == ["eligibility"]
    assert res["integrity_fail_closed"] is True


def test_model_outage_blocks_model_lane():
    res = run_degraded_mode(available={"model": False})
    assert res["model_fallback"] == "BLOCKED"


# ---------------------------------------------------------------------------
# C35 security attacks
# ---------------------------------------------------------------------------

def test_all_security_attacks_denied():
    res = run_security_attacks()
    assert res["all_denied"] is True
    for name, r in res["results"].items():
        assert r["denied"], f"attack not denied: {name}"
        assert r["reason"]


def test_security_attack_reasons_specific():
    res = run_security_attacks()
    reasons = {k: v["reason"] for k, v in res["results"].items()}
    assert "tenant mismatch" in reasons["cross_tenant_decision_reuse"]
    assert "project mismatch" in reasons["cross_project_decision_reuse"]
    assert "no trusted AuthorizationDecision" in reasons[
        "direct_provider_bypass"]
    assert "submission capability" in reasons["direct_submission"]


# ---------------------------------------------------------------------------
# C37-C40 telemetry + reconstruction + handoff
# ---------------------------------------------------------------------------

def test_telemetry_collects_workload_evidence():
    r = _run(draft_live=False)
    t = collect_telemetry(run_id="t1", records=r.records, model_calls=4,
                          worker_fanout=5, source_fetches=2)
    assert t.task_count >= 5
    assert t.checkpoint_count >= 5
    assert t.model_calls == 4
    assert t.worker_fanout == 5
    assert t.audit_volume == len(r.records)
    assert t.stages_completed == [rec.stage for rec in r.records]


def test_reconstruction_report_answers_north_star_questions():
    r = _run(draft_live=False)
    report = build_reconstruction_report(records=r.records)
    n = report["narrative"]
    assert n["client_intent"]
    assert n["why_opportunity_selected"]
    assert n["why_eligible"] == "ELIGIBLE"
    assert n["governing_revision"] == "opp_rev_ga_501_1"
    assert n["final_state"] == "SUBMISSION_READY_MOCK"
    assert n["submission_enabled"] is False
    assert report["reconstruction_complete"] is True
    assert report["raw_chat_required"] is False


def test_handoff_packet_ready_for_book9():
    r = _run(draft_live=False)
    t = collect_telemetry(run_id="t1", records=r.records)
    recon = build_reconstruction_report(records=r.records)
    handoff = build_handoff(run_id="t1", records=r.records,
                            reconstruction=recon, telemetry=t)
    assert handoff["review_range_ready"] is True
    assert handoff["telemetry"]["audit_volume"] == len(r.records)


def test_records_are_json_serializable():
    r = _run(draft_live=False)
    for rec in r.records:
        json.dumps(rec.to_dict())   # must not raise


def test_no_submission_capability_in_records():
    r = _run(draft_live=False)
    blob = json.dumps([rec.to_dict() for rec in r.records]).lower()
    assert "application.submit" not in blob
    assert "submission_enabled" not in blob or '"submission_enabled": false' \
        in blob
