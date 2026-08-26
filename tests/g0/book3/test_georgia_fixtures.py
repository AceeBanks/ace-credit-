"""B3.C17 tests — Georgia source profiles (first state-level proof).

Fail-closed:
  * the Georgia source lanes are declared with the crawled-state rule and
    namespaced-identifier policy;
  * every Georgia namespace exists in the Book 2 catalog (GA_PORTAL etc.);
  * Georgia opportunity fixtures normalize into the Book 2 core ontology —
    standard GrantOpportunity + OpportunityRevision, never a GeorgiaGrant root;
  * eligibility decisions anchor to the exact Georgia opportunity revision;
  * a changed Georgia webpage produces a new snapshot + governed change event;
  * a crawled Georgia page can never outrank the current official solicitation
    for solicitation terms (fact-specific precedence).
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_domain import load_identifier_namespaces
from tools.g0.validate_source_profiles import (
    EXPECTED_GEORGIA_LANES,
    FORBIDDEN_ROOT_ENTITIES,
    validate_georgia,
)
from prototype.g0.source.precedence import Claim, resolve
from prototype.g0.source.snapshot import CaptureMethod, build_snapshot
from prototype.g0.source.source_change import (
    ChangeClass,
    Materiality,
    SourceChangeEvent,
    classify_change,
)

GA_CFG = SOURCE_CONFIG_DIR / "georgia_profiles.yaml"


def _errors() -> list[str]:
    errors: list[str] = []
    validate_georgia(load_yaml(GA_CFG), errors)
    return errors


def test_validator_live_config_passes():
    assert _errors() == []


def test_required_georgia_lanes_present():
    profiles = load_yaml(GA_CFG)["source_profiles"]
    assert EXPECTED_GEORGIA_LANES <= set(profiles.keys())


def test_crawled_state_rule_and_identifier_policy_declared():
    cfg = load_yaml(GA_CFG)
    assert cfg["crawled_state_rule"]
    assert cfg["georgia_identifier_policy"]


def test_no_georgia_grant_root_entity():
    cfg = load_yaml(GA_CFG)
    keys = [str(k).lower() for k in cfg["source_profiles"].keys()]
    for bad in FORBIDDEN_ROOT_ENTITIES:
        assert bad.lower() not in keys, f"forbidden root entity {bad!r}"


def test_georgia_namespaces_in_book2_catalog():
    catalog = {ns["namespace_id"]
               for ns in load_identifier_namespaces()["namespaces"]}
    profiles = load_yaml(GA_CFG)["source_profiles"]
    for pid, p in profiles.items():
        for ns in p["identifier_namespaces"]:
            assert ns in catalog, f"{pid}: namespace {ns} not in Book 2 catalog"
        assert p["capture_method"] in {"HTML", "API_JSON", "BULK_FILE"}


def test_georgia_opportunity_normalizes_to_book2_core():
    from prototype.g0.domain.fixtures.georgia import (
        GA_OPP,
        GA_OPP_REV1,
        GA_PROJECT,
    )
    from prototype.g0.domain.models import (
        ApplicationProject,
        GrantOpportunity,
        OpportunityRevision,
    )
    # standard core types — no GeorgiaGrant root
    assert isinstance(GA_OPP, GrantOpportunity)
    assert isinstance(GA_OPP_REV1, OpportunityRevision)
    assert isinstance(GA_PROJECT, ApplicationProject)
    assert GA_OPP_REV1.opportunity_id == GA_OPP.opportunity_id
    # the application project targets the exact Georgia revision
    assert GA_PROJECT.opportunity_revision_id == GA_OPP_REV1.revision_id


def test_georgia_eligibility_anchors_to_exact_revision():
    from prototype.g0.domain.fixtures.georgia import GA_DECISION, GA_OPP_REV1
    assert GA_DECISION.opportunity_revision_id == GA_OPP_REV1.revision_id


def test_changed_georgia_webpage_new_snapshot_and_change_event():
    snap1 = build_snapshot(
        snapshot_id="snap_ga_1", source_id="src_ga_opb_grants_portal",
        resource_type="opportunity", external_resource_id="ga-501",
        canonical_url="https://opb.georgia.gov/grants/ga-501",
        request_id="req-1", retrieved_at="2026-08-01T00:00:00Z",
        raw_object_uri="obj://ga-501-v1", raw_bytes=b"deadline 2026-10-15",
        adapter_name="ga_portal_crawler", adapter_version="1.0.0",
        capture_method=CaptureMethod.HTML)
    snap2 = build_snapshot(
        snapshot_id="snap_ga_2", source_id="src_ga_opb_grants_portal",
        resource_type="opportunity", external_resource_id="ga-501",
        canonical_url="https://opb.georgia.gov/grants/ga-501",
        request_id="req-2", retrieved_at="2026-08-02T00:00:00Z",
        raw_object_uri="obj://ga-501-v2", raw_bytes=b"deadline 2026-10-29",
        adapter_name="ga_portal_crawler", adapter_version="1.0.0",
        capture_method=CaptureMethod.HTML,
        previous_snapshot_id=snap1.snapshot_id)
    # content changed -> different content hash, lineage preserved
    assert snap1.raw_hash != snap2.raw_hash
    assert snap2.previous_snapshot_id == snap1.snapshot_id
    # deadline field change is application-critical: P0 change event
    materiality = classify_change(ChangeClass.UPDATED, ["deadline_changed"],
                                  ["deadline"])
    assert materiality is Materiality.P0
    event = SourceChangeEvent(
        change_event_id="chg_ga_1", source_id="src_ga_opb_grants_portal",
        entity_type="opportunity", entity_id="ga-501",
        old_snapshot_id=snap1.snapshot_id, new_snapshot_id=snap2.snapshot_id,
        detected_at="2026-08-02T01:00:00Z", change_class=ChangeClass.UPDATED,
        materiality=materiality.value, affected_fields=["deadline"],
        semantic_diff_ref="diff://ga-501-deadline")
    assert event.materiality == "P0"


def test_crawler_cannot_outrank_official_solicitation():
    matrix = load_yaml(SOURCE_CONFIG_DIR / "precedence_matrix.yaml")
    official = Claim(
        claim_id="c1", fact_class="opportunity_deadline",
        source_class="OFFICIAL_ISSUER", source_id="src_ga_dca",
        source_effective_at="2026-08-02T00:00:00Z", value="2026-10-29")
    crawled = Claim(
        claim_id="c2", fact_class="opportunity_deadline",
        source_class="GOVERNED_WEB", source_id="src_ga_portal_crawl",
        source_effective_at="2026-08-01T00:00:00Z", value="2026-10-15")
    res = resolve([official, crawled], matrix["precedence_matrix"])
    assert res.resolved
    assert res.winner.claim_id == "c1"  # official issuer wins, not the crawler
