"""B3.C18 tests — Private/Foundation/Corporate Source Protocol.

Fail-closed:
  * a private source can only be ENABLED after ALL registration requirements
    are met;
  * a missing stable external ID never blocks internal source/opportunity
    identity (uncertainty preserved, not invented away);
  * a webpage redesign does not silently create a duplicate opportunity;
  * an old/archived foundation page never outranks the current issuer page.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_private_source_security import (
    KNOWN_REGISTRATION_REQUIREMENTS,
    KNOWN_SOURCE_CLASSES,
    validate_private,
)
from prototype.g0.source.precedence import Claim, resolve
from prototype.g0.source.private_sources import (
    REGISTRATION_REQUIREMENTS,
    PageFingerprint,
    PrivateSource,
    PrivateSourceStatus,
    RedesignResolution,
    missing_stable_id_allows_internal_identity,
    resolve_redesign,
)

CFG = SOURCE_CONFIG_DIR / "private_source_policy.yaml"


def test_validator_live_config_passes():
    errors: list[str] = []
    validate_private(load_yaml(CFG), errors)
    assert errors == []


def test_requirements_match_config():
    cfg = load_yaml(CFG)
    assert set(cfg["registration_requirements"]) == set(REGISTRATION_REQUIREMENTS)
    assert set(cfg["registration_requirements"]) == KNOWN_REGISTRATION_REQUIREMENTS
    assert set(cfg["allowed_source_classes"]) <= KNOWN_SOURCE_CLASSES


def test_enable_requires_all_registration_requirements():
    src = PrivateSource(
        source_id="src_foundation_alpha", name="Alpha Family Foundation",
        base_domains=["alphafamilyfoundation.org"],
        status=PrivateSourceStatus.ENABLED,
        satisfied_requirements={"issuer_ownership_verified",
                                "terms_robots_reviewed"},
        external_id=None)
    errors = src.registration_errors()
    assert errors  # ENABLED despite unmet requirements must fail
    assert any("ENABLED despite unmet" in e for e in errors)


def test_all_requirements_met_enables_cleanly():
    src = PrivateSource(
        source_id="src_foundation_alpha", name="Alpha Family Foundation",
        base_domains=["alphafamilyfoundation.org"],
        status=PrivateSourceStatus.ENABLED,
        satisfied_requirements=set(REGISTRATION_REQUIREMENTS),
        external_id=None)
    assert src.registration_errors() == []


def test_missing_stable_id_still_allows_internal_identity():
    src = missing_stable_id_allows_internal_identity(
        "src_foundation_beta", "Beta Community Trust")
    assert src.source_id == "src_foundation_beta"   # governed internal identity
    assert src.external_id is None                   # uncertainty preserved
    assert src.status is PrivateSourceStatus.PENDING


def test_redesign_keeps_same_opportunity():
    prev = PageFingerprint("https://beta.foundation.org/grants/community",
                           opportunity_key="community-grants", page_hash="h1")
    new = PageFingerprint("https://beta.foundation.org/grants/community",
                          opportunity_key="community-grants", page_hash="h2")
    assert resolve_redesign(prev, new) is RedesignResolution.SAME_OPPORTUNITY


def test_redesign_ambiguous_not_silent_duplicate():
    prev = PageFingerprint("https://beta.foundation.org/grants/community",
                           opportunity_key="community-grants", page_hash="h1")
    new = PageFingerprint("https://beta.foundation.org/grants/community",
                          opportunity_key="other-grants", page_hash="h2")
    # same canonical URL with a changed key -> NEEDS_REVIEW, never NEW/silent dup
    assert resolve_redesign(prev, new) is RedesignResolution.NEEDS_REVIEW


def test_new_opportunity_only_on_distinct_key_and_url():
    prev = PageFingerprint("https://beta.foundation.org/grants/community",
                           opportunity_key="community-grants", page_hash="h1")
    new = PageFingerprint("https://beta.foundation.org/grants/youth",
                          opportunity_key="youth-grants", page_hash="h9")
    assert resolve_redesign(prev, new) is RedesignResolution.NEW_OPPORTUNITY
    # ambiguous cross-URL cases go to review, not silent NEW
    amb = PageFingerprint("https://beta.foundation.org/grants/youth",
                          opportunity_key=None, page_hash="h9")
    assert resolve_redesign(prev, amb) is RedesignResolution.NEEDS_REVIEW


def test_old_foundation_page_cannot_outrank_current_issuer_page():
    matrix = load_yaml(SOURCE_CONFIG_DIR / "precedence_matrix.yaml")
    current = Claim(
        claim_id="c1", fact_class="opportunity_deadline",
        source_class="GOVERNED_WEB", source_id="src_foundation_alpha",
        source_effective_at="2026-08-10T00:00:00Z", value="2026-11-01")
    archived = Claim(
        claim_id="c2", fact_class="opportunity_deadline",
        source_class="GOVERNED_WEB", source_id="src_foundation_alpha_archive",
        source_effective_at="2025-06-01T00:00:00Z", value="2025-11-01")
    res = resolve([current, archived], matrix["precedence_matrix"])
    assert res.resolved
    # temporal rule picks the newest effective date at equal authority
    assert res.winner.claim_id == "c1"
