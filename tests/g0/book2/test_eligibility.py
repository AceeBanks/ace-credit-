"""B2.C10 tests — Eligibility Ontology & Deterministic Boundary.

Evaluation is a pure deterministic function; missing evidence is UNKNOWN
(aggregate CONDITIONAL), never fabricated; LLM narrative can never directly
set ELIGIBLE; a new opportunity revision supersedes the old decision.
"""
from __future__ import annotations

import copy
from decimal import Decimal

from prototype.g0.domain.eligibility import (
    evaluate_rule,
    evaluate_rule_set,
    re_evaluate,
)
from prototype.g0.domain.models import (
    EligibilityDecision,
    EligibilityRule,
    EligibilityRuleSet,
    EligibilityStatus,
)
from prototype.g0.domain.revisions import DecisionAnchor, is_stale
from tools.g0.validate_domain import (
    load_eligibility_policy,
    load_revision_policy,
    validate_eligibility_policy,
)

POLICY = load_eligibility_policy()
REVISION_POLICY = load_revision_policy()


def _rule(rid: str, operator: str, expected, fact_types=("organization_kind",),
          subject_type: str = "Organization", **kw) -> EligibilityRule:
    return EligibilityRule(rid, "requirement", subject_type, operator, expected,
                           required_fact_types=fact_types, **kw)


def _set(rid: str, *rules: EligibilityRule) -> EligibilityRuleSet:
    return EligibilityRuleSet(rid, "opp_rev-1", 1, rules)


def test_live_eligibility_policy_passes():
    ok, report = validate_eligibility_policy(POLICY)
    assert ok, report["errors"]
    assert report["operator_count"] == 13


def test_same_inputs_reproduce_same_decision():
    rs = _set("rs-1", _rule("r1", "EQUALS", "nonprofit"))
    facts = {"organization_kind": "nonprofit"}
    d1 = evaluate_rule_set(rs, facts, "d-1", "org-1")
    d2 = evaluate_rule_set(rs, facts, "d-2", "org-1")
    assert d1.result is d2.result is EligibilityStatus.ELIGIBLE
    assert d1.per_rule_results == d2.per_rule_results
    assert d1.explanation == d2.explanation


def test_missing_fact_is_unknown_not_false():
    rs = _set("rs-1", _rule("r1", "EQUALS", "nonprofit"))
    d = evaluate_rule_set(rs, {}, "d-1", "org-1")     # no facts at all
    assert d.per_rule_results[0][1] is EligibilityStatus.UNKNOWN
    assert d.result is EligibilityStatus.CONDITIONAL   # never fabricated ELIGIBLE


def test_closed_world_rule_treats_missing_as_ineligible():
    rs = _set("rs-1", _rule("r1", "EQUALS", "nonprofit", closed_world=True))
    d = evaluate_rule_set(rs, {}, "d-1", "org-1")
    assert d.per_rule_results[0][1] is EligibilityStatus.INELIGIBLE
    assert d.result is EligibilityStatus.INELIGIBLE


def test_any_required_failure_is_ineligible():
    rs = _set("rs-1",
              _rule("r1", "EQUALS", "nonprofit"),
              _rule("r2", "IN", ["GA", "SC"], fact_types=("jurisdiction",)))
    facts = {"organization_kind": "nonprofit", "jurisdiction": "CA"}
    d = evaluate_rule_set(rs, facts, "d-1", "org-1")
    assert d.result is EligibilityStatus.INELIGIBLE


def test_new_opportunity_revision_supersedes_old_decision():
    rs1 = _set("rs-1", _rule("r1", "EQUALS", "nonprofit"))
    facts = {"organization_kind": "nonprofit"}
    old = evaluate_rule_set(rs1, facts, "d-1", "org-1")
    # revision 2 arrives with new terms; the rule set targets the new revision
    rs2 = EligibilityRuleSet("rs-2", "opp_rev-2", 2, rs1.rules)
    new = re_evaluate(old, rs2, facts, "d-2")
    # the old decision object is untouched; the new one is authoritative
    assert old.decision_id == "d-1" and old.result is EligibilityStatus.ELIGIBLE
    assert new.decision_id == "d-2"
    assert new.opportunity_revision_id == "opp_rev-2"
    anchor = DecisionAnchor(old.decision_id, old.opportunity_revision_id)
    from prototype.g0.domain.revisions import RevisionSet, classify_revision
    rs = RevisionSet("opp-1", "GrantOpportunity")
    rs = rs.add(classify_revision("opp_rev-1", 1, ["deadline"],
                                  "2026-08-01T00:00:00Z", REVISION_POLICY))
    rs = rs.add(classify_revision("opp_rev-2", 2, ["eligibility"],
                                  "2026-08-02T00:00:00Z", REVISION_POLICY))
    assert is_stale(anchor, rs) is True


