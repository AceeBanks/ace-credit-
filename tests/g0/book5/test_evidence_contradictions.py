"""G0-B5-C5-C6 — Claim support/promotion + contradiction resolution tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.contradictions import (  # noqa: E402
    EvidenceQualityError,
    SupportAssertion,
    detect_unit_conflict,
    equal_authority_must_stay_open,
    independent_corroboration,
    open_contradiction,
    promote_claim,
    resolve_contradiction,
)

CONTR_CFG = yaml.safe_load(
    (_ROOT / "config/g0/evidence/contradiction_types.yaml").read_text(
        encoding="utf-8"))


def _support(support_id: str, support_type: str, evidence_ref: str) -> SupportAssertion:
    return SupportAssertion(
        support_id=support_id, claim_ref="claim-1", evidence_ref=evidence_ref,
        support_type=support_type, created_at="2026-08-26T00:00:00+00:00",
        method="support-scan-v1")


def test_unsupported_claim_cannot_promote():
    with pytest.raises(EvidenceQualityError, match="unsupported"):
        promote_claim(claim_ref="claim-1", support_assertions=[],
                      contradictions=[], policy_ref="policy/support-v1")


def test_user_attested_cannot_satisfy_official_requirement():
    supports = [_support("s1", "USER_ATTESTED", "ev-user")]
    with pytest.raises(EvidenceQualityError, match="support policy"):
        promote_claim(claim_ref="claim-1", support_assertions=supports,
                      contradictions=[], policy_ref="policy/support-v1",
                      min_support_types={"OFFICIAL_RECORD"})


def test_official_record_promotes():
    supports = [_support("s1", "OFFICIAL_RECORD", "ev-official")]
    result = promote_claim(claim_ref="claim-1", support_assertions=supports,
                           contradictions=[], policy_ref="policy/support-v1")
    assert result["result"] == "PROMOTED"


def test_open_p0_contradiction_blocks_promotion():
    supports = [_support("s1", "OFFICIAL_RECORD", "ev-official")]
    contrad = [{"contradiction_id": "c-1", "status": "OPEN", "severity": "P0"}]
    with pytest.raises(EvidenceQualityError, match="contradiction"):
        promote_claim(claim_ref="claim-1", support_assertions=supports,
                      contradictions=contrad, policy_ref="policy/support-v1")


def test_same_upstream_copy_is_not_independent_corroboration():
    supports = [_support("s1", "CORROBORATING", "ev-a"),
                _support("s2", "CORROBORATING", "ev-b")]
    upstream = {"ev-a": "article-1", "ev-b": "article-1"}
    assert independent_corroboration(supports, upstream) is False
    upstream2 = {"ev-a": "article-1", "ev-b": "article-2"}
    assert independent_corroboration(supports, upstream2) is True


def test_unit_mismatch_detected_before_value_conflict():
    assert detect_unit_conflict({"unit": "$"}, {"unit": "k"}) is True
    assert detect_unit_conflict({"unit": "$"}, {"unit": "USD"}) is False


def test_equal_authority_conflict_stays_open():
    from prototype.g0.evidence.contradictions import EvidenceQuality
    q1 = EvidenceQuality(quality_id="q1", evidence_ref="ev-a",
                         dimensions={k: 0.9 for k in (
                             "authority", "directness", "freshness",
                             "specificity", "corroboration",
                             "extraction_quality", "identity_certainty",
                             "temporal_fit")},
                         quality_class="VERIFIED_HIGH", computed_by="t")
    q2 = EvidenceQuality(quality_id="q2", evidence_ref="ev-b",
                         dimensions=dict(q1.dimensions),
                         quality_class="VERIFIED_HIGH", computed_by="t")
    assert equal_authority_must_stay_open([q1, q2]) is True


def test_confidence_cannot_resolve():
    c = open_contradiction(
        contradiction_id="c-1", tenant_id="tenant-a",
        entity_type="GrantOpportunity", entity_id="opp-1",
        predicate="deadline", claim_refs=["claim-a", "claim-b"],
        contradiction_type="VALUE_CONFLICT", severity="P1")
    with pytest.raises(EvidenceQualityError, match="confidence"):
        resolve_contradiction(contradiction=c, chosen_fact_ref="fact-1",
                              policy_ref="policy/x", resolved_by="svc",
                              reason="model says so", model_confidence=0.99)


def test_human_resolution_audited_and_losing_claim_retained():
    c = open_contradiction(
        contradiction_id="c-2", tenant_id="tenant-a",
        entity_type="GrantOpportunity", entity_id="opp-1",
        predicate="award_ceiling", claim_refs=["claim-a", "claim-b"],
        contradiction_type="VALUE_CONFLICT", severity="P0")
    event = resolve_contradiction(
        contradiction=c, chosen_fact_ref="fact-b",
        policy_ref="policy/resolution-v1", resolved_by="approver-1",
        reason="official solicitation rev-3 confirmed ceiling",
        approval_ref="approval-42")
    assert event.approval_ref == "approval-42"
    # losing claim retained in the resolution event (EVID-LAW-005)
    assert set(event.conflicting_claim_refs) == {"claim-a", "claim-b"}
    assert c.status == "RESOLVED_HUMAN"
    assert c.resolution_event_ref == event.resolution_id


def test_newer_source_does_not_auto_win_with_historical_dates():
    # CONTR-003: opening a temporal contradiction is governed; the resolver
    # cannot silently prefer recency
    c = open_contradiction(
        contradiction_id="c-3", tenant_id="tenant-a",
        entity_type="StatisticObservation", entity_id="stat-1",
        predicate="population", claim_refs=["claim-2020", "claim-2024"],
        contradiction_type="TEMPORAL_CONFLICT", severity="P1")
    with pytest.raises(EvidenceQualityError):
        resolve_contradiction(
            contradiction=c, chosen_fact_ref="claim-2024",
            policy_ref="policy/resolution-v1", resolved_by="svc",
            reason="newer source wins automatically")


def test_config_has_all_types_and_hard_rules():
    ids = {t["id"] for t in CONTR_CFG["contradiction_types"]}
    assert "UNIT_CONFLICT" in ids and "TEMPORAL_CONFLICT" in ids
    hard = {h["id"] for h in CONTR_CFG["hard_rules"]}
    for rule in ("CONTR-001", "CONTR-002", "CONTR-003", "CONTR-004",
                 "CONTR-005", "CONTR-006"):
        assert rule in hard
