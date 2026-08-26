"""B3.C24 tests — D0 Shadow Draft Harness Specification.

The harness is SPECIFIED, not productionized. Fail-closed:
  * the harness flow is exactly the ten specified stages in order;
  * model permissions are L2 internal only — no email/send/submission tools;
  * the hard stop is declared: D0 output can never be represented as
    submission-ready;
  * a packet built from the Book 2 Georgia draft bundle reconstructs without
    agent memory and coverage is measurable end-to-end.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_health_d0 import (
    REQUIRED_HARNESS_FLOW,
    validate_d0,
)
from prototype.g0.source.d0_packet import (
    D0Packet,
    PacketFact,
    packet_regenerable,
    requirement_coverage,
)

CFG = SOURCE_CONFIG_DIR / "d0_data_packet.yaml"


def test_validator_live_config_passes():
    errors: list[str] = []
    validate_d0(load_yaml(CFG), errors)
    assert errors == []


def test_harness_flow_is_exact_spec():
    cfg = load_yaml(CFG)
    assert cfg["harness_flow"] == REQUIRED_HARNESS_FLOW
    # the flow ends with a QA report before any client artifact is claimed
    assert cfg["harness_flow"][-1] == "d0_qa_report"
    assert "mock_proposal_artifact" in cfg["harness_flow"]


def test_model_permissions_l2_only_no_submission():
    cfg = load_yaml(CFG)
    perms = cfg["model_permissions"]
    assert "L2_INTERNAL_ONLY" in perms
    assert "NO_EMAIL_SEND_SUBMISSION" in perms
    # submission tooling is never present in the flow
    for stage in cfg["harness_flow"]:
        assert "submit" not in stage and "email" not in stage


def test_hard_stop_declared():
    cfg = load_yaml(CFG)
    assert "evaluation artifact" in cfg["hard_stop"].lower()
    assert "submission-ready" in cfg["hard_stop"].lower()


def test_book2_georgia_bundle_feeds_d0_packet():
    """The D0 packet is the source-governed evidence behind the Book 2
    DraftContextBundle: the Georgia fixture's exact revision + eligibility are
    reconstructable from the packet alone."""
    from prototype.g0.domain.fixtures.georgia import (
        GA_DECISION,
        GA_OPP_REV1,
        GA_PROJECT,
    )
    sections = {
        "client_profile_fixture": [PacketFact("org_name", "Community Youth Works, Inc.",
                                              source_ref="claim_org_name")],
        "georgia_opportunity": [PacketFact("opportunity_id", GA_OPP_REV1.opportunity_id,
                                           source_ref="snap_ga_501")],
        "opportunity_requirements": [PacketFact("req_narrative", "narrative required",
                                                source_ref="norm_req_1")],
        "eligibility": [PacketFact("eligible", "true",
                                   source_ref=GA_DECISION.decision_id)],
        "funder_program_research": [PacketFact("funder_priority", "rural impact",
                                               fact_state="PROVISIONAL")],
        "historical_winner_award_research": [PacketFact("prior_award", "50000",
                                                        fact_state="NEEDS_SOURCE")],
        "community_impact_statistics": [PacketFact("poverty_rate", "14.8",
                                                   fact_state="NEEDS_SOURCE")],
        "budget_assumptions": [PacketFact("budget_total", "49500",
                                          fact_state="NEEDS_CLIENT_INPUT")],
        "proposal_profile": [PacketFact("section_count", "18",
                                        fact_state="PROVISIONAL")],
    }
    packet = D0Packet(
        packet_id="packet_ga_501", tenant_id="tenant_ga",
        opportunity_revision_id=GA_PROJECT.opportunity_revision_id,
        sections=sections)
    assert packet.validation_errors() == []
    # exact revision visible + regenerable without agent memory
    assert packet.opportunity_revision_id == GA_OPP_REV1.revision_id
    assert packet_regenerable(packet) is True
    # requirement coverage measurable
    covered, total = requirement_coverage(packet, ["req_narrative"])
    assert (covered, total) == (1, 1)
