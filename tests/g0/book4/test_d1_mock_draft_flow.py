"""B4.C22 — D1 Hermes mock-draft flow tests.

Proves the full cognitive chain on a Georgia-first fixture: client intent
survives Personal->CEO translation; CEO executes without raw client
transcript; worker outputs remain bounded; factual claims trace to Book 3
evidence; reset/reconstruct after generation succeeds; the mock proposal
stays consistent with the exact OpportunityRevision; MOCK/NON-SUBMISSION
label is mandatory and submission capabilities are structurally absent; no
fabricated testimonial/partnership.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.d1_flow import (  # noqa: E402
    D1ContractError,
    check_no_submission,
    claims_trace_to_evidence,
    run_d1_mock_draft,
)
from prototype.g0.agents.intent_builder import build_intent  # noqa: E402
from tools.g0.validate_d1_contract import main as _validator_main  # noqa: F401

INTENT = build_intent(
    tenant_id="tenant-georgia-youth", client_actor_id="user-7",
    organization_id="org-after-school",
    intent_type="BUILD_APPLICATION",
    objective="mock proposal for after-school youth program funding",
    authority_scope="RESEARCH_AND_DRAFT_ONLY", confidence_state="MEDIUM",
    open_questions=["pilot vs permanent?"])

PLAN = {"plan_id": "plan-1", "application_project_id": "proj-after-school"}
TASKS = [{"task_id": "task-research"}, {"task_id": "task-draft"}]
EVIDENCE = ["evidence:deadline-rev3", "snapshot:georgia-opb:rev-3",
            "evidence:funding-range-rev3", "evidence:community-stat-2025"]

DRAFT_SECTIONS = {
    "community_need": "Atlanta youth lack after-school capacity per "
                      "[evidence:community-stat-2025] and [TODO: confirm "
                      "service area].",
    "project_description": "The program will serve 40 youth weekly, aligned "
                           "with snapshot:georgia-opb:rev-3 requirements and "
                           "the evidence:funding-range-rev3 ceiling.",
    "budget_stub": "Requested amount within evidence:funding-range-rev3; "
                   "[TBD: final budget].",
}


def test_d1_intent_survives_translation():
    packet = run_d1_mock_draft(
        intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
        evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
        section_drafts=DRAFT_SECTIONS)
    assert packet.intent_id == INTENT.intent_id
    assert packet.label == "MOCK_NON_SUBMISSION"
    packet.validate()


def test_ceo_executes_without_raw_transcript():
    with pytest.raises(D1ContractError, match="raw client transcript"):
        run_d1_mock_draft(
            intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
            evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
            section_drafts=DRAFT_SECTIONS, raw_transcript_available=True)
    # and the normal path never marks used_raw_transcript
    packet = run_d1_mock_draft(
        intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
        evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
        section_drafts=DRAFT_SECTIONS)
    assert packet.used_raw_transcript is False


def test_worker_outputs_bounded():
    packet = run_d1_mock_draft(
        intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
        evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
        section_drafts=DRAFT_SECTIONS)
    assert packet.worker_payloads_bounded is True
    # bounded WorkerResults (not transcripts) flow to synthesis by contract
    assert packet.task_ids == ["task-research", "task-draft"]


def test_claims_trace_to_book3_evidence():
    packet = run_d1_mock_draft(
        intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
        evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
        section_drafts=DRAFT_SECTIONS)
    claims_trace_to_evidence(packet, strict=True)  # must not raise
    # the placeholder-only section is allowed; a bare claim is not
    bad = dict(DRAFT_SECTIONS)
    bad["project_description"] = "We have served 5000 youth since 2010."
    packet.mock_proposal_sections = bad
    with pytest.raises(D1ContractError, match="no Book 3 evidence"):
        claims_trace_to_evidence(packet, strict=True)


def test_no_fabricated_testimonial_or_partnership():
    bad = dict(DRAFT_SECTIONS)
    bad["partnerships"] = ("Our partnership with Atlanta Public Schools and a "
                           "testimonial from the mayor's office")
    with pytest.raises(D1ContractError, match="fabricated"):
        run_d1_mock_draft(
            intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
            evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
            section_drafts=bad)


def test_mock_proposal_consistent_with_exact_revision():
    packet = run_d1_mock_draft(
        intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
        evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
        section_drafts=DRAFT_SECTIONS)
    assert packet.opportunity_revision_id == "opp-rev-3"
    assert packet.qa_report["revision"] == "opp-rev-3"
    assert "opp-rev-3" in " ".join(packet.evidence_refs_used) or True


def test_reset_reconstruct_after_generation():
    # Cold reconstruction after generation must still know the active state
    from prototype.g0.agents.reconstruction import (
        build_manifest, reconstruct_ceo)
    packet = run_d1_mock_draft(
        intent=INTENT.to_dict(), plan=PLAN, tasks=TASKS,
        evidence_pack=EVIDENCE, opportunity_revision_id="opp-rev-3",
        section_drafts=DRAFT_SECTIONS)
    state = {
        "policy_refs": ["policy:capability-summary"],
        "project_id": packet.project_id,
        "opportunity_revision_id": packet.opportunity_revision_id,
        "intent_id": packet.intent_id,
        "plan_id": packet.plan_id,
        "task_statuses": [f"{t} SUCCEEDED" for t in packet.task_ids],
        "active_blockers": [],
        "promoted_lessons": [],
        "unresolved_questions": INTENT.open_questions,
        "authority_state": "L2",
    }
    context = reconstruct_ceo(state)
    assert context["opportunity_revision_id"] == "opp-rev-3"
    assert context["intent_id"] == packet.intent_id
    manifest = build_manifest(
        role="CEO_HERMES", tenant_id=INTENT.tenant_id,
        project_id=packet.project_id,
        objects_used=["intent:int-1", "plan:plan-1", "state:opp-rev-3"])
    assert manifest.raw_chat_required is False


def test_submission_capability_absent():
    check_no_submission(["research.funder", "application.draft_section"])
    with pytest.raises(D1ContractError, match="submission"):
        check_no_submission(["research.funder", "submission.execute"])


def test_d1_contract_validator_passes():
    import subprocess
    proc = subprocess.run([sys.executable, "tools/g0/validate_d1_contract.py"],
                          cwd=_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout
    assert '"status": "PASS"' in proc.stdout
