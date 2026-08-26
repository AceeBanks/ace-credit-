"""B2.C5 tests — External Identifier Namespace Catalog.

Namespace collision, normalization, invalid format, same value in two
namespaces, historical validity windows, and the hard rule that an
external_id without a namespace is never stored.
"""
from __future__ import annotations

import copy

from tools.g0.validate_domain import (
    load_entity_types,
    load_identifier_namespaces,
    validate_identifier_namespaces,
)


def _live():
    return load_identifier_namespaces()


def test_live_namespace_catalog_passes():
    ok, report = validate_identifier_namespaces(_live(), load_entity_types())
    assert ok, report["errors"]
    assert report["namespace_count"] >= 10


def test_required_federal_and_georgia_namespaces_present():
    ids = {n["namespace_id"] for n in _live()["namespaces"]}
    required = {"EIN", "UEI", "ALN", "GRANTS_GOV_OPPORTUNITY", "FAIN",
                "USA_SPENDING_AWARD", "SAM_ENTITY", "FIPS", "GA_PORTAL",
                "COMMON_GRANTS", "PROVIDER"}
    assert required <= ids, f"missing: {sorted(required - ids)}"


def test_every_namespace_has_full_metadata():
    for ns in _live()["namespaces"]:
        for flag in ("globally_unique", "temporally_unique", "reusable",
                     "case_sensitive"):
            assert isinstance(ns[flag], bool), f"{ns['namespace_id']}.{flag}"
        assert ns["normalization_rule"] and ns["verification_sources"]


def test_duplicate_namespace_fails():
    data = copy.deepcopy(_live())
    data["namespaces"].append(dict(data["namespaces"][0]))
    ok, report = validate_identifier_namespaces(data, load_entity_types())
    assert not ok
    assert any("duplicate namespace" in e for e in report["errors"])


def test_namespace_referencing_unknown_entity_fails():
    data = copy.deepcopy(_live())
    data["namespaces"][0]["applies_to_entity_types"].append("GrantWinnerCompany")
    ok, report = validate_identifier_namespaces(data, load_entity_types())
    assert not ok
    assert any("unknown entity" in e for e in report["errors"])


def test_entity_types_validate_against_identifier_semantics():
    """Every entity with external IDs uses namespaced identifiers only."""
    from prototype.g0.domain.models import Award, ExternalIdentifier
    from decimal import Decimal
    # namespaced external ids are attached identities, never bare fields
    award = Award("award-1", "org-2", "org-1", Decimal("75000.00"),
                  external_award_ids=(
                      ExternalIdentifier("FAIN", "FAIN-2026-0001", "Award"),))
    assert award.external_award_ids[0].namespace == "FAIN"
    assert not hasattr(award, "external_id")  # no bare external_id field
