#!/usr/bin/env python3
"""G0-B5-C21 — validate_performance_envelope.

Validates the performance envelope policy and runs the small-fixture
benchmark, comparing against the prototype ceilings. Exit 0 when the policy
is valid and the measured envelope holds.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.benchmarks import (  # noqa: E402
    WORKLOADS,
    check_envelope,
    run_benchmark,
)
from tools.g0._common import load_yaml  # noqa: E402

EXPECTED_RULES = ("PERF-001", "PERF-002", "PERF-003")


def validate(errors: list[str] | None = None,
            policy: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/performance_envelope.yaml")
    rule_ids = [r.get("id") for r in policy.get("rules", [])]
    for rid in EXPECTED_RULES:
        if rid not in rule_ids:
            errors.append(f"performance policy missing rule {rid}")
            ok = False
    for wl in WORKLOADS:
        if wl not in policy.get("workloads", []):
            errors.append(f"performance policy missing workload {wl}")
            ok = False
    if not policy.get("prototype_ceilings"):
        errors.append("performance policy must define prototype_ceilings")
        ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "workloads": len(policy.get("workloads", [])),
                "fixture_sizes": len(policy.get("benchmark_fixture_sizes", []))}


def run_and_check() -> tuple[bool, dict]:
    policy = load_yaml(_ROOT / "config/g0/evidence/performance_envelope.yaml")
    results = run_benchmark(tenants=1, opportunities=10, samples=100)
    ok, problems = check_envelope(results, policy["prototype_ceilings"])
    return (ok and not problems), {"results": results, "problems": problems}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("PERFORMANCE POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    bench_ok, bench = run_and_check()
    if not bench_ok:
        print("PERFORMANCE ENVELOPE VIOLATED")
        for p in bench["problems"]:
            print(f"  - {p}")
        return 1
    print("performance envelope OK: "
          f"p50/p95 within ceilings across {WORKLOADS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
