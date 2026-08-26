"""G0-B3-C25-C26 — validate the adversarial scenario + invariant catalog.

Fail-closed checks:
  * all 25 adversarial scenarios A1..A25 are present with non-empty
    expectations;
  * all 22 mandatory invariants are declared and come from the known set;
  * all 6 property tests are declared and come from the known set.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    SOURCE_CONFIG_DIR,
    ValidationFailure,
    emit,
    load_yaml,
)

KNOWN_INVARIANTS = {
    "every_enabled_source_exists_in_registry",
    "every_material_fact_points_to_snapshot",
    "every_raw_capture_has_integrity_identity",
    "source_snapshots_immutable",
    "parsing_versioned_separately_from_capture",
    "promotion_policy_independent_of_extraction_engine",
    "search_snippets_cannot_promote_critical_claims",
    "source_precedence_fact_class_specific",
    "freshness_fact_source_semantic_not_generic_age",
    "equal_authority_critical_conflicts_block",
    "material_changes_produce_change_events",
    "p0_changes_invalidate_dependents",
    "external_identifiers_require_verification_state",
    "statistics_preserve_geography_population_time_vintage",
    "web_content_has_no_policy_authority",
    "historical_decisions_replayable_against_old_snapshots",
    "source_health_failure_cannot_fake_freshness",
    "retention_deletion_propagates_to_replay_evidence_status",
    "georgia_federal_sources_normalize_to_book2_ontology",
    "private_crawled_sources_remain_governed_registered",
    "d0_packet_reconstructs_without_agent_memory",
    "d0_draft_regenerable_with_bounded_variance",
}
KNOWN_PROPERTY_TESTS = {
    "raw_content_hashing_idempotent",
    "precedence_resolver_deterministic",
    "freshness_resolver_deterministic",
    "dependency_invalidation_deterministic",
    "provenance_graph_no_orphan_material_facts",
    "replay_preserves_source_identities",
}

REQUIRED_SCENARIO_IDS = {f"A{i}" for i in range(1, 26)}


def validate(cfg: dict, errors: list) -> None:
    scenarios = cfg.get("adversarial_scenarios", [])
    ids = {s.get("id") for s in scenarios}
    missing = REQUIRED_SCENARIO_IDS - ids
    if missing:
        errors.append(f"adversarial scenarios missing: {sorted(missing)}")
    extra = ids - REQUIRED_SCENARIO_IDS
    if extra:
        errors.append(f"unknown adversarial scenario ids: {sorted(extra)}")
    for s in scenarios:
        if not (s.get("id") and s.get("name") and s.get("expectation")):
            errors.append(f"scenario {s.get('id')!r} must carry id/name/expectation")
    invariants = set(cfg.get("mandatory_invariants", []))
    unknown_i = invariants - KNOWN_INVARIANTS
    if unknown_i:
        errors.append(f"unknown mandatory invariants: {sorted(unknown_i)}")
    missing_i = KNOWN_INVARIANTS - invariants
    if missing_i:
        errors.append(f"mandatory invariants missing: {sorted(missing_i)}")
    props = set(cfg.get("property_tests", []))
    unknown_p = props - KNOWN_PROPERTY_TESTS
    if unknown_p:
        errors.append(f"unknown property tests: {sorted(unknown_p)}")
    missing_p = KNOWN_PROPERTY_TESTS - props
    if missing_p:
        errors.append(f"property tests missing: {sorted(missing_p)}")


def main() -> int:
    errors: list[str] = []
    try:
        cfg = load_yaml(SOURCE_CONFIG_DIR / "adversarial_data.yaml")
        validate(cfg, errors)
    except ValidationFailure as exc:
        errors.append(str(exc))
    ok = not errors
    return emit({
        "validator": "validate_adversarial",
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "scenario_count": len(cfg.get("adversarial_scenarios", [])),
        "invariant_count": len(cfg.get("mandatory_invariants", [])),
        "property_test_count": len(cfg.get("property_tests", [])),
    })


if __name__ == "__main__":
    sys.exit(main())
