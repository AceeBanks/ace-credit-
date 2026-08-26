"""B3.C16 tests — Federal source profiles + fixtures.

Fail-closed:
  * the five required federal lanes are declared;
  * every profile identifier namespace exists in the Book 2 catalog;
  * capture methods and freshness refs come from known enums;
  * profile fixture examples are declared for the priority lanes;
  * the federal domain fixtures normalize into the Book 2 core ontology
    (GrantOpportunity / Program / Award), never a federal-specific root.
"""
from __future__ import annotations

from decimal import Decimal

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_domain import load_identifier_namespaces
from tools.g0.validate_source_profiles import (
    EXPECTED_FEDERAL_LANES,
    KNOWN_CAPTURE_METHODS,
    KNOWN_FRESHNESS_REFS,
    validate_federal,
)

FED_CFG = SOURCE_CONFIG_DIR / "federal_profiles.yaml"


def _errors() -> list[str]:
    errors: list[str] = []
    validate_federal(load_yaml(FED_CFG), errors)
    return errors


def test_validator_live_config_passes():
    assert _errors() == []


def test_required_federal_lanes_present():
    profiles = load_yaml(FED_CFG)["source_profiles"]
    assert EXPECTED_FEDERAL_LANES <= set(profiles.keys())


def test_all_namespaces_in_book2_catalog():
    catalog = {ns["namespace_id"]
               for ns in load_identifier_namespaces()["namespaces"]}
    profiles = load_yaml(FED_CFG)["source_profiles"]
    for pid, p in profiles.items():
        for ns in p["identifier_namespaces"]:
            assert ns in catalog, f"{pid}: namespace {ns} not in Book 2 catalog"


def test_capture_methods_and_freshness_known():
    profiles = load_yaml(FED_CFG)["source_profiles"]
    for pid, p in profiles.items():
        assert p["capture_method"] in KNOWN_CAPTURE_METHODS, pid
        assert p["freshness_policy_ref"] in KNOWN_FRESHNESS_REFS, pid


def test_priority_lanes_have_fixture_examples():
    profiles = load_yaml(FED_CFG)["source_profiles"]
    for lane in ("grants_gov_simpler", "usaspending", "irs_eo_bmf_990",
                 "census_acs_saipe"):
        assert profiles[lane]["fixture_examples"], lane


def test_federal_fixtures_are_book2_core_types():
    from prototype.g0.domain.fixtures.federal import (
        AWARD_RECORD,
        FED_OPP,
        FED_PROGRAM,
    )
    from prototype.g0.domain.models import Award, GrantOpportunity, Program
    assert isinstance(FED_OPP, GrantOpportunity)
    assert isinstance(FED_PROGRAM, Program)
    assert isinstance(AWARD_RECORD, Award)
    # award amount is Decimal money, not float
    assert isinstance(AWARD_RECORD.amount, Decimal)
    # award carries a FAIN namespace identifier via external id semantics


def test_federal_profile_priority_facts_map_to_domain_fact_classes():
    # no federal-only root fact classes: everything maps to shared core fact
    # classes defined in Book 2 / Book 3 precedence matrix
    from tools.g0._common import load_yaml as _ly
    matrix = _ly(SOURCE_CONFIG_DIR / "precedence_matrix.yaml")
    known = set(matrix.get("fact_classes", []))
    profiles = load_yaml(FED_CFG)["source_profiles"]
    for pid, p in profiles.items():
        for fact in p["priority_facts"]:
            assert fact in known, f"{pid}: priority fact {fact!r} not in precedence matrix"
