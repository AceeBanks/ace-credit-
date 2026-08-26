"""B3.C8-C9 tests — Source Precedence Matrix + Freshness Constitution.

Fail-closed:
  * fact-specific precedence works;
  * a higher generic source tier does not outrank a specialized authoritative
    source for the fact it governs;
  * client-intent facts can outrank government data ONLY for the facts the
    client controls, not legal/issuer facts;
  * equal-authority conflict => CONFLICTED, no last-write-wins;
  * same age produces different freshness for different fact classes;
  * annual-statistic latest-vintage remains valid;
  * hard-stale deadline blocks submission-ready state;
  * historical-fixed award remains valid absent correction.
"""
from __future__ import annotations

import copy

from prototype.g0.source.precedence import (
    Claim,
    ConflictResolution,
    client_controls,
    resolve,
    source_rank,
)
from prototype.g0.source.freshness import (
    FreshnessPolicy,
    FreshnessState,
    classify,
    hard_stale_blocks_critical,
)
from tools.g0._common import REPO_ROOT, SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_precedence_freshness import (
    validate_freshness_config,
    validate_precedence_config,
)

PRECEDENCE = SOURCE_CONFIG_DIR / "precedence_matrix.yaml"
FRESHNESS = SOURCE_CONFIG_DIR / "freshness_policy.yaml"


def _matrix():
    cfg = load_yaml(PRECEDENCE)
    return cfg["precedence_matrix"]

def _client_controlled():
    return set(load_yaml(PRECEDENCE)["client_controlled_fact_classes"])

def _policy(name):
    return load_yaml(FRESHNESS)["policies"][name]


def test_live_precedence_and_freshness_pass():
    ok_p, rep_p = validate_precedence_config(PRECEDENCE)
    assert ok_p, rep_p["errors"]
    ok_f, rep_f = validate_freshness_config(FRESHNESS)
    assert ok_f, rep_f["errors"]


# --- C8 precedence ----------------------------------------------------------

def test_deadline_official_issuer_outranks_user_recollection():
    matrix = _matrix()
    official = Claim("c1", "opportunity_deadline", "OFFICIAL_ISSUER", "src_ga_opb",
                     source_effective_at="2026-08-01T00:00:00Z", value="2026-09-01")
    user = Claim("c2", "opportunity_deadline", "USER_PROVIDED", "src_user",
                 source_effective_at="2026-08-02T00:00:00Z", value="2026-08-15")
    res = resolve([official, user], matrix)
    assert res.resolved
    assert res.winner.claim_id == "c1"


def test_higher_generic_tier_does_not_outrank_specialized_authority():
    # USER_PROVIDED (tier E) vs TRUSTED_CURATED (tier C) for tax-exempt status:
    # precedence chain governs by fact class, not generic tier.
    matrix = _matrix()
    irs = Claim("c1", "tax_exempt_status", "OFFICIAL_TRANSACTIONAL", "src_irs_eo",
                source_effective_at="t", value="501c3")
    agg = Claim("c2", "tax_exempt_status", "TRUSTED_CURATED", "src_candid",
                source_effective_at="t2", value="501c3-agg")
    res = resolve([irs, agg], matrix)
    assert res.resolved
    assert res.winner.claim_id == "c1"


def test_equal_authority_disagreement_conflicted_no_lww():
    matrix = _matrix()
    a = Claim("a", "historical_award_amount", "OFFICIAL_TRANSACTIONAL", "s1",
              source_effective_at="2026-01-01T00:00:00Z", value=100_000)
    b = Claim("b", "historical_award_amount", "OFFICIAL_TRANSACTIONAL", "s2",
              source_effective_at="2026-01-01T00:00:00Z", value=110_000)
    res = resolve([a, b], matrix)
    assert res.resolution == ConflictResolution.CONFLICTED
    assert res.winner is None


