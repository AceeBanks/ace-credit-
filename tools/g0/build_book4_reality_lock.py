"""B4.C28 — Book 4 Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book5 =
        dual_hermes_boundary_ratified
        AND personal_contract_complete
        AND ceo_contract_complete
        AND intent_contract_tests_pass
        AND clarification_protocol_pass
        AND task_contract_tests_pass
        AND sidechain_isolation_pass
        AND outcome_explanation_separation_pass
        AND personal_memory_policy_pass
        AND ceo_memory_policy_pass
        AND worker_stateless_default
        AND promotion_supersession_tests_pass
        AND compaction_anchor_tests_pass
        AND cold_reconstruction_pass
        AND multi_project_isolation_pass
        AND multi_tenant_memory_isolation_pass
        AND secret_memory_tests_pass
        AND d1_mock_draft_ready
        AND adversarial_p0_pass is True
        AND p0_open == 0

Usage:
    python tools/g0/build_book4_reality_lock.py [--no-tests] [--out PATH]

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
    load_yaml,
)
from tools.g0.validate_compaction_reconstruction import (  # noqa: E402
    validate_compaction_policy,
    validate_reconstruction_schema,
)
from tools.g0.validate_adversarial_context import check as validate_adversarial_cfg  # noqa: E402
from tools.g0.validate_context_explanation import (  # noqa: E402
    validate_context_budget_policy,
)
from tools.g0.validate_d1_contract import validate as validate_d1_cfg  # noqa: E402
from tools.g0.validate_dual_hermes_boundary import (  # noqa: E402
    validate as validate_boundary_cfg,
)
from tools.g0.validate_feedback_loop import validate as validate_feedback_cfg  # noqa: E402
from tools.g0.validate_intent_clarification import (  # noqa: E402
    validate_clarification_policy,
    validate_clarification_schema,
    validate_intent_schema,
)
from tools.g0.validate_memory_constitutions import (  # noqa: E402
    validate_ceo_classes,
    validate_personal_classes,
    validate_ttl_policy,
)
from tools.g0.validate_memory_lifecycle import (  # noqa: E402
    validate_promotion_policy,
)
from tools.g0.validate_portability import validate as validate_portability_cfg  # noqa: E402
from tools.g0.validate_role_contracts import validate as validate_contracts_cfg  # noqa: E402
from tools.g0.validate_sidechain_synthesis import validate as validate_sidechain  # noqa: E402
from tools.g0.validate_task_delegation import (  # noqa: E402
    validate_worker_context_policy,
)

AGENTS_CONFIG_DIR = Path("config/g0/agents")

STEMS = (
    "dual_hermes_boundary.yaml", "role_contracts.yaml",
    "clarification_policy.yaml", "worker_context_policy.yaml",
    "context_budget_policy.yaml", "memory_ttl_policy.yaml",
    "personal_memory_classes.yaml", "ceo_memory_classes.yaml",
    "memory_promotion_policy.yaml", "compaction_policy.yaml",
    "feedback_policy.yaml", "d1_mock_draft_contract.yaml",
    "skill_boundaries.yaml", "model_independence.yaml", "privacy_scope.yaml",
    "adversarial_context.yaml",
)

COMMITTED_LOCK_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "00-ratification"
    / "G0_B4_REALITY_LOCK.json"
)


def _run_book4_tests() -> dict:
    # Recursion guard: the lock-freshness test itself invokes this builder; the
    # inner pytest run must skip it or we recurse forever.
    env = {**os.environ, "G0_SKIP_LOCK_FRESHNESS": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book4", "-q", "--tb=no"],
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
        "scope": "tests/g0/book4 excluding G0_B4_REALITY_LOCK.json freshness self-test",
    }


def _run_adversarial_tests() -> dict:
    """Dedicated C26 adversarial suite run — P0 evidence for the lock."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/g0/book4/test_adversarial_context_pollution.py", "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=300,
    )
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    match = re.search(r"(\d+) passed", tail[0])
    failed = re.search(r"(\d+) failed", tail[0])
    return {
        "exit_code": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "failed": int(failed.group(1)) if failed else (1 if proc.returncode else 0),
        "summary": tail[0],
        "scope": "tests/g0/book4/test_adversarial_context_pollution.py (A1-A25 + catalog guards)",
    }


def _ok(check_result: tuple[bool, dict]) -> bool:
    return check_result[0]


def _errors_ok(fn, *extra) -> bool:
    errors: list[str] = []
    fn(errors, *extra)
    return not errors


