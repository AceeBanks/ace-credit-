"""B2.C7 tests — State Machine Catalog.

Illegal transitions rejected; submission unreachable in Phase 1; stale
eligibility blocks SUBMISSION_READY; unsatisfied mandatory requirements
block readiness; superseded revision triggers re-evaluation.
"""
from __future__ import annotations

import copy

from prototype.g0.domain.transitions import (
    can_transition,
    revision_stale_blocks,
    submission_ready_gate,
)
from tools.g0.validate_domain import load_state_machines, validate_state_machines


def _sm(name: str) -> dict:
    return next(m for m in load_state_machines()["state_machines"]
                if m["state_machine"] == name)


def test_live_state_machines_pass():
    ok, report = validate_state_machines(load_state_machines())
    assert ok, report["errors"]
    assert report["state_machine_count"] >= 6


def test_required_machines_present():
    names = {m["state_machine"] for m in load_state_machines()["state_machines"]}
    assert {"opportunity", "eligibility_decision", "application_project",
            "requirement", "artifact", "canonical_fact"} <= names


def test_illegal_transition_rejected():
    sm = _sm("application_project")
    verdict = can_transition(sm, "IDEA", "QA")   # jump without intermediate states
    assert not verdict.allowed
    assert "no transition" in verdict.reason


def test_legal_transition_allowed():
    sm = _sm("application_project")
    v = can_transition(sm, "IDEA", "QUALIFYING", capability="application.create_draft_project",
                       authority_level="L2")
    assert v.allowed, v.reason


def test_submission_unavailable_in_phase1():
    sm = _sm("application_project")
    v = can_transition(sm, "SUBMISSION_READY", "SUBMITTED", phase1=True,
                       authority_level="L5")
    assert not v.allowed
    assert "future state" in v.reason


def test_wrong_capability_rejected():
    sm = _sm("application_project")
    v = can_transition(sm, "IDEA", "QUALIFYING", capability="research.winner")
    assert not v.allowed
    assert v.capability == "application.create_draft_project"


def test_insufficient_authority_rejected():
    sm = _sm("canonical_fact")
    v = can_transition(sm, "PROPOSED", "PROMOTED", capability="evidence.resolve_conflict",
                       authority_level="L2")
    assert not v.allowed
    assert "authority" in v.reason


def test_precondition_gate():
    sm = _sm("application_project")
    v = can_transition(sm, "HUMAN_REVIEW", "SUBMISSION_READY",
                       capability="application.prepare_submission_package",
                       authority_level="L2",
                       satisfied_preconditions=set())
    assert not v.allowed
    assert "precondition" in v.reason


def test_stale_eligibility_blocks_submission_ready():
    assert submission_ready_gate(_sm("application_project"),
                                 eligibility_ineligible=True,
                                 revision_stale=False,
                                 mandatory_unsatisfied=False) is False


def test_unsatisfied_mandatory_requirement_blocks_readiness():
    assert submission_ready_gate(_sm("application_project"),
                                 eligibility_ineligible=False,
                                 revision_stale=False,
                                 mandatory_unsatisfied=True) is False


def test_all_preconditions_satisfied_gate_passes():
    assert submission_ready_gate(_sm("application_project"),
                                 eligibility_ineligible=False,
                                 revision_stale=False,
                                 mandatory_unsatisfied=False) is True


def test_stale_revision_forces_review_before_research_to_drafting():
    sm = _sm("application_project")
    blocked = revision_stale_blocks(sm, "DRAFTING")
    assert any("RESEARCH->DRAFTING" in b for b in blocked)


def test_duplicate_machine_fails():
    data = copy.deepcopy(load_state_machines())
    data["state_machines"].append(dict(data["state_machines"][0]))
    ok, report = validate_state_machines(data)
    assert not ok
    assert any("duplicate state machine" in e for e in report["errors"])


def test_unknown_precondition_fails():
    data = copy.deepcopy(load_state_machines())
    data["state_machines"][0]["transitions"][0]["preconditions"].append("vibes")
    ok, report = validate_state_machines(data)
    assert not ok
    assert any("unknown precondition" in e for e in report["errors"])


def test_unknown_transition_target_fails():
    data = copy.deepcopy(load_state_machines())
    data["state_machines"][0]["transitions"][0]["to"] = "NOPE"
    ok, report = validate_state_machines(data)
    assert not ok
    assert any("unknown state" in e for e in report["errors"])
