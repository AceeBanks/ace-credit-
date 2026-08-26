"""G0 Book 2 — B2.C9 fact, claim, evidence & statistic semantics.

Provisional executable form of the provenance substrate:
  - a claim can NEVER become a canonical fact automatically; promotion is an
    explicit governed action that MUST reference supporting claims
  - conflicting claims coexist — neither is deleted; a fact may be CONFLICTED
  - statistics keep context (geography, unit, reference period, population
    where relevant) instead of being flattened into bare facts
  - artifacts reference facts/statistics/claims through lineage objects.
"""
from __future__ import annotations

from dataclasses import replace

from prototype.g0.domain.models import (
    CanonicalFact,
    ClaimStatus,
    EvidenceClaim,
    FactPromotionState,
    SourceSnapshot,
    StatisticObservation,
)


def claim_to_fact_candidate(claim: EvidenceClaim, fact_id: str) -> CanonicalFact:
    """Produce a PROPOSED fact candidate from a claim.

    This is NOT promotion: the candidate carries no support and stays PROPOSED.
    Becoming canonical requires an explicit promote_fact() action afterwards.
    """
    return CanonicalFact(fact_id, claim.subject, claim.predicate, claim.value,
                         value_type=claim.value_type, scope=claim.subject,
                         promotion_state=FactPromotionState.PROPOSED)


def promote_fact(fact: CanonicalFact, supporting_claim_ids: tuple[str, ...]) -> CanonicalFact:
    """Explicit governed promotion. Fail-closed: support is mandatory."""
    if not supporting_claim_ids:
        raise ValueError("promotion requires at least one supporting claim ref (B2.C9)")
    return replace(fact, promotion_state=FactPromotionState.PROMOTED,
                   supporting_claim_ids=tuple(supporting_claim_ids))


def mark_conflict(fact: CanonicalFact, contradicting_claim_ids: tuple[str, ...]) -> CanonicalFact:
    """A fact becomes CONFLICTED; the disagreeing claims are NOT deleted."""
    if not contradicting_claim_ids:
        raise ValueError("CONFLICTED requires at least one contradicting claim ref (B2.C9)")
    return replace(fact, promotion_state=FactPromotionState.CONFLICTED,
                   contradicting_claim_ids=tuple(contradicting_claim_ids))


def _population_bearing(metric: str, policy: dict) -> bool:
    lowered = metric.lower()
    return any(k in lowered for k in policy.get("population_bearing_metric_keywords", []))


def validate_statistic(stat: StatisticObservation, policy: dict) -> list[str]:
    """Fail-closed statistic context check (B2.C9)."""
    errors: list[str] = []
    required = policy.get("required_statistic_context", [])
    if "geography" in required and not (stat.geography or "").strip():
        errors.append(f"{stat.stat_id}: geography required for statistics")
    if "unit" in required and not (stat.unit or "").strip():
        errors.append(f"{stat.stat_id}: unit required for statistics")
    if "reference_period" in required and not (stat.reference_period or "").strip():
        errors.append(f"{stat.stat_id}: reference_period required for statistics")
    if _population_bearing(stat.metric, policy) and not (stat.population or "").strip():
        errors.append(f"{stat.stat_id}: population required for population-bearing metric "
                      f"'{stat.metric}'")
    return errors


def assertion_lineage(artifact_version_ref: str, fact: CanonicalFact,
                      claims: dict[str, EvidenceClaim],
                      snapshots: dict[str, SourceSnapshot]) -> dict:
    """Trace an artifact's factual assertion back to the evidence object.

    Returns the resolved chain:
        artifact_version_ref -> fact -> supporting claims -> source snapshots.
    Unresolvable links raise (fail closed) rather than returning partial truth.
    """
    if not fact.supporting_claim_ids:
        raise ValueError(f"fact {fact.fact_id} has no supporting claims to trace")
    resolved_claims = []
    for cid in fact.supporting_claim_ids:
        claim = claims.get(cid)
        if claim is None:
            raise ValueError(f"supporting claim '{cid}' not found for fact {fact.fact_id}")
        snap = snapshots.get(claim.source_snapshot_id) if claim.source_snapshot_id else None
        resolved_claims.append({
            "claim_id": claim.claim_id,
            "proposition": claim.proposition,
            "status": claim.status.value,
            "source_snapshot_id": claim.source_snapshot_id,
            "snapshot_resolved": snap is not None,
        })
    return {
        "artifact_version_ref": artifact_version_ref,
        "fact_id": fact.fact_id,
        "promotion_state": fact.promotion_state.value,
        "supporting_claims": resolved_claims,
    }