def test_llm_narrative_cannot_directly_set_eligible():
    rs = _set("rs-1", _rule("r1", "EQUALS", "nonprofit"))
    # a narrative blob in the fact table is NOT a fact; the required fact is
    # still missing, so the decision stays CONDITIONAL — narrative can't flip it
    narrative_facts = {"organization_kind": "narrative-text",
                       "narrative": "we are definitely eligible"}
    d = evaluate_rule_set(rs, narrative_facts, "d-1", "org-1")
    assert d.result is not EligibilityStatus.ELIGIBLE


def test_operator_matrix():
    facts = {"organization_kind": "nonprofit", "jurisdiction": "GA",
             "revenue": Decimal("500000"), "formation_date": "2020-05-01",
             "county": "fulton"}
    cases = [
        (_rule("a", "IN", ["nonprofit", "tribal"]), facts, EligibilityStatus.ELIGIBLE),
        (_rule("b", "NOT_IN", ["for_profit"]), facts, EligibilityStatus.ELIGIBLE),
        (_rule("c", "GTE", Decimal("100000"), fact_types=("revenue",)),
         facts, EligibilityStatus.ELIGIBLE),
        (_rule("d", "LTE", Decimal("100000"), fact_types=("revenue",)),
         facts, EligibilityStatus.INELIGIBLE),
        (_rule("e", "BETWEEN", (Decimal("100000"), Decimal("600000")),
               fact_types=("revenue",)), facts, EligibilityStatus.ELIGIBLE),
        (_rule("f", "WITHIN_GEOGRAPHY", ["fulton", "dekalb"], fact_types=("county",)),
         facts, EligibilityStatus.ELIGIBLE),
        (_rule("g", "BEFORE", "2021-01-01", fact_types=("formation_date",)),
         facts, EligibilityStatus.ELIGIBLE),
        (_rule("h", "AFTER", "2019-01-01", fact_types=("formation_date",)),
         facts, EligibilityStatus.ELIGIBLE),
        (_rule("i", "BOOLEAN_TRUE", True, fact_types=("is_501c3",)),
         {"is_501c3": True}, EligibilityStatus.ELIGIBLE),
        (_rule("j", "EXISTS", None, fact_types=("ein",)),
         {"ein": "12-3456789"}, EligibilityStatus.ELIGIBLE),
        (_rule("k", "NOT_EXISTS", None, fact_types=("ein",)),
         {"ein": None}, EligibilityStatus.ELIGIBLE),
    ]
    for rule, ft, expected in cases:
        assert evaluate_rule(rule, ft) is expected, rule.operator


# --- validator defect injection ------------------------------------------------

def test_unknown_operator_set_fails():
    data = copy.deepcopy(POLICY)
    data["operators"].append("VIBES")
    ok, report = validate_eligibility_policy(data)
    assert not ok
    assert any("operators" in e for e in report["errors"])


def test_missing_evidence_semantics_must_be_unknown():
    data = copy.deepcopy(POLICY)
    data["missing_evidence_semantics"] = "FALSE"
    ok, report = validate_eligibility_policy(data)
    assert not ok
    assert any("UNKNOWN" in e for e in report["errors"])


def test_narrative_can_set_result_fails():
    data = copy.deepcopy(POLICY)
    data["extraction_boundary"]["llm_narrative_cannot_set_result"] = False
    ok, report = validate_eligibility_policy(data)
    assert not ok
    assert any("llm_narrative_cannot_set_result" in e for e in report["errors"])
