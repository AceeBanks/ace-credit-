"""B2.C12 tests — Budget & Financial Semantic Model.

Money is Decimal-only; totals are computed; currency/period explicit; amounts
carry lineage; narrative figures are checked against budget lines; match and
cost share are deterministic.
"""
from __future__ import annotations

import copy
from decimal import Decimal

import pytest

from prototype.g0.domain.budget import (
    check_ceiling,
    currency_mismatches,
    match_ratio,
    match_total,
    narrative_amount_mismatch,
    reconcile,
    total_by_category,
    validate_amounts,
)
from prototype.g0.domain.models import (
    Budget,
    BudgetLine,
    CostShare,
    InKindContribution,
    MatchContribution,
    Period,
)
from tools.g0.validate_domain import load_budget_policy, validate_budget_policy

POLICY = load_budget_policy()


def _budget(*lines: BudgetLine, currency: str = "USD", **kw) -> Budget:
    return Budget("budget-1", "app-1", currency=currency, lines=lines, **kw)


def test_live_budget_policy_passes():
    ok, report = validate_budget_policy(POLICY)
    assert ok, report["errors"]
    assert report["monetary_rule_count"] == 5


def test_totals_reconcile():
    b = _budget(BudgetLine("l1", "personnel", Decimal("50000.00")),
                BudgetLine("l2", "supplies", Decimal("12500.50")))
    assert reconcile(b) == Decimal("62500.50")
    assert b.total == Decimal("62500.50")          # computed, never hand-written
    by_cat = total_by_category(b)
    assert by_cat == {"personnel": Decimal("50000.00"), "supplies": Decimal("12500.50")}


def test_requested_amount_within_applicable_ceiling():
    b = _budget(BudgetLine("l1", "personnel", Decimal("80000.00")))
    assert check_ceiling(b, Decimal("100000")) == []
    assert check_ceiling(b, Decimal("75000")) != []   # exceeds ceiling
    assert check_ceiling(b, None) == []               # no rule -> no constraint


def test_match_calculation_is_deterministic():
    cash = MatchContribution("m1", "src-1", Decimal("25000.00"))
    inkind = InKindContribution("k1", "src-2", "volunteer labor", Decimal("5000.00"))
    cs = CostShare("cs-1", match_contributions=(cash,),
                   in_kind_contributions=(inkind,))
    assert match_total(cs) == Decimal("30000.00")
    assert match_ratio(cs, Decimal("100000")) == Decimal("0.3")
    # deterministic: same inputs, same result
    assert match_ratio(cs, Decimal("100000")) == match_ratio(cs, Decimal("100000"))


def test_narrative_amount_mismatch_detected():
    b = _budget(BudgetLine("l1", "personnel", Decimal("50000.00")))
    assert narrative_amount_mismatch(Decimal("50000.00"), b.total) is False
    assert narrative_amount_mismatch(Decimal("51000.00"), b.total) is True


def test_currency_mismatch_rejected():
    b = _budget(BudgetLine("l1", "personnel", Decimal("50000.00"), currency="EUR"))
    errors = currency_mismatches(b)
    assert any("EUR" in e for e in errors)
    assert currency_mismatches(_budget(BudgetLine("l1", "personnel",
                                                  Decimal("50000.00")))) == []


def test_float_money_rejected():
    b = _budget(BudgetLine("l1", "personnel", 50000.0))     # float, not Decimal
    errors = validate_amounts(b)
    assert any("must be Decimal" in e for e in errors)
    assert validate_amounts(_budget(BudgetLine("l1", "personnel",
                                               Decimal("50000.00")))) == []


def test_explicit_period_on_budget():
    period = Period("p1", "FY2026", "2025-07-01", "2026-06-30")
    b = _budget(BudgetLine("l1", "personnel", Decimal("1.00")), period=period)
    assert b.period is period


# --- validator defect injection ------------------------------------------------

def test_missing_monetary_rule_fails():
    data = copy.deepcopy(POLICY)
    data["monetary_rules"] = [r for r in data["monetary_rules"]
                              if r["rule"] != "decimal_only"]
    ok, report = validate_budget_policy(data)
    assert not ok
    assert any("monetary_rules" in e for e in report["errors"])


def test_currency_mismatch_must_be_rejected():
    data = copy.deepcopy(POLICY)
    data["currency_mismatch"] = "WARN"
    ok, report = validate_budget_policy(data)
    assert not ok
    assert any("currency_mismatch" in e for e in report["errors"])
