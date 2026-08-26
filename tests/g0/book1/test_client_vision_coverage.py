"""B1.C12 tests — Client-Vision Capability Coverage Test.

Proves the constitution permits the product the client actually asked for:
every Phase 1 deliverable must have at least one legal capability path when
evaluated by the executable policy prototype. The test fails if any Phase 1
deliverable has no legal capability path (plan §15).

A legal path is a capability that the CEO actor (L2, tenant-scoped) can reach
at the policy decision point — ALLOW, or REQUIRE_APPROVAL where the plan
explicitly gates the deliverable behind human approval. Auto-submission must
have NO legal path in Phase 1.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from prototype.g0.policy.evaluator import evaluate
from prototype.g0.policy.models import (
    Actor,
    AuthorityLevel,
    Decision,
    PolicyContext,
)
from prototype.g0.policy.registry import PolicyRegistry

_ROOT = Path(__file__).resolve().parents[3]

TENANT = "tenant-alpha"
PROJECT = "proj-1"


def _ceo() -> Actor:
    return Actor("ceo-1", "ACTOR-HERMES-CEO", (TENANT,), AuthorityLevel.L2)


def _ctx(resource_type: str, *, project_id: str | None = PROJECT) -> PolicyContext:
    return PolicyContext(
        tenant_id=TENANT,
        project_id=project_id,
        resource_type=resource_type,
    )


# Resource type accepted by each Phase 1 deliverable capability (from the
# live registry). Updated in lockstep with capability_registry.yaml.
_CAP_RESOURCE = {
    "organization.read": "organization_profile",
    "organization.propose_update": "organization_profile",
    "application.create_draft_project": "application_project",
    "opportunity.search": "opportunity",
    "opportunity.fetch": "opportunity",
    "opportunity.snapshot": "opportunity",
    "research.funder": "research_pack",
    "research.program": "research_pack",
    "research.organization": "research_pack",
    "research.community": "research_pack",
    "research.winner": "research_pack",
    "match.explain": "match_result",
    "application.draft_full_proposal": "application_draft",
    "application.draft_business_plan": "business_plan_draft",
    "application.draft_pitch_deck": "pitch_deck_draft",
    "application.draft_goal_sheet": "goal_sheet_draft",
    "application.draft_section": "application_draft",
    "budget.create": "budget",
    "budget.render": "budget",
    "qa.requirement_coverage": "qa_report",
    "qa.cross_document_consistency": "qa_report",
    "qa.alignment": "qa_report",
    "qa.humanization": "application_draft",
    "application.prepare_submission_package": "submission_package",
    "application.submit": "submission_package",
    "submission.prepare": "submission_package",
    "submission.execute": "funder_portal",
    "submission.certify": "submission_package",
    "submission.sign": "submission_package",
    "application.update_internal": "application_project",
}

# Phase 1 client deliverables (plan §15). Each maps to one or more capabilities
# that collectively provide a legal path; approval_class is the strictest class
# among those capabilities (AP0/AP1 = immediate, AP2 = human approval gate).
CLIENT_REQUIREMENTS = [
    {
        "client_requirement_id": "CR-01",
        "requirement": "Accept business concept",
        "capability_ids": ["organization.propose_update",
                           "application.create_draft_project"],
        "minimum_authority": "L1",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-02",
        "requirement": "Search across eight grant categories",
        "capability_ids": ["opportunity.search"],
        "minimum_authority": "L2",
        "approval_class": "AP0",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-03",
        "requirement": "Produce visible grant-specific research",
        "capability_ids": ["research.funder", "research.program",
                           "research.organization", "research.community",
                           "match.explain"],
        "minimum_authority": "L2",
        "approval_class": "AP0",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-04",
        "requirement": "Research past winners where available",
        "capability_ids": ["research.winner"],
        "minimum_authority": "L2",
        "approval_class": "AP0",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-05",
        "requirement": "Generate a grant proposal",
        "capability_ids": ["application.draft_full_proposal"],
        "minimum_authority": "L2",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-06",
        "requirement": "Generate a distinct business plan",
        "capability_ids": ["application.draft_business_plan"],
        "minimum_authority": "L2",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-07",
        "requirement": "Generate pitch deck",
        "capability_ids": ["application.draft_pitch_deck"],
        "minimum_authority": "L2",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-08",
        "requirement": "Generate financials where required",
        "capability_ids": ["budget.create", "budget.render"],
        "minimum_authority": "L2",
        "approval_class": "AP0",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-09",
        "requirement": "Generate partnerships/testimonials where available",
        "capability_ids": ["application.draft_section"],
        "minimum_authority": "L2",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-10",
        "requirement": "Generate goal sheets",
        "capability_ids": ["application.draft_goal_sheet"],
        "minimum_authority": "L2",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-11",
        "requirement": "Run quality/humanization passes",
        "capability_ids": ["qa.requirement_coverage",
                           "qa.cross_document_consistency", "qa.alignment",
                           "qa.humanization"],
        "minimum_authority": "L2",
        "approval_class": "AP1",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": [],
    },
    {
        "client_requirement_id": "CR-12",
        "requirement": "Output a submission-ready package",
        "capability_ids": ["application.prepare_submission_package"],
        "minimum_authority": "L2",
        "approval_class": "AP2",
        "book_implemented_later": False,
        "constitution_allows": True,
        "blocked_by": ["human approval (LAW-B1-012) — never auto-submitted"],
    },
    {
        "client_requirement_id": "CR-13",
        "requirement": "NOT auto-submit",
        "capability_ids": ["application.submit", "submission.prepare",
                           "submission.execute", "submission.certify",
                           "submission.sign"],
        "minimum_authority": "L5",
        "approval_class": "APX",
        "book_implemented_later": True,
        "constitution_allows": False,      # deliberately: no legal path in Phase 1
        "blocked_by": ["APX / DISABLED — structurally prohibited (CD-003)"],
    },
]


@pytest.fixture(scope="module")
def reg() -> PolicyRegistry:
    return PolicyRegistry.load()


def _path_result(reg, capability_id: str) -> str:
    """Evaluate one capability as CEO at L2; returns Decision value or reason."""
    result = evaluate(reg, _ceo(), capability_id,
                      _ctx(_CAP_RESOURCE[capability_id]))
    return result.decision.value


def test_matrix_covers_all_phase1_deliverables():
    ids = [r["client_requirement_id"] for r in CLIENT_REQUIREMENTS]
    assert ids == [f"CR-{n:02d}" for n in range(1, 14)]
    assert all(r["constitution_allows"] for r in CLIENT_REQUIREMENTS[:-1])
    assert CLIENT_REQUIREMENTS[-1]["constitution_allows"] is False


def test_matrix_capabilities_registered():
    reg = PolicyRegistry.load()
    caps = {c.capability_id for c in reg._capabilities.values()}
    for req in CLIENT_REQUIREMENTS:
        for cid in req["capability_ids"]:
            assert cid in caps, f"{req['client_requirement_id']}: {cid} not registered"
            assert cid in _CAP_RESOURCE, f"{req['client_requirement_id']}: {cid} missing resource mapping"


def test_every_deliverable_has_a_legal_capability_path(reg):
    """Each non-submission Phase 1 deliverable reaches ALLOW or REQUIRE_APPROVAL."""
    for req in CLIENT_REQUIREMENTS[:-1]:
        outcomes = [_path_result(reg, cid) for cid in req["capability_ids"]]
        legal = [o for o in outcomes if o in {Decision.ALLOW.value,
                                              Decision.REQUIRE_APPROVAL.value}]
        assert legal, (
            f"{req['client_requirement_id']} ({req['requirement']}) has no legal "
            f"capability path; got {dict(zip(req['capability_ids'], outcomes))}"
        )


def test_submission_has_no_legal_path(reg):
    """CR-13: every submission capability DENYs at CEO L2 in Phase 1."""
    req = CLIENT_REQUIREMENTS[-1]
    for cid in req["capability_ids"]:
        result = evaluate(reg, _ceo(), cid, _ctx(_CAP_RESOURCE[cid]))
        assert result.decision is Decision.DENY, \
            f"{cid} must DENY, got {result.decision}"


def test_submission_capabilities_structurally_disabled(reg):
    """Registry evidence: whole submission family is DISABLED/APX (CD-003)."""
    for cid in ("application.submit", "submission.prepare", "submission.execute",
                "submission.certify", "submission.sign"):
        cap = reg.get_capability(cid)
        assert cap.phase_status == "DISABLED", cid
        assert cap.approval_class == "APX", cid


def test_drafting_is_legal_at_l2(reg):
    """LAW-B1-013: drafting must be reachable by CEO at L2."""
    for cid in ("application.draft_full_proposal", "application.draft_business_plan",
                "application.draft_pitch_deck", "application.draft_goal_sheet",
                "application.draft_section"):
        cap = reg.get_capability(cid)
        assert cap.phase_status == "ENABLED", cid
        assert AuthorityLevel.rank(cap.minimum_level) <= AuthorityLevel.rank(AuthorityLevel.L2)
        result = evaluate(reg, _ceo(), cid, _ctx(_CAP_RESOURCE[cid]))
        assert result.decision in (Decision.ALLOW, Decision.REQUIRE_APPROVAL), cid


def test_submission_ready_package_is_approval_gated(reg):
    """CR-12 legal path requires human approval; never silent."""
    result = evaluate(reg, _ceo(), "application.prepare_submission_package",
                      _ctx("submission_package"))
    assert result.decision is Decision.REQUIRE_APPROVAL
