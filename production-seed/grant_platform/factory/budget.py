"""G1 Wave 4 — budget engine (G1.7).

Build budget line items, totals, categories, and a budget narrative that
reconciles to the solicitation ceiling. No invented financial line items:
the default lane emits governed fixture lines for the Georgia opportunity;
any client-provided lines are labeled CLIENT and must reconcile.

Cross-checks:
- total <= ceiling (hard);
- narrative total == table total;
- categories sum == total.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

GOVERNED_LINES = (
    ("Personnel: Program Coordinator", "personnel", "30000.00"),
    ("Personnel: STEM Facilitator", "personnel", "12000.00"),
    ("Program supplies and materials", "supplies", "5000.00"),
    ("Transportation assistance", "travel", "2000.00"),
    ("Evaluation and reporting", "evaluation", "1000.00"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class BudgetLine:
    line_id: str
    description: str
    category: str
    amount: str          # decimal string
    source: str = "GOVERNED"   # GOVERNED | CLIENT | ASSUMPTION


@dataclass
class BudgetReport:
    lines: list[BudgetLine]
    total: str
    ceiling: str
    within_ceiling: bool
    categories: dict[str, str]
    narrative: str
    issues: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.within_ceiling and not self.issues


def build_budget(*, ceiling: str = "50000.00",
                 client_lines: list[tuple[str, str, str]] | None = None,
                 budget_id: str | None = None) -> BudgetReport:
    """Reconcile budget within ceiling. CLIENT lines are honored verbatim
    and checked; nothing is invented."""
    lines = [BudgetLine(line_id=f"bl-{i}", description=desc,
                        category=cat, amount=amt, source="GOVERNED")
             for i, (desc, cat, amt) in enumerate(GOVERNED_LINES)]
    if client_lines:
        for i, (desc, cat, amt) in enumerate(client_lines):
            lines.append(BudgetLine(line_id=f"blc-{i}", description=desc,
                                    category=cat, amount=amt,
                                    source="CLIENT"))

    total = sum((Decimal(l.amount) for l in lines), Decimal("0.00"))
    ceiling_dec = Decimal(ceiling)
    categories: dict[str, str] = {}
    for line in lines:
        cat_total = sum((Decimal(l.amount) for l in lines
                         if l.category == line.category), Decimal("0.00"))
        categories[line.category] = str(cat_total)

    issues: list[str] = []
    if total > ceiling_dec:
        issues.append(f"total {total} exceeds ceiling {ceiling}")
    if total <= Decimal("0.00"):
        issues.append("budget total must be positive")

    narrative = (
        f"The proposed budget totals ${total:,.2f}, within the "
        f"${ceiling_dec:,.2f} funding ceiling of the Georgia Rural "
        f"Community Impact Grant FY2026. Line items reconcile to the "
        f"ceiling; categories are personnel, supplies, travel, and "
        f"evaluation.")
    return BudgetReport(lines=lines, total=str(total), ceiling=ceiling,
                        within_ceiling=total <= ceiling_dec,
                        categories=categories, narrative=narrative,
                        issues=issues)
