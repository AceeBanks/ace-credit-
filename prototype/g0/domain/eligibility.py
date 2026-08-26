"""G0 Book 2 — B2.C10 deterministic eligibility evaluation.

Interpretation (solicitation -> candidate rule) is separate from evaluation
(validated rule + canonical facts -> deterministic result). Evaluation here is
a pure function: same rule set + same facts -> same decision, always.

Missing evidence yields UNKNOWN (aggregate CONDITIONAL), never fabricated
eligibility. A fact counts as false only when the rule explicitly declares
closed-world behavior. LLM narrative output can never directly set ELIGIBLE —
the only way to produce a decision is this deterministic engine.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from prototype.g0.domain.models import (
    EligibilityDecision,
    EligibilityRule,
    EligibilityRuleSet,
    EligibilityStatus,
)


def _to_decimal(value) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _to_date(value) -> date | None:
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def evaluate_rule(rule: EligibilityRule, fact_values: dict) -> EligibilityStatus:
    """Deterministic per-rule evaluation over a fact table keyed by fact type.

    `fact_values` maps fact type -> value (the types named in
    rule.required_fact_types). Missing keys are UNKNOWN unless the rule
    declares closed_world, in which case absence counts as false.
    """
    op = rule.operator
    fact_key = rule.required_fact_types[0] if rule.required_fact_types else None

    if fact_key is not None and fact_key not in fact_values:
        # missing evidence: UNKNOWN unless the rule is explicitly closed-world
        if rule.closed_world:
            if op in ("EXISTS", "EQUALS", "IN", "GTE", "LTE", "BETWEEN",
                      "WITHIN_GEOGRAPHY", "BEFORE", "AFTER", "BOOLEAN_TRUE"):
                return EligibilityStatus.INELIGIBLE
            if op == "NOT_EXISTS":
                return EligibilityStatus.ELIGIBLE
            return EligibilityStatus.UNKNOWN
        return EligibilityStatus.UNKNOWN

    if fact_key is None:
        # rules like EXISTS/NOT_EXISTS over subject-level state still need a key
        if op in ("EXISTS", "NOT_EXISTS") and rule.subject_type:
            present = rule.subject_type in fact_values
            return (EligibilityStatus.ELIGIBLE if present else
                    (EligibilityStatus.INELIGIBLE if rule.closed_world
                     else EligibilityStatus.UNKNOWN)) if op == "EXISTS" else \
                (EligibilityStatus.INELIGIBLE if present else EligibilityStatus.ELIGIBLE)
        return EligibilityStatus.UNKNOWN

    value = fact_values[fact_key]
    expected = rule.expected_value

    if op == "EXISTS":
        return EligibilityStatus.ELIGIBLE if value is not None else EligibilityStatus.INELIGIBLE
    if op == "NOT_EXISTS":
        return EligibilityStatus.INELIGIBLE if value is not None else EligibilityStatus.ELIGIBLE
    if op == "EQUALS":
        return EligibilityStatus.ELIGIBLE if value == expected else EligibilityStatus.INELIGIBLE
    if op == "IN":
        return EligibilityStatus.ELIGIBLE if value in expected else EligibilityStatus.INELIGIBLE
    if op == "NOT_IN":
        return EligibilityStatus.INELIGIBLE if value in expected else EligibilityStatus.ELIGIBLE
    if op == "BOOLEAN_TRUE":
        return EligibilityStatus.ELIGIBLE if value is True else EligibilityStatus.INELIGIBLE
    if op == "GTE":
        v, e = _to_decimal(value), _to_decimal(expected)
        return (EligibilityStatus.ELIGIBLE if v >= e else EligibilityStatus.INELIGIBLE
                if v is not None and e is not None else EligibilityStatus.UNKNOWN)
    if op == "LTE":
        v, e = _to_decimal(value), _to_decimal(expected)
        return (EligibilityStatus.ELIGIBLE if v <= e else EligibilityStatus.INELIGIBLE
                if v is not None and e is not None else EligibilityStatus.UNKNOWN)
    if op == "BETWEEN":
        v = _to_decimal(value)
        lo, hi = _to_decimal(expected[0]), _to_decimal(expected[1])
        if v is None or lo is None or hi is None:
            return EligibilityStatus.UNKNOWN
        return (EligibilityStatus.ELIGIBLE if lo <= v <= hi
                else EligibilityStatus.INELIGIBLE)
    if op == "WITHIN_GEOGRAPHY":
        return (EligibilityStatus.ELIGIBLE if value in expected
                else EligibilityStatus.INELIGIBLE)
    if op in ("BEFORE", "AFTER"):
        v, e = _to_date(value), _to_date(expected)
        if v is None or e is None:
            return EligibilityStatus.UNKNOWN
        ok = v < e if op == "BEFORE" else v > e
        return EligibilityStatus.ELIGIBLE if ok else EligibilityStatus.INELIGIBLE
    if op == "CUSTOM_DETERMINISTIC_PREDICATE":
        # deterministic only when a callable predicate is supplied; otherwise
        # the rule cannot be evaluated here and fails closed to UNKNOWN
        pred = getattr(rule, "_predicate_fn", None)
        if pred is None:
            return EligibilityStatus.UNKNOWN
        try:
            return (EligibilityStatus.ELIGIBLE if bool(pred(value))
                    else EligibilityStatus.INELIGIBLE)
        except Exception:
            return EligibilityStatus.UNKNOWN
    return EligibilityStatus.UNKNOWN


def evaluate_rule_set(rule_set: EligibilityRuleSet, fact_values: dict,
                      decision_id: str, organization_id: str,
                      fact_version_refs: tuple[str, ...] = ()) -> EligibilityDecision:
    """Deterministic aggregate decision. The ONLY path to an EligibilityDecision.

    Aggregate semantics (eligibility_policy.yaml): any REQUIRED failure ->
    INELIGIBLE; else any UNKNOWN -> CONDITIONAL; else ELIGIBLE.
    """
    per_rule: list[tuple[str, EligibilityStatus]] = []
    for rule in rule_set.rules:
        status = evaluate_rule(rule, fact_values)
        per_rule.append((rule.rule_id, status))

    any_failure = any(s is EligibilityStatus.INELIGIBLE
                      for _, s in per_rule)
    any_unknown = any(s is EligibilityStatus.UNKNOWN for _, s in per_rule)
    if any_failure:
        result = EligibilityStatus.INELIGIBLE
    elif any_unknown:
        result = EligibilityStatus.CONDITIONAL
    else:
        result = EligibilityStatus.ELIGIBLE

    explanation = "; ".join(f"{rid}={s.value}" for rid, s in per_rule)
    return EligibilityDecision(
        decision_id=decision_id,
        organization_id=organization_id,
        opportunity_revision_id=rule_set.opportunity_revision_id,
        rule_set_id=rule_set.rule_set_id,
        rule_set_version=rule_set.version,
        result=result,
        per_rule_results=tuple(per_rule),
        explanation=explanation,
    )


def re_evaluate(decision: EligibilityDecision, new_rule_set: EligibilityRuleSet,
                fact_values: dict, new_decision_id: str,
                fact_version_refs: tuple[str, ...] = ()) -> EligibilityDecision:
    """Evaluate against a NEW opportunity revision/rule set. The old decision
    object is immutable and untouched (B2.C8): the new decision supersedes it
    and the old one is marked stale via the C8 revision machinery."""
    return evaluate_rule_set(new_rule_set, fact_values, new_decision_id,
                             decision.organization_id, fact_version_refs)
