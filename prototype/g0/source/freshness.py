"""G0-B3-C9 — Freshness constitution.

Defines when data is current enough for its intended use. Same data age can be
FRESH for one fact class and HARD_STALE for another. Vintage-based facts
(annual statistics, IRS filings) are not merely age-driven; they stay valid as
long as the latest official vintage remains the applicable one. Hard-stale
critical facts block submission-ready state.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class FreshnessState(Enum):
    FRESH = "FRESH"
    SOFT_STALE = "SOFT_STALE"
    HARD_STALE = "HARD_STALE"
    UNKNOWN_FRESHNESS = "UNKNOWN_FRESHNESS"
    HISTORICAL_FIXED = "HISTORICAL_FIXED"


@dataclass(frozen=True)
class FreshnessPolicy:
    fact_class: str
    source_class: str
    soft_stale_after_days: int | None
    hard_stale_after_days: int | None
    refresh_on_access: bool
    refresh_on_deadline_window: str | None
    latest_vintage_rule: str | None
    critical_use_block_on_hard_stale: bool


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def classify(policy: FreshnessPolicy, retrieved_at: str | None,
             age_days: float | None = None, now: datetime | None = None,
             retrieved_ts: datetime | None = None,
             latest_vintage_current: bool = True) -> FreshnessState:
    """Classify freshness for a captured fact under a policy.

    Order (fail-closed):
      1. UNKNOWN_FRESHNESS when we cannot tell the age and no vintage rule.
      2. HISTORICAL_FIXED / vintage rules resolve before age windows.
      3. HARD_STALE when age > hard window.
      4. SOFT_STALE when age > soft window.
      5. else FRESH.
    """
    # Vintage-based facts: not stale merely because old, if the latest official
    # vintage is still the applicable one.
    if policy.latest_vintage_rule is not None:
        if policy.latest_vintage_rule == "historical_fixed_absent_correction":
            from prototype.g0.source.freshness import FreshnessState as _F
            return _F.HISTORICAL_FIXED if latest_vintage_current else _F.SOFT_STALE
        if policy.latest_vintage_rule in ("latest_official_vintage",
                                          "dataset_vintage_reference_period"):
            if latest_vintage_current:
                return FreshnessState.FRESH
            return FreshnessState.HARD_STALE

    if age_days is None:
        return FreshnessState.UNKNOWN_FRESHNESS

    if policy.hard_stale_after_days is not None and age_days > policy.hard_stale_after_days:
        return FreshnessState.HARD_STALE
    if policy.soft_stale_after_days is not None and age_days > policy.soft_stale_after_days:
        return FreshnessState.SOFT_STALE
    return FreshnessState.FRESH


def hard_stale_blocks_critical(policy: FreshnessPolicy, state: FreshnessState) -> bool:
    return policy.critical_use_block_on_hard_stale and state == FreshnessState.HARD_STALE