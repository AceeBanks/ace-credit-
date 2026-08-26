"""B3.C27 — Book 3 Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book4 =
        data_constitution_complete
        AND enabled_sources_registered == 1.0
        AND critical_facts_with_snapshot_lineage == 1.0
        AND snapshot_immutability_tests_pass
        AND capture_replay_tests_pass
        AND extraction_lineage_tests_pass
        AND precedence_tests_pass
        AND freshness_tests_pass
        AND promotion_tests_pass
        AND conflict_tests_pass
        AND material_change_tests_pass
        AND dependency_invalidation_tests_pass
        AND identifier_verification_tests_pass
        AND statistic_semantics_tests_pass
        AND source_security_tests_pass
        AND retention_tests_pass
        AND provenance_chain_tests_pass
        AND federal_fixture_tests_pass
        AND georgia_fixture_tests_pass
        AND private_source_fixture_tests_pass
        AND d0_data_packet_ready
        AND d0_shadow_draft_allowed
        AND adversarial_p0_pass is True
        AND p0_open == 0

Usage:
    python tools/g0/build_book3_reality_lock.py [--no-tests] [--out PATH]

`--no-tests` skips the pytest run (used by unit tests that inject fixtures);
the emitted lock then reports adversarial_p0_pass as null rather than a claim.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    RATIFICATION_CONFIG_DIR,
    SOURCE_CONFIG_DIR,
    load_yaml,
)
from tools.g0.validate_adversarial import validate as validate_adversarial_cfg  # noqa: E402
from tools.g0.validate_capture_extraction import (  # noqa: E402
    validate_capture,
    validate_extraction,
)
from tools.g0.validate_data_constitution import validate as validate_constitution  # noqa: E402
from tools.g0.validate_dependency_identifier import (  # noqa: E402
    validate_dependency,
    validate_identifier,
)
from tools.g0.validate_health_d0 import validate_d0 as validate_d0_cfg  # noqa: E402
from tools.g0.validate_health_d0 import validate_health as validate_health_cfg  # noqa: E402
from tools.g0.validate_onboarding_snapshot import (  # noqa: E402
    validate_onboarding,
    validate_snapshot_rows,
)
from tools.g0.validate_precedence_freshness import (  # noqa: E402
    validate_freshness,
    validate_precedence,
)
from tools.g0.validate_private_source_security import (  # noqa: E402
    validate_private,
    validate_security,
)
from tools.g0.validate_promotion_conflict import (  # noqa: E402
    validate_conflict,
    validate_promotion,
    validate_source_change,
)
from tools.g0.validate_retention_provenance import (  # noqa: E402
    validate_provenance,
    validate_retention,
)
from tools.g0.validate_source_profiles import (  # noqa: E402
    validate_federal,
    validate_georgia,
)
from tools.g0.validate_source_registry import (  # noqa: E402
    validate_classes,
    validate_registry,
)
from tools.g0.validate_statistics import validate as validate_statistics_cfg  # noqa: E402

COMMITTED_LOCK_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "00-ratification"
    / "G0_B3_REALITY_LOCK.json"
)

STEMS = (
    "data_constitution.yaml", "source_classes.yaml", "source_registry.yaml",
    "onboarding_snapshot.yaml", "capture_extraction.yaml",
    "precedence_matrix.yaml", "freshness_policy.yaml", "promotion_conflict.yaml",
    "dependency_identifier.yaml", "statistic_policy.yaml",
    "federal_profiles.yaml", "georgia_profiles.yaml",
    "private_source_policy.yaml", "source_security_policy.yaml",
    "retention_policy.yaml", "provenance_chain.yaml",
    "source_health_policy.yaml", "d0_data_packet.yaml", "adversarial_data.yaml",
)

# Critical fact classes whose lineage the lock must prove (from the promotion
# model) — each must appear in the fact-class-specific precedence matrix.
CRITICAL_FACT_CLASSES = {
    "opportunity_deadline", "opportunity_eligibility",
    "opportunity_award_ceiling", "opportunity_required_attachments",
    "legal_organization_name", "tax_exempt_status",
    "opportunity_submission_instructions",
}


def _run_book3_tests() -> dict:
    # Recursion guard: the lock-freshness test itself invokes this builder; the
    # inner pytest run must skip it or we recurse forever.
    env = {**os.environ, "G0_SKIP_LOCK_FRESHNESS": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book3", "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=600, env=env,
    )
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    match = re.search(r"(\d+) passed", tail[0])
    failed = re.search(r"(\d+) failed", tail[0])
    return {
        "exit_code": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "failed": int(failed.group(1)) if failed else (1 if proc.returncode else 0),
        "summary": tail[0],
        "scope": "tests/g0/book3 excluding G0_B3_REALITY_LOCK.json freshness self-test",
    }


def _critical_facts_with_lineage(configs: dict) -> float:
    matrix = configs["precedence_matrix"].get("precedence_matrix", {})
    covered = [c for c in CRITICAL_FACT_CLASSES if c in matrix]
    return round(len(covered) / len(CRITICAL_FACT_CLASSES), 6) if CRITICAL_FACT_CLASSES else 0.0


def _enabled_sources_registered(configs: dict) -> float:
    """Fraction of ENABLED sources that are fully governed: every enabled
    source must carry an adapter version and the four policy refs. A source
    that is enabled but ungoverned drops the ratio below 1.0."""
    sources = configs["source_registry"].get("sources", [])
    enabled = [s for s in sources if s.get("enabled") is True]
    if not enabled:
        return 0.0
    ok = sum(1 for s in enabled
             if (s.get("adapter_version")
                 and s.get("terms_policy_ref") and s.get("robots_policy_ref")
                 and s.get("rate_limit_policy_ref") and s.get("health_policy_ref")))
    return round(ok / len(enabled), 6)


def compute_lock(configs: dict, test_results: dict | None = None,
                 ledger: dict | None = None) -> dict:
    """Compute the Reality Lock from loaded configs (+ optional pytest results).

    `configs` maps config-stem -> parsed document. `test_results` None means
    tests were not executed (reported as null and readiness is blocked).
    """
    def _ok(check_result: tuple[bool, dict]) -> bool:
        return check_result[0]

    def errors_of(fn, data: dict) -> bool:
        errors: list[str] = []
        fn(data, errors)
        return not errors

    class_ids = {c["class_id"] for c in configs["source_classes"].get("classes", [])}

    predicates = {
        "data_constitution_complete": _ok(validate_constitution(configs["data_constitution"])),
        "enabled_sources_registered": _enabled_sources_registered(configs),
        "critical_facts_with_snapshot_lineage": _critical_facts_with_lineage(configs),
        "snapshot_immutability_tests_pass": errors_of(
            lambda d, e: (validate_onboarding(d.get("source_statuses", {}),
                                              d.get("onboarding_packets", {}), e),
                          validate_snapshot_rows(d.get("snapshot_fixtures", []), e)),
            configs["onboarding_snapshot"]),
        "capture_replay_tests_pass": errors_of(validate_capture,
                                               configs["capture_extraction"]),
        "extraction_lineage_tests_pass": errors_of(validate_extraction,
                                                   configs["capture_extraction"]),
        "precedence_tests_pass": errors_of(validate_precedence,
                                           configs["precedence_matrix"]),
        "freshness_tests_pass": errors_of(validate_freshness,
                                          configs["freshness_policy"]),
        "promotion_tests_pass": errors_of(validate_promotion,
                                          configs["promotion_conflict"]),
        "conflict_tests_pass": errors_of(validate_conflict,
                                         configs["promotion_conflict"]),
        "material_change_tests_pass": errors_of(validate_source_change,
                                                configs["promotion_conflict"]),
        "dependency_invalidation_tests_pass": errors_of(
            validate_dependency, configs["dependency_identifier"]),
        "identifier_verification_tests_pass": errors_of(
            validate_identifier, configs["dependency_identifier"]),
        "statistic_semantics_tests_pass": _ok(
            validate_statistics_cfg(SOURCE_CONFIG_DIR / "statistic_policy.yaml")),
        "source_security_tests_pass": errors_of(validate_security,
                                                configs["source_security_policy"]),
        "retention_tests_pass": errors_of(validate_retention,
                                          configs["retention_policy"]),
        "provenance_chain_tests_pass": errors_of(validate_provenance,
                                                 configs["provenance_chain"]),
        "federal_fixture_tests_pass": errors_of(validate_federal,
                                                configs["federal_profiles"]),
        "georgia_fixture_tests_pass": errors_of(validate_georgia,
                                                configs["georgia_profiles"]),
        "private_source_fixture_tests_pass": errors_of(validate_private,
                                                       configs["private_source_policy"]),
        "d0_data_packet_ready": errors_of(validate_d0_cfg, configs["d0_data_packet"]),
    }

    # registry validity + adversarial catalog also gate readiness
    registry_ok = _ok(validate_registry(configs["source_registry"], class_ids))
    adversarial_ok = errors_of(validate_adversarial_cfg, configs["adversarial_data"])

    if test_results is None:
        predicates["adversarial_p0_pass"] = None
    else:
        predicates["adversarial_p0_pass"] = (
            test_results["exit_code"] == 0 and test_results["failed"] == 0
        )

    # p0_open from the shared contradiction ledger; injectable for defect tests
    if not isinstance(ledger, dict):
        ledger = load_yaml(RATIFICATION_CONFIG_DIR / "contradiction_ledger.yaml")
    p0_open = len([c for c in ledger.get("contradictions", [])
                   if c.get("severity") == "P0" and c.get("status") != "RESOLVED"])

    d0_shadow_draft_allowed = (
        predicates["d0_data_packet_ready"]
        and predicates.get("adversarial_p0_pass") is True
        and p0_open == 0
    )
    predicates["d0_shadow_draft_allowed"] = d0_shadow_draft_allowed

    boolean_gates = [v for k, v in predicates.items()
                     if k not in ("enabled_sources_registered",
                                  "critical_facts_with_snapshot_lineage")]
    ready = (
        registry_ok
        and adversarial_ok
        and all(v is True for v in boolean_gates)
        and predicates["enabled_sources_registered"] >= 1.0
        and predicates["critical_facts_with_snapshot_lineage"] >= 1.0
        and predicates["adversarial_p0_pass"] is True
        and p0_open == 0
    )

    enabled_count = len([s for s in configs["source_registry"].get("sources", [])
                         if s.get("enabled") is True])
    return {
        "book": "G0-B3",
        "status": "PASS" if ready else "FAIL",
        **predicates,
        "p0_open": p0_open,
        "ready_for_d0": ready,
        "ready_for_book4": ready,
        "evidence": {
            "test_results": test_results,
            "config_count": len(STEMS),
            "enabled_source_count": enabled_count,
            "critical_fact_class_count": len(CRITICAL_FACT_CLASSES),
        },
    }


def build_live_lock(run_tests: bool = True) -> dict:
    configs = {stem.removesuffix(".yaml"): load_yaml(SOURCE_CONFIG_DIR / stem)
               for stem in STEMS}
    test_results = _run_book3_tests() if run_tests else None
    return compute_lock(configs, test_results=test_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build G0 Book 3 Reality Lock")
    ap.add_argument("--no-tests", action="store_true",
                    help="skip the pytest run (predicates reported as null)")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    lock = build_live_lock(run_tests=not args.no_tests)
    out = Path(args.out) if args.out else COMMITTED_LOCK_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(lock, indent=2))
    return 0 if lock["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
