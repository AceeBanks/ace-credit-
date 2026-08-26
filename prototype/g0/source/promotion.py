"""G0-B3-C10 — Evidence confidence & promotion model.

Defines how candidate claims become usable evidence / canonical facts. Promotion
state is explicit and governed: CANDIDATE -> ... -> VERIFIED (or REJECTED /
SUPERSEDED / CONFLICTED / STALE).

No opaque scalar requirement: a total score may be computed for ranking, but
the underlying confidence components and the decision reason remain available
on the promotion event.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PromotionState(Enum):
    CANDIDATE = "CANDIDATE"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"
    CONFLICTED = "CONFLICTED"
    STALE = "STALE"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


# Confidence components the promotion model must be able to carry.
CONFIDENCE_COMPONENTS = {
    "source_authority",
    "directness_of_support",
    "extraction_quality",
    "normalization_confidence",
    "corroboration",
    "freshness",
    "contradiction_state",
    "identity_resolution",
    "geography_population_fit",
    "temporal_applicability",
}

# Critical fact classes that demand official/direct source or explicit exception.
CRITICAL_FACT_CLASSES = {
    "opportunity_deadline",
    "opportunity_eligibility",
    "opportunity_award_ceiling",
    "opportunity_required_attachments",
    "legal_organization_name",
    "tax_exempt_status",
    "opportunity_submission_instructions",
}


@dataclass(frozen=True)
class PromotionRule:
    fact_class: str
    min_authority_required: str  # e.g. "OFFICIAL_*" or "any"
    allow_narrative_multiple: bool = False
    client_approval_controls: bool = False


@dataclass
class Confidence:
    components: dict  # keyed by CONFIDENCE_COMPONENTS -> float in [0,1]

    @property
    def total_score(self) -> float:
        vals = [v for v in self.components.values() if isinstance(v, (int, float))]
        return (sum(vals) / len(vals)) if vals else 0.0

    def explain(self) -> dict:
        # keep the underlying components available (no opaque scalar)
        return dict(self.components)


@dataclass
class PromotionEvent:
    promotion_event_id: str
    claim_id: str
    target_fact_id: str
    old_state: PromotionState
    new_state: PromotionState
    reason_codes: list[str] = field(default_factory=list)
    policy_version: str = "1.0"
    source_refs: list[str] = field(default_factory=list)
    confidence: Optional[Confidence] = None
    resolver_actor: Optional[str] = None
    resolved_at: Optional[str] = None


class PromotionGovernor:
    """Applies promotion policy and records every transition."""

    def __init__(self, rules: dict[str, PromotionRule], policy_version: str = "1.0") -> None:
        self._rules = rules
        self._policy_version = policy_version
        self._events: list[PromotionEvent] = []
        self._state: dict[str, PromotionState] = {}

    def state(self, target_fact_id: str) -> Optional[PromotionState]:
        return self._state.get(target_fact_id)

    def promote(self, claim_id: str, target_fact_id: str, rule: PromotionRule,
                source_classes: list[str], confidence: Confidence,
                resolver_actor: str | None = None,
                client_approved: bool = False) -> PromotionState:
        old = self._state.get(target_fact_id, PromotionState.CANDIDATE)
        new, reasons = self._decide(rule, source_classes, confidence, client_approved)
        self._state[target_fact_id] = new
        self._events.append(PromotionEvent(
            promotion_event_id=f"pe_{claim_id}", claim_id=claim_id,
            target_fact_id=target_fact_id, old_state=old, new_state=new,
            reason_codes=reasons, policy_version=self._policy_version,
            confidence=confidence, resolver_actor=resolver_actor))
        return new

    def _decide(self, rule: PromotionRule, source_classes: list[str],
                confidence: Confidence, client_approved: bool) -> tuple[PromotionState, list[str]]:
        if rule.client_approval_controls:
            if client_approved:
                return PromotionState.VERIFIED, ["client_approval_controls"]
            return PromotionState.PROVISIONAL, ["awaiting_client_approval"]
        if rule.fact_class in CRITICAL_FACT_CLASSES:
            official = any(sc.startswith("OFFICIAL_") for sc in source_classes)
            if not official:
                return (PromotionState.CONFLICTED,
                        ["critical_fact_without_official_or_direct_source"])
            if confidence.total_score < 0.7:
                return PromotionState.STALE, ["low_conf_critical_fact"]
            return PromotionState.VERIFIED, ["official_source", "conf_critical_ok"]
        # non-critical / narrative/context: allow multiple credible institutional sources
        if rule.allow_narrative_multiple and confidence.total_score >= 0.5:
            return PromotionState.VERIFIED, ["narrative_multiple_institutional"]
        if confidence.total_score < 0.4:
            return PromotionState.REJECTED, ["low_confidence"]
        return PromotionState.PROVISIONAL, ["candidate_needs_more"]

    @property
    def events(self) -> list[PromotionEvent]:
        return list(self._events)


def make_rule(fact_class: str, critical: bool | None = None,
              narrative: bool = False, client_controls: bool = False) -> PromotionRule:
    if critical is None:
        critical = fact_class in CRITICAL_FACT_CLASSES
    min_auth = "OFFICIAL_*" if critical else "any"
    return PromotionRule(fact_class=fact_class, min_authority_required=min_auth,
                         allow_narrative_multiple=narrative,
                         client_approval_controls=client_controls)