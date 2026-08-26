"""G0-B3-C15 — StatisticObservation data policy.

Makes quantitative community/impact evidence safe for grant writing. Enforces
geography (no silent level crossing), population (denominator) semantics, time
(reference period vs release vintage vs retrieval time), and derived-stat
lineage. A statistic claimed for one geography that does not match the
dataset's geography is FLAGGED.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class QualityState(Enum):
    VERIFIED = "VERIFIED"
    CANDIDATE = "CANDIDATE"
    FLAGGED = "FLAGGED"
    REJECTED = "REJECTED"


# Required dimensions (mirrors statistic_policy.yaml).
REQUIRED_DIMENSIONS = [
    "metric_code", "metric_label", "value", "unit", "geography_type",
    "geography_id", "geography_label", "population_scope",
    "reference_period_start", "reference_period_end", "dataset_name",
    "dataset_vintage", "estimate_type", "margin_of_error",
    "confidence_interval", "methodology_ref", "source_snapshot_ref",
    "quality_state",
]
# Dimensions that may be absent only for specific estimate types.
DENOMINATOR_REQUIRED_ESTIMATE_TYPES = {"percent_estimate"}

KNOWN_GEO = {"city", "county", "tract", "block_group", "state", "national",
             "custom_region"}
KNOWN_ESTIMATE = {"direct_estimate", "model_based_estimate", "percent_estimate",
                  "aggregate", "survey_estimate"}


@dataclass
class StatObservation:
    metric_code: str
    value: float
    unit: str
    geography_type: str  # city | county | tract | block_group | state | national
    geography_id: str
    geography_label: str
    population_scope: str
    reference_period_start: str
    reference_period_end: str
    dataset_name: str
    dataset_vintage: str
    estimate_type: str
    source_snapshot_ref: str
    margin_of_error: float | None = None
    confidence_interval: list | None = None
    methodology_ref: str | None = None
    quality_state: QualityState = QualityState.CANDIDATE
    metric_label: str = ""
    # for derived statistics
    formula: str | None = None
    parent_observation_refs: list[str] = field(default_factory=list)

    def required_dimension_errors(self) -> list[str]:
        """Fail-closed: every required dimension must be present (not None)."""
        errors: list[str] = []
        for dim in REQUIRED_DIMENSIONS:
            if getattr(self, dim, None) in (None, ""):
                errors.append(f"{self.metric_code}: missing required dimension "
                              f"'{dim}'")
        return errors

    def check(self, geography_match: bool = True) -> tuple[bool, list[str]]:
        errors = self.required_dimension_errors()
        if not self.reference_period_start or not self.reference_period_end:
            errors.append("missing reference period")
        if (self.estimate_type in DENOMINATOR_REQUIRED_ESTIMATE_TYPES
                and not self.population_scope):
            errors.append("percentage without denominator context")
        if self.estimate_type not in KNOWN_ESTIMATE:
            errors.append(f"unknown estimate_type {self.estimate_type!r}")
        if self.geography_type not in KNOWN_GEO:
            errors.append(f"unknown geography_type {self.geography_type!r}")
        if not geography_match:
            errors.append(
                f"geography mismatch: statistic geography ({self.geography_label}) "
                f"does not match dataset geography")
        return (not errors), errors


def derived_stat_replays(parent_values: dict[str, float], formula: str,
                         expected: float) -> bool:
    """Deterministic replay of a derived statistic from its parent observations.

    Supported formulas (fail-closed — anything else returns False):
      * "sum"            — sum of parent values
      * "mean"           — arithmetic mean of parent values
      * "rate"           — parent_values["value"] / parent_values["denominator"]
    No evaluation of arbitrary expressions: derived stats must carry an explicit,
    supported formula so the derivation replays from the recorded parents.
    """
    try:
        if formula == "sum":
            result = sum(parent_values.values())
        elif formula == "mean":
            result = sum(parent_values.values()) / len(parent_values)
        elif formula == "rate":
            denom = parent_values["denominator"]
            if denom == 0:
                return False
            result = parent_values["value"] / denom
        else:
            return False
        return abs(result - expected) < 1e-9
    except (KeyError, TypeError, ZeroDivisionError, ValueError):
        return False


def vintage_policy_fresh(dataset_vintage: str, latest_vintage: str) -> bool:
    """Latest-vintage policy: a statistic is usable only if its dataset vintage
    is the latest applicable release (or explicitly retained). An old vintage
    (e.g. ACS 2019 when 2023 is released) is stale even if the number of days
    since retrieval is small."""
    return dataset_vintage >= latest_vintage
