"""B5.C4-C6 — Evidence quality, claim support/promotion and contradiction
resolution (prototype).

  * quality scoring: dimensions stay inspectable; composite is reproducible;
    high authority + stale is never silently high confidence; conflicting
    authoritative evidence cannot be averaged away;
  * support: support types distinguish direct/corroborating/derived/user-
    attested/official; the same support cannot masquerade as independent
    corroboration; unsupported claims cannot promote under support policies;
  * contradiction: unit mismatch is detected before value conflict; equal
    authority stays OPEN; resolution events are append-only and retain the
    losing claim (EVID-LAW-005); confidence scores never resolve conflicts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

DIMENSIONS = ("authority", "directness", "freshness", "specificity",
              "corroboration", "extraction_quality", "identity_certainty",
              "temporal_fit")


class EvidenceQualityError(ValueError):
    """Raised when a quality/support/contradiction rule is violated."""


@dataclass
class EvidenceQuality:
    quality_id: str
    evidence_ref: str
    dimensions: dict[str, float]
    quality_class: str
    computed_by: str
    composite_score: float | None = None

    def __post_init__(self) -> None:
        if not all(0.0 <= v <= 1.0 for v in self.dimensions.values()):
            raise EvidenceQualityError("dimension values must be in [0,1]")
        missing = set(DIMENSIONS) - set(self.dimensions)
        if missing:
            raise EvidenceQualityError(f"missing dimensions: {sorted(missing)}")
        if self.composite_score is not None and not (0.0 <= self.composite_score <= 1.0):
            raise EvidenceQualityError("composite must be in [0,1]")


def score_quality(*, evidence_ref: str, dimensions: dict[str, float],
                  class_rule: dict | None = None,
                  composite_weights: dict[str, float] | None = None) -> EvidenceQuality:
    """Deterministic quality scoring with class derivation.

    QUAL-001: a stale evidence never derives VERIFIED_HIGH even with perfect
    authority — the class rule checks the freshness dimension first.
    """
    q = EvidenceQuality(
        quality_id=f"qual-{abs(hash((evidence_ref, str(dimensions))))}",
        evidence_ref=evidence_ref, dimensions=dict(dimensions),
        quality_class="PROVISIONAL", computed_by="quality-engine-v1")
    # class derivation (QUAL-001): stale can never be VERIFIED_HIGH
    if dimensions["freshness"] < 0.3:
        q.quality_class = "STALE"
    elif dimensions["authority"] >= 0.8 and dimensions["directness"] >= 0.7 \
            and dimensions["freshness"] >= 0.6 and dimensions["specificity"] >= 0.6 \
            and dimensions["corroboration"] >= 0.4:
        q.quality_class = "VERIFIED_HIGH"
    elif dimensions["authority"] >= 0.6:
        q.quality_class = "VERIFIED_MODERATE"
    else:
        q.quality_class = "PROVISIONAL"
    weights = composite_weights or {
        "authority": 0.25, "directness": 0.15, "freshness": 0.2,
        "specificity": 0.1, "corroboration": 0.15, "extraction_quality": 0.05,
        "identity_certainty": 0.05, "temporal_fit": 0.05}
    q.composite_score = round(
        sum(dimensions[d] * weights.get(d, 0.0) for d in DIMENSIONS), 4)
    return q


def authoritative_conflict_guard(qualities: list[EvidenceQuality]) -> None:
    """QUAL-003: conflicting authoritative evidence cannot be averaged away."""
    authoritative = [q for q in qualities if q.dimensions["authority"] >= 0.8]
    conflicting_classes = {q.quality_class for q in authoritative}
    if len(authoritative) >= 2 and len(conflicting_classes) > 1:
        raise EvidenceQualityError(
            "conflicting authoritative evidence must surface as CONFLICTED, "
            "never averaged")


# ---------------------------------------------------------------- support

SUPPORT_TYPES = ("DIRECT", "CORROBORATING", "DERIVED", "USER_ATTESTED",
                 "ADMIN_VERIFIED", "OFFICIAL_RECORD", "STATISTICAL_CONTEXT")


@dataclass
class SupportAssertion:
    support_id: str
    claim_ref: str
    evidence_ref: str
    support_type: str
    created_at: str
    method: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "support_id": self.support_id, "claim_ref": self.claim_ref,
            "evidence_ref": self.evidence_ref, "support_type": self.support_type,
            "created_at": self.created_at, "method": self.method,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def independent_corroboration(supports: list[SupportAssertion],
                              upstream_map: dict[str, str]) -> bool:
    """Same upstream article copied twice is NOT independent corroboration."""
    upstreams = set()
    for s in supports:
        if s.support_type != "CORROBORATING":
            continue
        upstream = upstream_map.get(s.evidence_ref, s.evidence_ref)
        if upstream in upstreams:
            return False
        upstreams.add(upstream)
    return len(upstreams) >= 2


def promote_claim(*, claim_ref: str, support_assertions: list[SupportAssertion],
                  contradictions: list[dict], policy_ref: str,
                  min_support_types: set[str] | None = None) -> dict:
    """EVID-LAW-004: explicit governed promotion.

    Fails when: no support, unsupported claim, or an open contradiction of
    P0/P1 severity (EVID-LAW-014: confidence never resolves it).
    """
    min_types = min_support_types or {"DIRECT", "OFFICIAL_RECORD"}
    if not support_assertions:
        raise EvidenceQualityError(
            "unsupported claim cannot promote under support policy "
            f"{policy_ref}")
    actual = {s.support_type for s in support_assertions}
    if not (actual & min_types):
        raise EvidenceQualityError(
            f"support policy {policy_ref} requires one of {sorted(min_types)}; "
            f"got {sorted(actual)}")
    open_critical = [c for c in contradictions
                     if c.get("status") == "OPEN" and c.get("severity") in ("P0", "P1")]
    if open_critical:
        raise EvidenceQualityError(
            "cannot promote while an open P0/P1 contradiction exists: "
            f"{[c['contradiction_id'] for c in open_critical]}")
    return {
        "promotion": f"prom-{abs(hash(claim_ref))}",
        "claim_ref": claim_ref,
        "support_set": [s.support_id for s in support_assertions],
        "contradiction_set": [c["contradiction_id"] for c in contradictions],
        "policy_ref": policy_ref,
        "result": "PROMOTED",
        "promoted_at": _now(),
    }


def derived_fact_replay(method_version: str, inputs: list[Any],
                        compute) -> dict:
    """EVID-LAW-009: derived facts replay deterministically."""
    value = compute(inputs)
    return {"method_version": method_version, "inputs": list(inputs),
            "value": value}


# ---------------------------------------------------------- contradictions

@dataclass
class Contradiction:
    contradiction_id: str
    subject_scope: dict
    predicate: str
    claim_refs: list[str]
    contradiction_type: str
    severity: str
    status: str = "OPEN"
    opened_at: str = ""
    resolved_at: str | None = None
    resolution_event_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "contradiction_id": self.contradiction_id,
            "subject_scope": dict(self.subject_scope), "predicate": self.predicate,
            "claim_refs": list(self.claim_refs),
            "contradiction_type": self.contradiction_type,
            "severity": self.severity, "status": self.status,
            "opened_at": self.opened_at, "resolved_at": self.resolved_at,
            "resolution_event_ref": self.resolution_event_ref,
        }


UNIT_SYMBOLS = {"$": "USD", "USD": "USD", "k": "THOUSAND", "m": "MILLION",
                "%": "PERCENT", "pp": "PERCENT_POINT", "acres": "ACRES",
                "sqmi": "SQMI"}


def detect_unit_conflict(left: dict, right: dict) -> bool:
    """UNIT_CONFLICT is detected before VALUE_CONFLICT."""
    lu = UNIT_SYMBOLS.get(left.get("unit", ""), left.get("unit"))
    ru = UNIT_SYMBOLS.get(right.get("unit", ""), right.get("unit"))
    return lu != ru


def open_contradiction(*, contradiction_id: str, tenant_id: str,
                       entity_type: str, entity_id: str, predicate: str,
                       claim_refs: list[str], contradiction_type: str,
                       severity: str) -> Contradiction:
    if len(claim_refs) < 2:
        raise EvidenceQualityError("contradiction requires at least 2 claims")
    if contradiction_type not in ("VALUE_CONFLICT", "IDENTITY_CONFLICT",
                                  "TEMPORAL_CONFLICT", "SOURCE_REVISION_CONFLICT",
                                  "SCOPE_CONFLICT", "UNIT_CONFLICT",
                                  "INTERPRETATION_CONFLICT"):
        raise EvidenceQualityError(f"unknown contradiction type "
                                   f"{contradiction_type!r}")
    return Contradiction(
        contradiction_id=contradiction_id,
        subject_scope={"tenant_id": tenant_id, "entity_type": entity_type,
                       "entity_id": entity_id},
        predicate=predicate, claim_refs=list(claim_refs),
        contradiction_type=contradiction_type, severity=severity,
        opened_at=_now())


@dataclass
class ResolutionEvent:
    resolution_id: str
    contradiction_id: str
    conflicting_claim_refs: list[str]
    resolution_status: str
    resolved_at: str
    resolved_by: str
    policy_ref: str
    chosen_operational_fact_ref: str | None = None
    reason: str = ""
    approval_ref: str | None = None
    downstream_invalidations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "resolution_id": self.resolution_id,
            "contradiction_id": self.contradiction_id,
            "conflicting_claim_refs": list(self.conflicting_claim_refs),
            "chosen_operational_fact_ref": self.chosen_operational_fact_ref,
            "resolution_status": self.resolution_status, "reason": self.reason,
            "policy_ref": self.policy_ref, "approval_ref": self.approval_ref,
            "resolved_at": self.resolved_at, "resolved_by": self.resolved_by,
            "downstream_invalidations": list(self.downstream_invalidations),
        }


def resolve_contradiction(*, contradiction: Contradiction, chosen_fact_ref: str | None,
                          policy_ref: str, resolved_by: str, reason: str,
                          approval_ref: str | None = None,
                          resolution_status: str | None = None,
                          model_confidence: float | None = None) -> ResolutionEvent:
    """CONTR-001/002: confidence cannot resolve; equal authority stays OPEN.

    A resolution is only valid for non-OPEN contradictions opened with a
    governing method; "higher model confidence" is never accepted as a reason.
    """
    if model_confidence is not None:
        raise EvidenceQualityError(
            "model confidence cannot resolve a contradiction (CONTR-001)")
    if "confidence" in reason.lower() or "model says" in reason.lower():
        raise EvidenceQualityError(
            "higher-confidence-model-output is not a valid resolution policy")
    lowered = reason.lower()
    if ("newer" in lowered and "wins" in lowered) or \
            ("recency" in lowered and "resolve" in lowered):
        raise EvidenceQualityError(
            "newer-source-automatically-wins is not a valid resolution policy "
            "(CONTR-003: historical effective dates govern)")
    if contradiction.status != "OPEN":
        raise EvidenceQualityError(
            f"contradiction {contradiction.contradiction_id} is not OPEN")
    if resolution_status is None:
        if chosen_fact_ref is None:
            raise EvidenceQualityError(
                "UNRESOLVED_ACCEPTED requires explicit status; equal-authority "
                "conflicts stay OPEN until a governed resolution exists")
        resolution_status = "RESOLVED_HUMAN" if approval_ref else "RESOLVED_SOURCE_PRECEDENCE"
    event = ResolutionEvent(
        resolution_id=f"res-{abs(hash(contradiction.contradiction_id))}",
        contradiction_id=contradiction.contradiction_id,
        conflicting_claim_refs=list(contradiction.claim_refs),
        resolution_status=resolution_status, resolved_at=_now(),
        resolved_by=resolved_by, policy_ref=policy_ref,
        chosen_operational_fact_ref=chosen_fact_ref, reason=reason,
        approval_ref=approval_ref)
    contradiction.status = resolution_status
    contradiction.resolved_at = event.resolved_at
    contradiction.resolution_event_ref = event.resolution_id
    return event


def equal_authority_must_stay_open(qualities: list[EvidenceQuality]) -> bool:
    """CONTR-002: equal-authority conflicts cannot be force-closed."""
    authorities = [q.dimensions["authority"] for q in qualities]
    return len(set(authorities)) <= 1 and len(authorities) >= 2


def reopen_on_amendment(contradiction: Contradiction,
                        amendment_refs: list[str]) -> bool:
    """CONTR-004 / ADV-36: a previously-resolved contradiction becomes OPEN
    again when a new amendment (SUPERSEDES/new-revision) touches one of its
    claims/facts — old resolutions do not permanently close conflicts."""
    if contradiction.status in ("OPEN", "UNRESOLVED_ACCEPTED"):
        return False
    touched = set(contradiction.claim_refs)
    if any(a in touched for a in amendment_refs):
        contradiction.status = "OPEN"
        contradiction.resolved_at = None
        contradiction.resolution_event_ref = None
        return True
    return False