def test_equal_authority_temporal_rule_resolves_conflict():
    matrix = _matrix()
    a = Claim("a", "opportunity_award_ceiling", "OFFICIAL_ISSUER", "s1",
              source_effective_at="2026-08-10T00:00:00Z", value=500_000)
    b = Claim("b", "opportunity_award_ceiling", "OFFICIAL_ISSUER", "s2",
              source_effective_at="2026-08-11T00:00:00Z", value=600_000)
    res = resolve([a, b], matrix)
    assert res.resolution == ConflictResolution.RESOLVED
    assert res.winner.claim_id == "b"


def test_client_intent_outranks_gov_for_client_fact_only():
    matrix = _matrix()
    controlled = _client_controlled()
    # client-controlled: internal project goals can outrank gov data
    assert client_controls("client_program_intent", controlled)
    assert client_controls("user_preferences_intention", controlled)
    assert client_controls("internal_project_goals", controlled)
    # issuer/legal facts are NOT client-controlled
    assert not client_controls("tax_exempt_status", controlled)
    assert not client_controls("opportunity_deadline", controlled)


# --- C9 freshness -----------------------------------------------------------

def _pol(**kw) -> FreshnessPolicy:
    base = dict(fact_class="x", source_class="OFFICIAL_ISSUER",
                soft_stale_after_days=7, hard_stale_after_days=14,
                refresh_on_access=True, refresh_on_deadline_window="<14 days",
                latest_vintage_rule=None, critical_use_block_on_hard_stale=True)
    base.update(kw)
    return FreshnessPolicy(**base)


def test_same_age_differs_by_fact_class():
    deadline = _pol(fact_class="opportunity_deadline", soft_stale_after_days=7,
                    hard_stale_after_days=14)
    funding = _pol(fact_class="funder_identity", source_class="GOVERNED_WEB",
                   soft_stale_after_days=60, hard_stale_after_days=180)
    # 30 days old: HARD_STALE for deadline, FRESH for funder
    assert classify(deadline, "2026-07-01T00:00:00Z", age_days=30) == FreshnessState.HARD_STALE
    assert classify(funding, "2026-07-01T00:00:00Z", age_days=30) == FreshnessState.FRESH


def test_annual_statistic_latest_vintage_remains_valid():
    p = _pol(latest_vintage_rule="dataset_vintage_reference_period",
             critical_use_block_on_hard_stale=False)
    # 400 days old but vintage is still current => FRESH
    assert classify(p, "2025-07-01T00:00:00Z", age_days=400,
                    latest_vintage_current=True) == FreshnessState.FRESH
    # vintage superseded => HARD_STALE
    assert classify(p, "2025-07-01T00:00:00Z", age_days=400,
                    latest_vintage_current=False) == FreshnessState.HARD_STALE


def test_hard_stale_deadline_blocks_submission_readiness():
    p = _pol(fact_class="opportunity_deadline", critical_use_block_on_hard_stale=True)
    state = classify(p, "2026-07-01T00:00:00Z", age_days=40)
    assert state == FreshnessState.HARD_STALE
    assert hard_stale_blocks_critical(p, state)


def test_historical_fixed_award_remains_valid_absent_correction():
    p = _pol(fact_class="historical_award_amount", latest_vintage_rule="historical_fixed_absent_correction",
             soft_stale_after_days=None, hard_stale_after_days=None,
             critical_use_block_on_hard_stale=False)
    assert classify(p, "2020-01-01T00:00:00Z", age_days=2400,
                    latest_vintage_current=True) == FreshnessState.HISTORICAL_FIXED


def test_unknown_age_is_unknown_freshness():
    p = _pol(latest_vintage_rule=None)
    assert classify(p, None, age_days=None) == FreshnessState.UNKNOWN_FRESHNESS


def test_soft_stale_not_hard():
    p = _pol(soft_stale_after_days=7, hard_stale_after_days=14)
    assert classify(p, "t", age_days=10) == FreshnessState.SOFT_STALE