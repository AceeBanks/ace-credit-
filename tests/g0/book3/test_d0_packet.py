"""B3.C23 tests — D0 Shadow Draft Data Packet.

Fail-closed:
  * all nine packet sections are required;
  * no missing factual input may be silently invented — every fact carries a
    source ref or an explicit NEEDS_CLIENT_INPUT / NEEDS_SOURCE / PROVISIONAL /
    UNSUPPORTED_DO_NOT_USE state;
  * the packet records the exact OpportunityRevision;
  * packets regenerate deterministically from the packet alone (no agent
    memory);
  * requirement coverage is measurable.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_health_d0 import (
    REQUIRED_FACT_STATES,
    REQUIRED_OUTPUT_LABELS,
    REQUIRED_PACKET_SECTIONS,
    REQUIRED_SUCCESS_CRITERIA,
    validate_d0,
)
from prototype.g0.source.d0_packet import (
    D0Packet,
    PacketFact,
    requirement_coverage,
)

CFG = SOURCE_CONFIG_DIR / "d0_data_packet.yaml"


def _sections(overrides: dict | None = None) -> dict:
    sections = {
        "client_profile_fixture": [
            PacketFact("org_name", "Community Youth Works, Inc.", source_ref="claim_org_name")],
        "georgia_opportunity": [
            PacketFact("deadline", "2026-10-15", source_ref="snap_ga_501")],
        "opportunity_requirements": [
            PacketFact("req_narrative", "grant narrative required", source_ref="norm_req_1"),
            PacketFact("req_budget", "budget required", source_ref="norm_req_2")],
        "eligibility": [
            PacketFact("eligible", "true", source_ref="eldec_ga_501")],
        "funder_program_research": [
            PacketFact("funder_priority", "rural impact", source_ref="claim_funder_1")],
        "historical_winner_award_research": [
            PacketFact("prior_award", "50000", source_ref="snap_award_ga")],
        "community_impact_statistics": [
            PacketFact("poverty_rate", "14.8", source_ref="stat_13121")],
        "budget_assumptions": [
            PacketFact("budget_total", "49500", fact_state="NEEDS_CLIENT_INPUT")],
        "proposal_profile": [
            PacketFact("section_count", "18", fact_state="PROVISIONAL")],
    }
    if overrides:
        sections.update(overrides)
    return sections


def _packet(**kw) -> D0Packet:
    base = dict(packet_id="packet_d0_1", tenant_id="tenant_ga",
                opportunity_revision_id="opp_rev_ga_501_1",
                sections=_sections())
    base.update(kw)
    return D0Packet(**base)


def test_validator_live_config_passes():
    errors: list[str] = []
    validate_d0(load_yaml(CFG), errors)
    assert errors == []


def test_config_matches_prototype_constants():
    cfg = load_yaml(CFG)
    assert cfg["packet_sections"] == REQUIRED_PACKET_SECTIONS
    assert set(cfg["output_labels"]) == REQUIRED_OUTPUT_LABELS
    assert set(cfg["fact_states"]) == REQUIRED_FACT_STATES
    assert set(cfg["success_criteria"]) == REQUIRED_SUCCESS_CRITERIA


def test_complete_packet_validates():
    packet = _packet()
    assert packet.validation_errors() == []


def test_missing_section_fails():
    sections = _sections()
    del sections["budget_assumptions"]
    errors = _packet(sections=sections).validation_errors()
    assert any("missing sections" in e for e in errors)


def test_unsupported_fact_fails():
    sections = _sections({"proposal_profile": [
        PacketFact("testimonial", "Our partner loves us")]})  # no source, no state
    errors = _packet(sections=sections).validation_errors()
    assert any("unsupported fact" in e for e in errors)


def test_explicit_fact_state_allows_unsourced_fact():
    sections = _sections({"proposal_profile": [
        PacketFact("org_story", "", fact_state="NEEDS_CLIENT_INPUT")]})
    assert _packet(sections=sections).validation_errors() == []


def test_missing_revision_fails():
    errors = _packet(opportunity_revision_id="").validation_errors()
    assert any("OpportunityRevision" in e for e in errors)


def test_missing_mock_labels_fail():
    errors = _packet(labels=frozenset(("MOCK",))).validation_errors()
    assert any("NON_SUBMISSION" in e for e in errors)


def test_packet_regenerates_deterministically():
    p1 = _packet()
    rebuilt = D0Packet(
        packet_id=p1.packet_id, tenant_id=p1.tenant_id,
        opportunity_revision_id=p1.opportunity_revision_id,
        sections=p1.sections, labels=p1.labels, created_at="")
    assert rebuilt.determinism_key() == p1.determinism_key()


def test_requirement_coverage_measurable():
    packet = _packet()
    covered, total = requirement_coverage(packet, ["req_narrative", "req_budget",
                                                   "req_attachments"])
    assert (covered, total) == (2, 3)
