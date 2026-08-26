"""B3.C22 tests — Source Health, Observability & Degradation.

Fail-closed:
  * a schema-change fixture triggers SCHEMA_CHANGED / promotion disabled /
    repair required — no silent null mapping for critical facts;
  * a source outage never erases cached/historical snapshots;
  * a hard-stale critical opportunity forces uncertainty/block.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_health_d0 import (
    KNOWN_HEALTH_STATES,
    KNOWN_METRICS,
    validate_health,
)
from prototype.g0.source.health import (
    HealthState,
    PromotionAvailability,
    SourceHealth,
    hard_stale_blocks_opportunity,
    outage_preserves_history,
)

CFG = SOURCE_CONFIG_DIR / "source_health_policy.yaml"


def test_validator_live_config_passes():
    errors: list[str] = []
    validate_health(load_yaml(CFG), errors)
    assert errors == []


def test_health_states_and_metrics_match_config():
    cfg = load_yaml(CFG)
    assert set(cfg["health_states"]) == KNOWN_HEALTH_STATES
    assert set(cfg["metrics"]) == KNOWN_METRICS


def test_schema_drift_triggers_degraded_and_promotion_disabled():
    h = SourceHealth(source_id="src_grants_gov", state=HealthState.HEALTHY)
    h.apply_schema_drift(fixture_captured=True)
    assert h.state is HealthState.SCHEMA_CHANGED
    assert (h.promotion_availability
            is PromotionAvailability.DISABLED_FOR_FRESH_PROMOTION)
    assert h.fixture_captured is True
    assert h.repair_required is True


def test_schema_drift_never_silently_nulls_critical_facts():
    # The drift path has NO branch that maps missing fields to null and
    # continues: repair is always required and promotion is always disabled.
    h = SourceHealth(source_id="src_census_acs")
    h.apply_schema_drift()
    assert h.repair_required is True
    assert (h.promotion_availability
            is PromotionAvailability.DISABLED_FOR_FRESH_PROMOTION)


def test_outage_does_not_erase_history():
    history = ["snap_1", "snap_2", "snap_3"]
    assert outage_preserves_history(history) is True
    # even after an outage, historical snapshots remain queryable
    assert len(history) == 3


def test_hard_stale_critical_opportunity_blocks():
    assert hard_stale_blocks_opportunity("HARD_STALE") is True
    assert hard_stale_blocks_opportunity("FRESH") is False


def test_disabled_source_still_queryable_historically():
    h = SourceHealth(source_id="src_ga_opb")
    h.apply_schema_drift()
    # promotion availability is disabled, but history is untouched
    assert h.promotion_availability != PromotionAvailability.ENABLED
    assert outage_preserves_history(["snap_ga_old"]) is True
