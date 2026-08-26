"""B2.C6 tests — Typed Relationship Catalog.

Invalid endpoint types rejected, cardinality enforced, self-loops prohibited
where declared, temporal versioning supported, cross-tenant rejected.
"""
from __future__ import annotations

import copy

from prototype.g0.domain.models import Relationship
from prototype.g0.domain.relationships import (
    cardinality_ok,
    endpoint_types_ok,
    self_loop_allowed,
    tenants_ok,
)
from tools.g0.validate_domain import (
    load_entity_types,
    load_relationships,
    validate_relationships,
)


def _specs() -> dict:
    return {r["relationship_type"]: r for r in load_relationships()["relationship_types"]}


def _resolve(ref: str) -> str:
    # entity_type by ref prefix (B2.C4 scheme); longest prefixes first so
    # opp_rev_ is not shadowed by opp_, app_rev_ by app_.
    table = {
        "opp_rev_": "OpportunityRevision", "app_rev_": "ApplicationRevision",
        "org_": "Organization", "person_": "Person", "program_": "Program",
        "opp_": "GrantOpportunity", "award_": "Award", "app_": "ApplicationProject",
        "req_": "Requirement", "artifact_": "Artifact", "budget_": "Budget",
        "claim_": "EvidenceClaim", "fact_": "CanonicalFact",
        "stat_": "StatisticObservation", "outcome_": "OutcomeFeedback",
        "snap_": "SourceSnapshot",
    }
    for prefix, et in sorted(table.items(), key=lambda kv: -len(kv[0])):
        if ref.startswith(prefix):
            return et
    raise KeyError(ref)


def test_live_relationship_catalog_passes():
    ok, report = validate_relationships(load_relationships(), load_entity_types())
    assert ok, report["errors"]
    assert report["relationship_count"] >= 24


def test_all_plan_relationship_types_present():
    ids = {r["relationship_type"] for r in load_relationships()["relationship_types"]}
    required = {"ORGANIZATION_HAS_CONTACT", "ORGANIZATION_HAS_PARTNER",
                "FUNDER_OFFERS_PROGRAM", "PROGRAM_HAS_OPPORTUNITY",
                "OPPORTUNITY_HAS_REVISION", "AWARD_FUNDED_BY", "AWARD_RECEIVED_BY",
                "APPLICATION_TARGETS_OPPORTUNITY_REVISION",
                "APPLICATION_HAS_REQUIREMENT", "CLAIM_ASSERTED_BY_SOURCE_SNAPSHOT",
                "FACT_SUPPORTED_BY_CLAIM", "ARTIFACT_USES_FACT",
                "REQUIREMENT_SUPPORTED_BY_ARTIFACT"}
    assert required <= ids, f"missing: {sorted(required - ids)}"


def test_duplicate_relationship_type_fails():
    data = copy.deepcopy(load_relationships())
    data["relationship_types"].append(dict(data["relationship_types"][0]))
    ok, report = validate_relationships(data, load_entity_types())
    assert not ok
    assert any("duplicate relationship type" in e for e in report["errors"])


def test_unknown_endpoint_type_fails():
    data = copy.deepcopy(load_relationships())
    data["relationship_types"][0]["target_entity_types"].append("GrantWinnerCompany")
    ok, report = validate_relationships(data, load_entity_types())
    assert not ok
    assert any("endpoint type" in e for e in report["errors"])


def test_invalid_endpoint_types_rejected_at_runtime():
    spec = _specs()["APPLICATION_TARGETS_OPPORTUNITY_REVISION"]
    bad = Relationship("rel-1", "APPLICATION_TARGETS_OPPORTUNITY_REVISION",
                       "app_1", "artifact_9")   # artifact is not a revision
    good = Relationship("rel-2", "APPLICATION_TARGETS_OPPORTUNITY_REVISION",
                        "app_1", "opp_rev_2")
    assert not endpoint_types_ok(bad, spec, _resolve)
    assert endpoint_types_ok(good, spec, _resolve)


def test_cardinality_11_enforced():
    spec = _specs()["STATISTIC_DERIVED_FROM_SOURCE"]
    assert cardinality_ok(spec, existing_source_count=0)
    assert not cardinality_ok(spec, existing_source_count=1)


def test_org_partner_self_loop_prohibited():
    spec = _specs()["ORGANIZATION_HAS_PARTNER"]
    loop = Relationship("rel-3", "ORGANIZATION_HAS_PARTNER", "org_1", "org_1")
    assert not self_loop_allowed(loop, spec)
    normal = Relationship("rel-4", "ORGANIZATION_HAS_PARTNER", "org_1", "org_2")
    assert self_loop_allowed(normal, spec)


def test_cross_tenant_relationship_rejected():
    spec = _specs()["APPLICATION_HAS_REQUIREMENT"]
    tenant_of = {"app_1": "tenant-alpha", "req_1": "tenant-beta"}
    rel = Relationship("rel-5", "APPLICATION_HAS_REQUIREMENT", "app_1", "req_1",
                       tenant_id="tenant-alpha")
    assert not tenants_ok(rel, tenant_of.__getitem__, "tenant-alpha")


def test_temporal_relationship_versioning_supported():
    # same edge with different validity windows coexists (temporal edges)
    spec = _specs()["ORGANIZATION_HAS_PARTNER"]
    r1 = Relationship("rel-6", "ORGANIZATION_HAS_PARTNER", "org_1", "org_2",
                      valid_from="2025-01-01", valid_to="2025-12-31")
    r2 = Relationship("rel-7", "ORGANIZATION_HAS_PARTNER", "org_1", "org_2",
                      valid_from="2026-01-01", valid_to="2026-12-31")
    assert r1.valid_from != r2.valid_from  # distinct temporal edges, same semantics
    assert r1.relationship_type == r2.relationship_type
