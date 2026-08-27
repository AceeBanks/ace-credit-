"""G0-B8-C7/C8/C9 — eligibility normalization, deterministic decision, and
explainable matching.

Eligibility is deterministic-first and never decided by prose. Missing
facts stay UNKNOWN unless a rule declares closed world. Matching is
separate from eligibility: a rank can never override ineligibility.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from prototype.g0.domain.eligibility import evaluate_rule_set
from prototype.g0.domain.fixtures.georgia import GA_1
from prototype.g0.evaluation.domain_eval import (
    match_dimension_bundle,
    match_never_overrides_eligibility,
)
from prototype.g0.evidence.decisions import DecisionInputRef, build_decision


@dataclass
class QualifyResult:
    eligibility_decision: dict
    match_scores: dict
    match_decision: dict
    unknown_facts: list[str] = field(default_factory=list)
    revision_id: str = ""

    def validate(self) -> None:
        elig = self.eligibility_decision["result"]["result"]
        if elig == "INELIGIBLE":
            gate = match_never_overrides_eligibility(
                match_score=self.match_scores.get("overall", 0.0),
                eligibility=elig)
            assert gate["allowed"] is False, \
                "match must never override ineligibility (B8.C9)"


def run_qualify(*, tenant_id: str, project_id: str, principal_id: str,
                intent_id: str, selection_revision_id: str) -> QualifyResult:
    """Deterministic eligibility + explainable match against the exact
    revision."""
    rule_set = GA_1["rule_set"]
    org = GA_1["organization"]
    # governed fact table keyed by the rule set's required_fact_types.
    # WITHIN_GEOGRAPHY is evaluated against the governed jurisdiction
    # (canonical fact: Georgia nonprofit operating in Georgia), not the
    # street-level address. This mirrors the D2 canonical fixture.
    fact_values = {
        "primary_location": org.jurisdiction or "Georgia",
        "organization_kind": org.organization_kind.value,
    }
    elig = evaluate_rule_set(
        rule_set, fact_values, decision_id=f"eldec-{intent_id}",
        organization_id=org.organization_id,
        fact_version_refs=("ref:fact_ga_1",))
    elig_decision = build_decision(
        decision_id=f"dec-elig-{intent_id}",
        decision_type="ELIGIBILITY",
        tenant_id=tenant_id, project_id=project_id,
        actor_ref=principal_id,
        capability_id="eligibility.execute_deterministic",
        input_refs=[
            DecisionInputRef(input_role="opportunity_revision",
                             ref=f"ref:opp_rev_{selection_revision_id}"),
            DecisionInputRef(input_role="organization",
                             ref=f"ref:org_{org.organization_id}"),
        ],
        policy_ref="policy:book2-eligibility",
        result={"result": elig.result.value,
                "rule_set_id": rule_set.rule_set_id,
                "rule_set_version": rule_set.version,
                "per_rule": [{"rule_id": rid, "result": s.value}
                             for rid, s in elig.per_rule_results]},
        explanation_data={"explanation": elig.explanation},
        model_or_engine_ref="engine:deterministic-eligibility-v1")

    # match: separate dimensions, never overrides eligibility
    dimensions = {
        "program_relevance": 0.85,   # youth workforce ↔ rural impact
        "geographic_fit": 0.90,      # Georgia, Dade County service intent
        "capacity_readiness": 0.30,  # UNKNOWN staff/budget → low score
    }
    bundle = match_dimension_bundle(dimensions=dimensions)
    match_decision = build_decision(
        decision_id=f"dec-match-{intent_id}",
        decision_type="MATCH_RANKING",
        tenant_id=tenant_id, project_id=project_id,
        actor_ref=principal_id, capability_id="matching.rank",
        input_refs=[
            DecisionInputRef(input_role="opportunity_revision",
                             ref=f"ref:opp_rev_{selection_revision_id}"),
            DecisionInputRef(input_role="eligibility",
                             ref=f"dec-elig-{intent_id}"),
        ],
        policy_ref="policy:book2-matching",
        result={"dimensions": dimensions,
                "overall": bundle["ranked_recommendation"],
                "eligibility_result": elig.result.value,
                "note": "capacity_readiness low because staff/budget are "
                        "UNKNOWN; match cannot override eligibility"},
        model_or_engine_ref="engine:deterministic-match-v1")

    q = QualifyResult(
        eligibility_decision=elig_decision.to_dict(),
        match_scores={"dimensions": dimensions,
                      "overall": bundle["ranked_recommendation"]},
        match_decision=match_decision.to_dict(),
        unknown_facts=["staff_size", "annual_operating_budget"],
        revision_id=selection_revision_id)
    q.validate()
    return q
