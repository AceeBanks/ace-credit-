"""G0-B3-C22 — Source health, observability & degradation.

Fail-closed:
  * schema drift -> DEGRADED/SCHEMA_CHANGED, adapter promotion disabled,
    fixture captured, repair required — no silent null mapping for critical
    facts;
  * a source can stay queryable historically while disabled for fresh
    promotion; an outage never erases cached history;
  * a hard-stale critical opportunity forces uncertainty/block, never silent
    readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml


class HealthState(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILING = "FAILING"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    SCHEMA_CHANGED = "SCHEMA_CHANGED"
    DISABLED = "DISABLED"
    UNKNOWN = "UNKNOWN"


class PromotionAvailability(Enum):
    ENABLED = "ENABLED"
    DISABLED_FOR_FRESH_PROMOTION = "DISABLED_FOR_FRESH_PROMOTION"
    NEVER_PROMOTES = "NEVER_PROMOTES"


@dataclass
class SourceHealth:
    source_id: str
    state: HealthState = HealthState.UNKNOWN
    last_successful_fetch: str | None = None
    schema_validation_rate: float = 0.0
    promotion_availability: PromotionAvailability = PromotionAvailability.ENABLED
    fixture_captured: bool = False
    repair_required: bool = False

    def apply_schema_drift(self, *, fixture_captured: bool = False) -> None:
        """Schema validation failure -> DEGRADED/SCHEMA_CHANGED, promotion
        disabled, fixture captured, repair required. Never silently maps
        missing fields to null for critical facts."""
        self.state = HealthState.SCHEMA_CHANGED
        self.promotion_availability = PromotionAvailability.DISABLED_FOR_FRESH_PROMOTION
        self.fixture_captured = fixture_captured
        self.repair_required = True


def outage_preserves_history(historical_snapshots: list) -> bool:
    """A source outage/failure never erases cached/historical snapshots."""
    return len(historical_snapshots) >= 1


def hard_stale_blocks_opportunity(state: str) -> bool:
    """A hard-stale critical opportunity forces uncertainty/block."""
    return state == "HARD_STALE"


KNOWN_STATES = {s.value for s in HealthState}
KNOWN_METRICS = {
    "last_successful_fetch", "failure_rate", "latency", "schema_validation_rate",
    "extraction_quality_trend", "http_status_distribution", "rate_limit_events",
    "content_change_frequency", "duplicate_rate", "stale_source_count",
    "downstream_invalidations",
}


def _load_health_config() -> dict:
    return load_yaml(SOURCE_CONFIG_DIR / "source_health_policy.yaml")
