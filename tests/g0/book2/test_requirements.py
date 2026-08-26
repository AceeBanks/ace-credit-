"""B2.C11 tests — Requirement & Application Content Model.

Requirements represent the real grant-writing workload; responses link the
evidence that satisfies them; dynamic solicitation sections coexist with the
client's 18-section profile; proposal and business plan remain distinct.
"""
from __future__ import annotations

import copy

from prototype.g0.domain.models import (
    BusinessPlanSection,
    ProposalSection,
    Requirement,
    RequirementResponse,
)
from prototype.g0.domain.requirements import (
    completed_response_requires_link,
    section_links_resolve,
)
from tools.g0.validate_domain import (
    load_requirement_types,
    validate_requirement_types,
)

POLICY = load_requirement_types()


def test_live_requirement_types_passes():
    ok, report = validate_requirement_types(POLICY)
    assert ok, report["errors"]
    assert report["requirement_type_count"] == 8


def test_one_requirement_may_require_multiple_artifacts():
    req = Requirement("req-1", "opp_rev-1", "attachment", mandatory=True,
                      required_attachments=("art-a", "art-b", "art-c"))
    assert len(req.required_attachments) == 3
    assert req.required_attachments == ("art-a", "art-b", "art-c")


def test_one_artifact_satisfies_multiple_requirements_only_when_linked():
    shared = RequirementResponse("resp-1", "req-1", "section",
                                 artifact_version_id="artver-9")
    # the SAME artifact version explicitly linked to two requirements
    other = RequirementResponse("resp-2", "req-2", "section",
                                artifact_version_id="artver-9")
    assert shared.artifact_version_id == other.artifact_version_id
    # a third requirement with NO link does NOT get satisfied
    unlinked = RequirementResponse("resp-3", "req-3", "section",
                                   artifact_version_id=None)
    assert unlinked.artifact_version_id is None
    assert shared.requirement_id != other.requirement_id  # explicit per-requirement links


def test_proposal_and_business_plan_sections_remain_distinct():
    prop = ProposalSection("sec-1", profile_section_key="org_background", title="Org")
    bp = BusinessPlanSection("sec-2", business_plan_section_key="operations", title="Ops")
    assert type(prop) is not type(bp)
    assert not hasattr(bp, "profile_section_key")       # different schema
    assert prop.profile_section_key == "org_background"


def test_dynamic_solicitation_section_coexists_with_client_profile():
    # client 18-section profile key present...
    profiled = ProposalSection("sec-1", profile_section_key="budget_narrative", order=7)
    # ...and a funder-specific section with no profile key
    dynamic = ProposalSection("sec-2", requirement_id="req-99", title="Novel Funder Q",
                              order=99)
    assert profiled.profile_section_key is not None
    assert dynamic.profile_section_key is None
    assert dynamic.requirement_id == "req-99"            # solicitation-driven


def test_section_content_links_resolve_or_fail_closed():
    sec = ProposalSection("sec-1", content_link_refs=("fact-1", "claim-2", "stat-3"))
    assert section_links_resolve(sec, {"fact-1", "claim-2", "stat-3"}) == []
    broken = section_links_resolve(sec, {"fact-1"})
    assert broken == ["claim-2", "stat-3"]


def test_unsupported_partnership_cannot_be_invented_as_completed():
    # support-letter response claiming SATISFIED without a linked artifact
    invented = RequirementResponse("resp-1", "req-1", "support_letter",
                                   artifact_version_id=None, state="SATISFIED")
    assert completed_response_requires_link(invented) is False
    # with a real linked artifact it is validly complete
    real = RequirementResponse("resp-2", "req-1", "support_letter",
                               artifact_version_id="artver-5", state="SATISFIED")
    assert completed_response_requires_link(real) is True
    # an in-progress response is not yet claiming completion — no false alarm
    progress = RequirementResponse("resp-3", "req-1", "support_letter",
                                   artifact_version_id=None, state="IN_PROGRESS")
    assert completed_response_requires_link(progress) is True


# --- validator defect injection ------------------------------------------------

def test_missing_requirement_type_fails():
    data = copy.deepcopy(POLICY)
    data["requirement_types"] = [t for t in data["requirement_types"]
                                 if t["type"] != "narrative"]
    ok, report = validate_requirement_types(data)
    assert not ok
    assert any("requirement_types" in e for e in report["errors"])


def test_missing_section_family_fails():
    data = copy.deepcopy(POLICY)
    data["section_families"] = [f for f in data["section_families"]
                                if f["family"] != "proposal_section"]
    ok, report = validate_requirement_types(data)
    assert not ok
    assert any("proposal_section" in e for e in report["errors"])
