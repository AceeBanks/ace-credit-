"""B2.C16 tests — Extension Namespace & Sector Portability.

Grant ontology stays precise; provider-specific fields live in namespaced
extensions; adding a future state/private grant provider never changes core
identity semantics.
"""
from __future__ import annotations

import copy

from prototype.g0.domain.extensions import (
    core_identity_scheme,
    is_namespaced,
    provider_prefix,
    register_provider,
)
from tools.g0.validate_domain import (
    load_entity_types,
    load_extension_namespace,
    validate_extension_namespace,
)

POLICY = load_extension_namespace()


def test_live_extension_namespace_passes():
    ok, report = validate_extension_namespace(POLICY)
    assert ok, report["errors"]
    assert report["grant_concept_count"] >= 10
    assert report["provider_count"] >= 3


def test_grant_concepts_stay_in_grant_namespace():
    grant = set(POLICY["grant_namespace_concepts"])
    assert {"GrantOpportunity", "OpportunityRevision", "EligibilityDecision",
            "ApplicationProject", "Requirement", "Award"} <= grant


def test_no_premature_generalization():
    # GrantOpportunity is NOT renamed into a meaningless OpportunityObject
    grant = set(POLICY["grant_namespace_concepts"])
    assert "GrantOpportunity" in grant
    assert "OpportunityObject" not in grant
    assert POLICY["premature_generalization_prohibited"] is True


def test_cross_sector_primitives_move_only_via_explicit_adr():
    candidates = set(POLICY["platform_primitive_candidates"])
    assert {"Organization", "Person", "Artifact", "EvidenceClaim",
            "CanonicalFact", "StatisticObservation"} == candidates
    assert POLICY["platform_move_rule"] == "explicit_adr_required"


def test_provider_prefixes_are_namespaced():
    assert provider_prefix("georgia", POLICY) == "ga_"
    assert provider_prefix("federal", POLICY) == "fed_"
    assert is_namespaced("ga_org_type", "ga_") is True
    assert is_namespaced("org_type", "ga_") is False        # root pollution


def test_adding_provider_does_not_change_core_identity_semantics():
    scheme_before = core_identity_scheme(load_entity_types()["entity_types"])
    # simulate registering a NEW state provider (Alabama): core catalog unchanged
    scheme_after = core_identity_scheme(load_entity_types()["entity_types"])
    assert register_provider(scheme_before, scheme_after) is True
    # a provider addition that mutated the identity scheme fails closed
    mutated = {**scheme_after, "GrantOpportunity": "opp2_"}
    assert register_provider(scheme_before, mutated) is False


def test_identity_prefix_scheme_has_stable_roots():
    scheme = core_identity_scheme(load_entity_types()["entity_types"])
    assert scheme["GrantOpportunity"] == "opp_"
    assert scheme["ApplicationProject"] == "app_"
    assert scheme["Award"] == "award_"
    assert scheme["Organization"] == "org_"


def test_unknown_provider_fails_closed():
    import pytest
    from prototype.g0.domain.extensions import provider_prefix
    with pytest.raises(ValueError):
        provider_prefix("not-a-provider", POLICY)


# --- validator defect injection ------------------------------------------------

def test_missing_grant_concept_fails():
    data = copy.deepcopy(POLICY)
    data["grant_namespace_concepts"] = [c for c in data["grant_namespace_concepts"]
                                        if c != "Award"]
    ok, report = validate_extension_namespace(data)
    assert not ok
    assert any("Award" in e for e in report["errors"])


def test_unprefixed_provider_fails():
    data = copy.deepcopy(POLICY)
    data["provider_namespaces"].append({"provider": "alabama", "prefix": "al"})
    ok, report = validate_extension_namespace(data)
    assert not ok
    assert any("prefix must end with '_'" in e for e in report["errors"])


def test_premature_generalization_fails():
    data = copy.deepcopy(POLICY)
    data["premature_generalization_prohibited"] = False
    ok, report = validate_extension_namespace(data)
    assert not ok
    assert any("premature_generalization_prohibited" in e for e in report["errors"])
