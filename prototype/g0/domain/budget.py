"""G0 Book 2 — B2.C12 budget & financial semantics.

Money is Decimal-only; totals are computed, never hand-written; currency and
period are explicit; amounts carry assumption/source lineage. The LLM never
improvises arithmetic on canonical money — these pure functions are the only
way totals and ratios are produced.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from prototype.g0.domain.models import Budget, BudgetLine, CostShare


def reconcile(budget: Budget) -> Decimal:
    """Deterministic total across all lines. Pure computation."""
    return budget.total


def total_by_category(budget: Budget) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for line in budget.lines:
        out[line.category] = out.get(line.category, Decimal("0")) + line.amount
    return out


def currency_mismatches(budget: Budget) -> list[str]:
    """Explicit currency rule: every line must carry the budget currency."""
    return [f"{line.line_id}: currency '{line.currency}' != budget '{budget.currency}'"
            for line in budget.lines if line.currency != budget.currency]


def check_ceiling(budget: Budget, ceiling: Decimal | None) -> list[str]:
    """Requested amount must be <= applicable ceiling where a rule exists."""
    if ceiling is None:
        return []
    if budget.total > ceiling:
        return [f"budget {budget.budget_id} total {budget.total} exceeds ceiling {ceiling}"]
    return []


def match_total(cost_share: CostShare) -> Decimal:
    """Deterministic match/cost-share total (cash + in-kind FMV)."""
    return cost_share.total


def match_ratio(cost_share: CostShare, requested: Decimal) -> Decimal | None:
    """Match ratio as a fraction of the requested amount (e.g. 0.25 = 25%)."""
    if requested == 0:
        return None
    return match_total(cost_share) / requested


def narrative_amount_mismatch(narrative_figure: Decimal, budget_total: Decimal,
                              tolerance: Decimal = Decimal("0.01")) -> bool:
    """Detect narrative-vs-budget figure discrepancy (B2.C12 narrative linkage)."""
    return abs(narrative_figure - budget_total) > tolerance


def validate_amounts(budget: Budget) -> list[str]:
    """Decimal-only rule: float money is prohibited (B2.C12)."""
    errors: list[str] = []
    for line in budget.lines:
        if not isinstance(line.amount, Decimal):
            errors.append(f"{line.line_id}: amount must be Decimal, got {type(line.amount).__name__}")
    return errors
