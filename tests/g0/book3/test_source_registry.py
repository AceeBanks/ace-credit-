"""B3.C2-C3 tests — Source Classification + SourceRegistry.

Every registered source has a class and authority tier; derived internal
objects cannot pretend to be external authority; source class alone never
bypasses fact-specific precedence; registry seed integrity checks fail closed.
"""
from __future__ import annotations

import copy

from tools.g0.validate_source_registry import (
    load_classes,
    load_registry,
    validate_classes,
    validate_registry,
)


def _class_ids():
    return {c["class_id"] for c in load_classes()["classes"]}


def test_live_classes_and_registry_pass():
    ok_c, _ = validate_classes(load_classes())
    ok_r, _ = validate_registry(load_registry(), _class_ids())
    assert ok_c and ok_r


def test_all_8_source_classes_present_with_authority_tiers():
    classes = {c["class_id"]: c for c in load_classes()["classes"]}
    assert set(classes) == {"OFFICIAL_ISSUER", "OFFICIAL_AGGREGATOR",
                            "OFFICIAL_TRANSACTIONAL", "OFFICIAL_STATISTICAL",
                            "TRUSTED_CURATED", "GOVERNED_WEB", "USER_PROVIDED",
                            "DERIVED_INTERNAL"}
    assert classes["OFFICIAL_ISSUER"]["authority_tier"] == "A"
    assert classes["OFFICIAL_AGGREGATOR"]["authority_tier"] == "B"
    assert classes["GOVERNED_WEB"]["authority_tier"] == "D"
    assert classes["USER_PROVIDED"]["authority_tier"] == "E"


def test_derived_internal_cannot_pretend_external_authority():
    classes = {c["class_id"]: c for c in load_classes()["classes"]}
    derived = classes["DERIVED_INTERNAL"]
    assert derived.get("external_authority") is False
    assert derived.get("authority_tier") is None


def test_source_class_alone_does_not_bypass_precedence():
    reg = load_registry()
    gov_web = [s for s in reg["sources"] if s["source_class"] == "GOVERNED_WEB"]
    official = [s for s in reg["sources"] if s["source_class"] == "OFFICIAL_ISSUER"]
    # the registry enforces both class AND tier; precedence (C8) is fact-specific
    assert gov_web and official
    # a governed web source is tier D, never outranking an official issuer (A)
    assert gov_web[0]["authority_tier"] == "D"
    assert min(o["authority_tier"] for o in official) == "A"


def test_seed_registry_covers_federal_georgia_statistical():
    ids = {s["source_id"] for s in load_registry()["sources"]}
    for expected in ("src_grants_gov", "src_simpler_grants", "src_usaspending",
                     "src_irs_eo", "src_census_acs", "src_ga_opb_grants",
                     "src_ga_dca", "src_foundation_xyz"):
        assert expected in ids, expected


def test_duplicate_source_id_rejected():
    data = copy.deepcopy(load_registry())
    data["sources"].append(dict(data["sources"][0]))
    ok, report = validate_registry(data, _class_ids())
    assert not ok
    assert any("duplicate source id" in e for e in report["errors"])


def test_source_without_authority_classification_rejected():
    data = copy.deepcopy(load_registry())
    data["sources"][0]["source_class"] = "MYSTERY"
    ok, report = validate_registry(data, _class_ids())
    assert not ok
    assert any("unclassified or unknown" in e for e in report["errors"])


def test_enabled_web_source_without_policy_review_rejected():
    data = copy.deepcopy(load_registry())
    s = next(x for x in data["sources"] if x["source_id"] == "src_ga_opb_grants")
    s["terms_policy_ref"] = None
    ok, report = validate_registry(data, _class_ids())
    assert not ok
    assert any("terms_policy_ref" in e for e in report["errors"])


def test_auth_required_source_without_credential_scope_rejected():
    data = copy.deepcopy(load_registry())
    data["sources"][0]["auth_mode"] = "oauth"
    data["sources"][0]["credential_scope_ref"] = None
    ok, report = validate_registry(data, _class_ids())
    assert not ok
    assert any("credential_scope_ref" in e for e in report["errors"])


def test_enabled_machine_source_requires_adapter_version():
    data = copy.deepcopy(load_registry())
    data["sources"][0]["adapter_version"] = None
    ok, report = validate_registry(data, _class_ids())
    assert not ok
    assert any("adapter_version" in e for e in report["errors"])


def test_class_missing_tier_rejected():
    data = copy.deepcopy(load_classes())
    data["classes"][0]["authority_tier"] = "Z"
    ok, report = validate_classes(data)
    assert not ok
    assert any("tier" in e for e in report["errors"])