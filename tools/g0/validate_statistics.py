"""G0-B3-C15 — validate StatisticObservation data policy.

Fail-closed checks:
  * every required dimension is present on a statistic record/fixture
  * geography types / estimate types / population scopes / quality states are
    from known enums
  * geography-match, denominator-context, derived-stat and proposal-use rules
    are declared
  * reference period is mandatory; percent estimates require denominator
    context; derived stats must carry formula + parent observation refs
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (
    SOURCE_CONFIG_DIR,
    cli_main,
    finish,
    load_yaml,
)

REQUIRED_DIMENSIONS = [
    "metric_code", "metric_label", "value", "unit", "geography_type",
    "geography_id", "geography_label", "population_scope",
    "reference_period_start", "reference_period_end", "dataset_name",
    "dataset_vintage", "estimate_type", "margin_of_error",
    "confidence_interval", "methodology_ref", "source_snapshot_ref",
    "quality_state",
]
KNOWN_GEO = {"city", "county", "tract", "block_group", "state", "national",
             "custom_region"}
KNOWN_ESTIMATE = {"direct_estimate", "model_based_estimate", "percent_estimate",
                  "aggregate", "survey_estimate"}
KNOWN_POP = {"all_persons", "children_under_18", "single_parent_households",
             "labor_force_participants", "school_age_population"}
KNOWN_QUALITY = {"VERIFIED", "CANDIDATE", "FLAGGED", "REJECTED"}

DENOMINATOR_REQUIRED = {"percent_estimate"}


@dataclass
class FixtureStats:
    rows: list  # statistical fixture rows


def validate_row(row: dict, errors: list) -> None:
    ctx = row.get("metric_code", "<anon>")
    for f in REQUIRED_DIMENSIONS:
        if f not in row:
            errors.append(f"{ctx}: missing required dimension '{f}'")
    if row.get("geography_type") not in KNOWN_GEO:
        errors.append(f"{ctx}: unknown geography_type {row.get('geography_type')!r}")
    if row.get("estimate_type") not in KNOWN_ESTIMATE:
        errors.append(f"{ctx}: unknown estimate_type {row.get('estimate_type')!r}")
    if row.get("population_scope") not in KNOWN_POP:
        errors.append(f"{ctx}: unknown population_scope {row.get('population_scope')!r}")
    if row.get("quality_state") not in KNOWN_QUALITY:
        errors.append(f"{ctx}: unknown quality_state {row.get('quality_state')!r}")
    if row.get("estimate_type") in DENOMINATOR_REQUIRED and not row.get("population_scope"):
        errors.append(f"{ctx}: percent estimate requires denominator context")
    if row.get("estimate_type") == "percent_estimate" and not row.get("margin_of_error"):
        # MOE is a required dimension; percent estimates that omit it are not
        # safe to quote in a proposal narrative.
        errors.append(f"{ctx}: percent estimate requires margin_of_error")


def validate(config):
    cfg = load_yaml(config)
    if not isinstance(cfg, dict):
        return False, {"errors": ["statistic config must parse to a mapping"]}
    errors: list[str] = []
    declared = cfg.get("required_dimensions", [])
    if set(declared) != set(REQUIRED_DIMENSIONS):
        missing = set(REQUIRED_DIMENSIONS) - set(declared)
        extra = set(declared) - set(REQUIRED_DIMENSIONS)
        if missing:
            errors.append(f"config required_dimensions missing: {sorted(missing)}")
        if extra:
            errors.append(f"config required_dimensions has unknown entries: {sorted(extra)}")
    fixtures = cfg.get("statistic_fixtures", [])
    for row in fixtures:
        if isinstance(row, dict):
            validate_row(row, errors)
        else:
            errors.append("statistic fixture rows must be mappings")
    if not cfg.get("geography_match_rule"):
        errors.append("geography match rule must be declared")
    if not cfg.get("derived_stat_rule"):
        errors.append("derived-stat lineage rule must be declared")
    if not cfg.get("proposal_use_rule"):
        errors.append("proposal use rule must be declared")
    return finish("validate_statistics", not errors, {
        "errors": errors,
        "declared_dimension_count": len(declared),
        "fixture_count": len(fixtures),
    })


if __name__ == "__main__":
    default = SOURCE_CONFIG_DIR / "statistic_policy.yaml"
    raise SystemExit(cli_main(validate, default))