def compute_lock(configs: dict, test_results: dict | None = None,
                 adversarial_results: dict | None = None,
                 ledger: dict | None = None) -> dict:
    """Compute the Reality Lock from loaded configs (+ optional pytest results)."""

    boundary_ok = _ok(validate_boundary_cfg(configs["dual_hermes_boundary"]))
    contracts_ok = _ok(validate_contracts_cfg(configs["role_contracts"]))

    intent_ok = _errors_ok(validate_intent_schema)
    clarification_cfg_ok = _errors_ok(validate_clarification_policy,
                                       configs["clarification_policy"])
    clarification_schema_ok = _errors_ok(validate_clarification_schema)
    worker_cfg_ok = _errors_ok(validate_worker_context_policy,
                                configs["worker_context_policy"])
    sidechain_ok = _errors_ok(validate_sidechain)
    context_budget_ok = _errors_ok(validate_context_budget_policy,
                                    configs["context_budget_policy"])
    personal_ok = _errors_ok(validate_personal_classes,
                              configs["personal_memory_classes"])
    ceo_ok = _errors_ok(validate_ceo_classes,
                        configs["ceo_memory_classes"])
    ttl_ok = _errors_ok(validate_ttl_policy, configs["memory_ttl_policy"])
    promotion_ok = _errors_ok(validate_promotion_policy,
                               configs["memory_promotion_policy"])
    compaction_ok = _errors_ok(validate_compaction_policy,
                                configs["compaction_policy"])
    recon_schema_ok = _errors_ok(validate_reconstruction_schema)
    d1_ok = _ok(validate_d1_cfg(configs["d1_mock_draft_contract"]))
    adversarial_catalog_ok = _ok(validate_adversarial_cfg(
        configs["adversarial_context"]))
    feedback_ok = _ok(validate_feedback_cfg(configs["feedback_policy"]))
    portability_ok = _ok(validate_portability_cfg({
        "skill_boundaries": configs["skill_boundaries"],
        "model_independence": configs["model_independence"],
        "privacy_scope": configs["privacy_scope"],
    }))

    # Behavioral predicates are derived from BOTH the frozen config/schema
    # checks AND the live test run — never hand-set.
    tests_green = test_results is not None and \
        test_results["exit_code"] == 0 and test_results["failed"] == 0

    def behavioral(config_ok: bool) -> bool:
        return config_ok and tests_green

    predicates = {
        "dual_hermes_boundary_ratified": boundary_ok,
        "personal_contract_complete": contracts_ok,
        "ceo_contract_complete": contracts_ok,
        "intent_contract_tests_pass": intent_ok,
        "clarification_protocol_pass": (clarification_cfg_ok
                                        and clarification_schema_ok),
        "task_contract_tests_pass": worker_cfg_ok,
        "sidechain_isolation_pass": sidechain_ok,
        "outcome_explanation_separation_pass": context_budget_ok,
        "personal_memory_policy_pass": personal_ok and ttl_ok,
        "ceo_memory_policy_pass": ceo_ok and ttl_ok,
        "worker_stateless_default": worker_cfg_ok and promotion_ok,
        "promotion_supersession_tests_pass": promotion_ok,
        "compaction_anchor_tests_pass": compaction_ok,
        "cold_reconstruction_pass": behavioral(recon_schema_ok),
        "multi_project_isolation_pass": behavioral(context_budget_ok),
        "multi_tenant_memory_isolation_pass": behavioral(portability_ok),
        "secret_memory_tests_pass": behavioral(sidechain_ok and worker_cfg_ok),
        "d1_mock_draft_ready": d1_ok,
    }

    if test_results is None and adversarial_results is None:
        predicates["adversarial_p0_pass"] = None
    else:
        adv = (adversarial_results if adversarial_results is not None
               else test_results)
        predicates["adversarial_p0_pass"] = (
            adv["exit_code"] == 0 and adv["failed"] == 0
            and adversarial_catalog_ok)

    if not isinstance(ledger, dict):
        ledger = load_yaml(RATIFICATION_CONFIG_DIR / "contradiction_ledger.yaml")
    p0_open = len([c for c in ledger.get("contradictions", [])
                   if c.get("severity") == "P0" and c.get("status") != "RESOLVED"])

    ready = (
        feedback_ok
        and portability_ok
        and adversarial_catalog_ok
        and all(v is True for v in predicates.values())
        and p0_open == 0
    )

    return {
        "book": "G0-B4",
        "status": "PASS" if ready else "FAIL",
        **predicates,
        "p0_open": p0_open,
        "d1_mock_draft_unlocked": predicates["d1_mock_draft_ready"] and ready,
        "ready_for_book5": ready,
        "evidence": {
            "test_results": test_results,
            "adversarial_results": adversarial_results,
            "config_count": len(STEMS),
            "validator_checks": {
                "feedback_policy": feedback_ok,
                "portability_policies": portability_ok,
                "adversarial_catalog": adversarial_catalog_ok,
            },
        },
    }


def build_live_lock(run_tests: bool = True) -> dict:
    configs = {stem.removesuffix(".yaml"): load_yaml(AGENTS_CONFIG_DIR / stem)
               for stem in STEMS}
    test_results = _run_book4_tests() if run_tests else None
    adversarial_results = _run_adversarial_tests() if run_tests else None
    return compute_lock(configs, test_results=test_results,
                        adversarial_results=adversarial_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build G0 Book 4 Reality Lock")
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
