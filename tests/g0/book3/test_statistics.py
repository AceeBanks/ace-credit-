"""B3.C15 tests — StatisticObservation Data Policy.

Fail-closed:
  * every required dimension must be present (missing refs rejected);
  * geography mismatch (county vs city) is FLAGGED, never silently crossed;
  * reference period is mandatory;
  * a percentage without denominator context is rejected;
  * derived statistics replay deterministically from parent observations
    (supported formulas only — no arbitrary expression evaluation);
  * an old dataset vintage is stale under the latest-vintage policy.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_statistics import (
    KNOWN_ESTIMATE,
    KNOWN_GEO,
    KNOWN_POP,
    KNOWN_QUALITY,
    validate,
    validate_row,
)
from prototype.g0.source.statistics import (
    REQUIRED_DIMENSIONS,
    QualityState,
    StatObservation,
    derived_stat_replays,
    vintage_policy_fresh,
)

CFG = SOURCE_CONFIG_DIR / "statistic_policy.yaml"


def _obs(**overrides) -> StatObservation:
    base = dict(
        metric_code="pov_rate", metric_label="Poverty rate", value=14.8,
        unit="percent", geography_type="county", geography_id="13121",
        geography_label="Fulton County, GA", population_scope="all_persons",
        reference_period_start="2023-01-01", reference_period_end="2023-12-31",
        dataset_name="Census ACS 5-Year", dataset_vintage="2023",
        estimate_type="percent_estimate", margin_of_error=0.9,
        confidence_interval=[13.9, 15.7],
        methodology_ref="census-acs-2023-5yr", source_snapshot_ref="snap_1",
        quality_state=QualityState.VERIFIED,
    )
    base.update(overrides)
    return StatObservation(**base)


def test_validator_live_config_passes():
    ok, report = validate(CFG)
    assert ok, report["errors"]
    assert report["fixture_count"] == 2


def test_config_dimensions_match_prototype():
    cfg = load_yaml(CFG)
    assert set(cfg["required_dimensions"]) == set(REQUIRED_DIMENSIONS)
    assert set(cfg["geography_types"]) == KNOWN_GEO
    assert set(cfg["estimate_types"]) == KNOWN_ESTIMATE
    assert set(cfg["population_scopes"]) == KNOWN_POP
    assert set(cfg["quality_states"]) == KNOWN_QUALITY


def test_geography_mismatch_flagged():
    ok, errors = _obs().check(geography_match=False)
    assert not ok
    assert any("geography mismatch" in e for e in errors)


def test_missing_reference_period_rejected():
    obs = _obs(reference_period_start=None, reference_period_end=None)
    ok, errors = obs.check()
    assert not ok
    assert any("reference period" in e for e in errors)


def test_percentage_without_denominator_rejected():
    obs = _obs(population_scope=None)
    ok, errors = obs.check()
    assert not ok
    assert any("denominator context" in e for e in errors)


def test_missing_source_snapshot_ref_rejected():
    obs = _obs(source_snapshot_ref=None)
    assert any("source_snapshot_ref" in e for e in obs.required_dimension_errors())


def test_percent_estimate_without_moe_flagged_by_validator():
    errors: list[str] = []
    row = {
        "metric_code": "m1", "value": 10.0, "unit": "percent",
        "geography_type": "county", "geography_id": "1", "geography_label": "G",
        "population_scope": "all_persons", "reference_period_start": "2023-01-01",
        "reference_period_end": "2023-12-31", "dataset_name": "D",
        "dataset_vintage": "2023", "estimate_type": "percent_estimate",
        "margin_of_error": None, "confidence_interval": None,
        "methodology_ref": None, "source_snapshot_ref": None,
        "quality_state": "CANDIDATE",
    }
    validate_row(row, errors)
    assert any("margin_of_error" in e for e in errors)


def test_derived_stat_replays_from_parents():
    assert derived_stat_replays({"a": 100.0, "b": 200.0, "c": 300.0}, "sum", 600.0)
    assert derived_stat_replays({"a": 10.0, "b": 20.0, "c": 30.0}, "mean", 20.0)
    assert derived_stat_replays({"value": 5.0, "denominator": 100.0}, "rate", 0.05)


def test_unsupported_formula_does_not_replay():
    # fail-closed: an arbitrary expression is NOT a supported derived formula
    assert derived_stat_replays({"a": 100.0}, "__import__('os').system('x')", 0.0) is False
    assert derived_stat_replays({"a": 100.0}, "a + 100", 200.0) is False


def test_zero_denominator_rate_fails():
    assert derived_stat_replays({"value": 1.0, "denominator": 0.0}, "rate", 1.0) is False


def test_old_vintage_stale_under_latest_vintage_policy():
    # ACS 2019 is stale once the 2023 vintage is the latest applicable release
    assert vintage_policy_fresh("2019", "2023") is False
    assert vintage_policy_fresh("2023", "2023") is True


def test_state_stat_not_represented_as_county():
    state = _obs(geography_type="state", geography_id="13",
                 geography_label="Georgia", population_scope="all_persons")
    # a statewide observation claiming Fulton County dataset geography fails
    ok, errors = state.check(geography_match=False)
    assert not ok
    assert any("geography mismatch" in e for e in errors)
