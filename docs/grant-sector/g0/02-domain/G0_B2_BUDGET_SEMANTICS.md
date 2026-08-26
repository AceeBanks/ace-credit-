# G0 Book 2 — Chapter C12: Budget & Financial Semantic Model

## Decision

Narrative and numbers share a structured domain — the LLM never improvises
arithmetic on canonical money. Totals, ratios and ceilings are produced only by
the deterministic functions in `prototype/g0/domain/budget.py`.

Machine-readable source of truth: `config/g0/domain/budget_policy.yaml`.

## Concepts

`Budget`, `BudgetVersion`, `BudgetLine`, `BudgetCategory`, `FundingSource`,
`MatchContribution`, `InKindContribution`, `CostShare`, `Period`, `Assumption`.

## Monetary rules (all enforced)

| Rule | Enforcement |
|---|---|
| decimal/fixed-point only | `validate_amounts` rejects non-Decimal amounts |
| explicit currency | `currency_mismatches` rejects line ≠ budget currency |
| explicit period | Budget carries a `Period` |
| deterministic totals | `reconcile` / `total_by_category` compute, never hand-write |
| amount lineage | lines carry `assumption_ref`; budget carries `assumptions` |

## Narrative linkage

Budget lines may link to project activity, outcome, proposal section,
requirement, evidence/assumption. `narrative_amount_mismatch` detects a
narrative figure that differs from the computed budget total.

## Ceiling & match

- `check_ceiling`: requested amount ≤ applicable ceiling where a rule exists
  (no rule → no constraint).
- `match_total` / `match_ratio`: deterministic cash + in-kind FMV totals.

## Tests (11 in `test_budget.py`)

- totals reconcile (computed, deterministic)
- requested amount within applicable ceiling; over-ceiling flagged; no-rule no-op
- match/cost-share calculation deterministic
- narrative amount mismatch detected
- currency mismatch rejected
- float money rejected (Decimal-only)
- explicit period on budget
- validator: missing monetary rule, currency-mismatch-not-rejected fail closed

Run: `python -m pytest tests/g0/book2/test_budget.py -q` — **11 passed**.
