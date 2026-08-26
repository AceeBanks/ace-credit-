"""B3.C13-C14 tests — Dependency Invalidation + External Identifier Verification.

Fail-closed:
  * deadline-only change invalidates the right artifacts, not unrelated
    historical-winner research;
  * eligibility change invalidates eligibility and readiness;
  * budget ceiling change invalidates budget/financial consistency;
  * nonmaterial P2 change does not invalidate the application;
  * external ID claimed in chat does not become verified automatically;
  * conflicting verified IDs trigger identity conflict;
  * same value in different namespaces remains distinct.
"""
from __future__ import annotations

from prototype.g0.source.dependency_invalidation import (
    DEPENDENCIES,
    DependencyGraph,
    InvalidationState,
)
from prototype.g0.source.identifier_verification import (
    IdentifierRegistry,
    VerificationEvent,
    VerificationMethod,
    VerificationState,
    chat_claim_is_not_verified,
)
from tools.g0._common import REPO_ROOT, SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_dependency_identifier import (
    KNOWN_INVALIDATION_STATES,
    KNOWN_METHODS,
    KNOWN_VERIFICATION_STATES,
    validate,
)

CFG = SOURCE_CONFIG_DIR / "dependency_identifier.yaml"


def _graph() -> DependencyGraph:
    g = DependencyGraph()
    for artifact, upstream in DEPENDENCIES.items():
        g.add(artifact, set(upstream))
    return g


def test_validator_live_config_passes():
    ok, report = validate(CFG)
    assert ok, report["errors"]


def test_enum_sets_match_config():
    cfg = load_yaml(CFG)
    assert set(cfg["invalidation_states"]) == KNOWN_INVALIDATION_STATES
    assert set(cfg["verification_states"]) == KNOWN_VERIFICATION_STATES
    assert set(cfg["verification_methods"]) == KNOWN_METHODS


# --- C13 dependency invalidation -------------------------------------------

def test_deadline_change_invalidates_deadline_dependents_only():
    g = _graph()
    affected = g.invalidate({"opportunity_deadline"})
    set_affected = set(affected)
    assert "eligibility_decision" in set_affected
    assert "match_explanation" in set_affected
    assert "requirement_set" in set_affected
    # budget depends on award ceiling/floor/match, NOT deadline -> untouched
    assert "budget" not in set_affected
    assert g.state("budget") == InvalidationState.CURRENT


def test_eligibility_change_invalidates_eligibility_and_readiness():
    g = _graph()
    g.invalidate({"opportunity_eligibility"})
    assert g.state("eligibility_decision") == InvalidationState.STALE_RECOMPUTE_REQUIRED
    # submission package is not directly eligibility-dependent
    assert g.state("submission_package") == InvalidationState.CURRENT


def test_budget_ceiling_change_invalidates_budget():
    g = _graph()
    g.invalidate({"opportunity_award_ceiling"})
    assert g.state("budget") == InvalidationState.STALE_RECOMPUTE_REQUIRED
    assert g.state("match_explanation") == InvalidationState.STALE_RECOMPUTE_REQUIRED


def test_nonmaterial_p2_change_does_not_invalidate():
    g = _graph()
    # A P2 formatting/site-chrome change touches no fact any artifact depends on
    affected = g.invalidate({"site_chrome_formatting"}, materiality="P2")
    assert affected == []
    assert g.state("budget") == InvalidationState.CURRENT
    assert g.state("submission_package") == InvalidationState.CURRENT


def test_recompute_restores_current():
    g = _graph()
    g.invalidate({"opportunity_eligibility"})
    g.recompute("eligibility_decision")
    assert g.state("eligibility_decision") == InvalidationState.CURRENT


def test_signal_based_selective_invalidation():
    g = _graph()
    # match_requirement_changed targets budget/match/proposal but not everything
    g.invalidate(set(), signal="match_requirement_changed", materiality="P0")
    assert g.state("budget") == InvalidationState.STALE_RECOMPUTE_REQUIRED
    assert g.state("requirement_set") == InvalidationState.CURRENT


# --- C14 identifier verification -------------------------------------------

def test_chat_claimed_id_not_auto_verified():
    state = chat_claim_is_not_verified()
    assert state == VerificationState.UNVERIFIED


def test_user_asserted_then_official_verified():
    reg = IdentifierRegistry()
    reg.add(VerificationEvent("ein", "12-3456789", "org1", None,
                              VerificationMethod.USER_PROVIDED,
                              ("2026-01-01", None), VerificationState.USER_ASSERTED))
    assert reg.state("org1", "ein") == VerificationState.USER_ASSERTED
    reg.add(VerificationEvent("ein", "12-3456789", "org1", "snap_irs",
                              VerificationMethod.OFFICIAL_RECORD_MATCH,
                              ("2026-02-01", None), VerificationState.VERIFIED_OFFICIAL))
    assert reg.state("org1", "ein") == VerificationState.VERIFIED_OFFICIAL


def test_conflicting_verified_ids_trigger_identity_conflict():
    reg = IdentifierRegistry()
    reg.add(VerificationEvent("ein", "12-0000001", "org1", "s1",
                              VerificationMethod.OFFICIAL_RECORD_MATCH,
                              ("2026-01-01", None), VerificationState.VERIFIED_OFFICIAL))
    reg.add(VerificationEvent("ein", "12-9999999", "org1", "s2",
                              VerificationMethod.OFFICIAL_RECORD_MATCH,
                              ("2026-01-02", None), VerificationState.VERIFIED_OFFICIAL))
    assert any("identity conflict" in e for e in reg._identity_conflicts)


def test_same_value_different_namespaces_distinct():
    reg = IdentifierRegistry()
    # ein namespace vs georgia_portal_id namespace with same literal value string
    reg.add(VerificationEvent("ein", "9999", "org1", None,
                              VerificationMethod.USER_PROVIDED,
                              ("2026-01-01", None), VerificationState.USER_ASSERTED))
    reg.add(VerificationEvent("georgia_portal_id", "9999", "org1", "s3",
                              VerificationMethod.ISSUER_PORTAL,
                              ("2026-01-02", None), VerificationState.VERIFIED_OFFICIAL))
    assert reg.state("org1", "ein") == VerificationState.USER_ASSERTED
    assert reg.state("org1", "georgia_portal_id") == VerificationState.VERIFIED_OFFICIAL
    # no identity conflict because namespaces differ
    assert reg._identity_conflicts == []