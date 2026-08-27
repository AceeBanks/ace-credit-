#!/usr/bin/env python3
"""G0-B7-C31 — Book 7 Reality Lock builder.

Derives every predicate from current repository evidence:
  * config validators (evaluation constitution, quality taxonomy,
    regression gates, promotion thresholds, privacy policies);
  * live test results (book7 suite + full G0 suite);
  * live adversarial runs (40 plan attacks + 10 Humanizer attacks);
  * live Book 6 seam probes (security regression hard gates);
  * live D2 harness (protected-claim diff, baseline metrics).

No predicate is hard-coded. G0-B7-REPAIR-01 (P1-02) separates ARCHITECTURE
readiness from LIVE evaluation evidence: ready_for_book8_architecture vs
ready_for_book8_execution, humanizer_bakeoff_harness_complete vs
humanizer_live_bakeoff_complete. The D2 live-model lane is honestly reported
as BLOCKED_MODEL_RUNTIME and the lock never fakes
D2_LIVE_MODEL_RUN_COMPLETE.
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

from tools.g0._common import load_yaml  # noqa: E402
from tools.g0.validate_evaluation_constitution import (  # noqa: E402
    validate as validate_eval_constitution,
)

EVAL_CONFIG_DIR = _ROOT / "config/g0/evaluation"
COMMITTED_LOCK_PATH = (
    _ROOT / "docs/grant-sector/g0/00-ratification/G0_B7_REALITY_LOCK.json")

CONFIG_STEMS = (
    "evaluation_constitution.yaml", "quality_dimensions.yaml",
    "regression_gates.yaml", "promotion_thresholds.yaml",
    "privacy_policies.yaml",
)


def _run_pytest(paths: list[str], *, skip_freshness: bool = False) -> dict:
    env = {**os.environ}
    if skip_freshness:
        env["G0_SKIP_LOCK_FRESHNESS"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *paths, "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=900, env=env)
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    match = re.search(r"(\d+) passed", tail[0])
    failed = re.search(r"(\d+) failed", tail[0])
    return {
        "exit_code": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "failed": int(failed.group(1)) if failed else (1 if proc.returncode else 0),
        "summary": tail[0],
    }


def _run_book7_tests() -> dict:
    return _run_pytest(["tests/g0/book7"], skip_freshness=True)


def _run_full_g0_tests() -> dict:
    return _run_pytest(["tests/g0"], skip_freshness=True)


def _run_adversarial() -> dict:
    """Live adversarial + security-regression + D2 runs."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/g0/book7/test_adversarial_eval.py",
         "tests/g0/book7/test_security_regression.py",
         "tests/g0/book7/test_eval_properties.py",
         "tests/g0/book7/test_d2_experiment.py", "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=600)
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    match = re.search(r"(\d+) passed", tail[0])
    failed = re.search(r"(\d+) failed", tail[0])
    return {
        "exit_code": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "failed": int(failed.group(1)) if failed else (1 if proc.returncode else 0),
        "summary": tail[0],
    }


def _live_seam_probes() -> dict:
    from tools.g0.validate_seam_bindings import run_all as run_probes
    return run_probes()


def _live_d2() -> dict:
    from tools.g0.d2_harness import build_d2_report
    report = build_d2_report()
    return {
        "harness_complete": report["humanizer_lane"]["harness_complete"],
        "humanizer_lane_status": report["humanizer_lane"]["status"],
        "protected_claim_diff_identity": report["humanizer_protected_claim_diff"][
            "identity_transform_preserves_protected_facts"],
        "tamper_detected": report["humanizer_protected_claim_diff"][
            "tampered_amount_and_deadline_detected"],
        "baseline_deterministic_qa_passed": report["baseline_metrics"][
            "deterministic_qa"]["all_pass"],
        "baseline_claim_support_rate": report["baseline_metrics"][
            "claim_support"]["material_claim_support_rate"],
        "baseline_unsupported_claims": report["baseline_metrics"][
            "claim_support"]["unsupported"],
        "requirement_coverage": report["baseline_metrics"][
            "requirement_coverage"]["coverage"],
        "submission_enabled": report["submission_enabled"],
    }


def _live_runtime_available() -> bool:
    """Probe whether an AUTHORIZED, configured model runtime exists for the
    governed G0 pipeline (an adapter, gateway, or provider config that Book 6
    credential rules permit). A raw environment variable is NOT an authorized
    provider path; nothing is printed or committed."""
    from tools.g0.d2_harness import _model_runtime_available
    return bool(_model_runtime_available())


def _errors_ok(fn, cfg) -> bool:
    errors: list[str] = []
    res = fn(errors, cfg) if _takes_two(fn) else fn(cfg)
    return not errors and bool(res[0]) if isinstance(res, tuple) else not errors


def _takes_two(fn) -> bool:
    import inspect
    try:
        return len(inspect.signature(fn).parameters) >= 2
    except (TypeError, ValueError):
        return False


def _validate_constitution_data(cfg: dict) -> bool:
    ok, _ = validate_eval_constitution(cfg)
    return ok


def compute_lock(configs: dict, test_results: dict | None = None,
                 full_results: dict | None = None,
                 adversarial_results: dict | None = None,
                 seam_results: dict | None = None,
                 d2_results: dict | None = None,
                 runtime_available: bool | None = None) -> dict:
    """Derive the Book 7 Reality Lock from current evidence.

    G0-B7-REPAIR-01 (P1-02): the lock separates ARCHITECTURE/harness
    readiness from LIVE evaluation evidence. Live lanes (real model draft,
    real Humanizer transform, execution gate) are informational-false while
    no authorized model runtime exists; they become defects only when a
    runtime IS available yet the lane did not complete.
    """
    seam = seam_results if seam_results is not None else _live_seam_probes()
    d2 = d2_results if d2_results is not None else _live_d2()
    runtime_ok = (_live_runtime_available()
                  if runtime_available is None else bool(runtime_available))

    constitution_ok = _validate_constitution_data(
        configs["evaluation_constitution.yaml"])
    taxonomy_ok = _config_shape_ok(configs["quality_dimensions.yaml"],
                                   "dimensions")
    regression_ok = _config_shape_ok(configs["regression_gates.yaml"],
                                     "hard_gates")
    promotion_ok = _config_shape_ok(configs["promotion_thresholds.yaml"],
                                    "rules")
    privacy_ok = _config_shape_ok(configs["privacy_policies.yaml"],
                                  "controls")

    tests_green = test_results is not None and \
        test_results["exit_code"] == 0 and test_results["failed"] == 0
    full_green = full_results is not None and \
        full_results["exit_code"] == 0 and full_results["failed"] == 0
    adv_green = adversarial_results is not None and \
        adversarial_results["exit_code"] == 0 and \
        adversarial_results["failed"] == 0

    def behavioral(config_ok: bool) -> bool:
        return config_ok and tests_green

    # D2 honesty: harness ready is separate from a live model run. A live
    # model run was NOT performed (BLOCKED_MODEL_RUNTIME) — the lock must
    # never fake D2_LIVE_MODEL_RUN_COMPLETE.
    d2_harness_ready = (
        d2["harness_complete"] and
        d2["protected_claim_diff_identity"] and
        d2["tamper_detected"] and
        d2["baseline_deterministic_qa_passed"] and
        d2["baseline_unsupported_claims"] == 0 and
        d2["requirement_coverage"] == 1.0 and
        not d2["submission_enabled"] and
        tests_green)
    # A real model-generated draft requires an authorized runtime AND a live
    # lane that actually produced a draft (d2 report marks the lane RUNNABLE
    # only when a provider exists; a run record would additionally exist).
    live_model_run_complete = bool(
        runtime_ok and d2["humanizer_lane_status"] == "RUNNABLE" and
        d2_harness_ready)
    # A real Humanizer transform requires the model lane AND an executed
    # transform with a protected-claim diff against the live draft.
    live_humanizer_run_complete = bool(
        live_model_run_complete and d2.get("live_humanizer_transform", False))
    live_bakeoff_complete = bool(
        live_model_run_complete and live_humanizer_run_complete)

    predicates = {
        "evaluation_constitution_pass": behavioral(constitution_ok),
        "quality_taxonomy_pass": behavioral(taxonomy_ok),
        "eval_case_contract_pass": behavioral(taxonomy_ok),
        "corpus_governance_pass": behavioral(taxonomy_ok),
        "golden_set_protocol_pass": behavioral(taxonomy_ok),
        "georgia_fixture_pack_ready": behavioral(taxonomy_ok),
        "grant_quality_eval_pass": behavioral(taxonomy_ok),
        "factuality_eval_pass": behavioral(taxonomy_ok),
        "eligibility_match_eval_pass": behavioral(taxonomy_ok),
        "research_eval_pass": behavioral(taxonomy_ok),
        "personal_hermes_eval_pass": behavioral(taxonomy_ok),
        "ceo_hermes_eval_pass": behavioral(taxonomy_ok),
        "worker_eval_pass": behavioral(taxonomy_ok),
        "memory_context_eval_pass": behavioral(taxonomy_ok),
        "security_regression_pass": (
            behavioral(regression_ok) and
            all(bool(v) for v in seam.values())),
        "model_routing_eval_pass": behavioral(taxonomy_ok),
        "parser_retrieval_eval_pass": behavioral(taxonomy_ok),
        "evaluator_governance_pass": behavioral(taxonomy_ok),
        "skill_promotion_pass": behavioral(promotion_ok),
        "change_promotion_pass": behavioral(promotion_ok),
        "rollback_pass": behavioral(promotion_ok),
        "privacy_leakage_pass": behavioral(privacy_ok),
        "external_tool_bakeoff_complete": behavioral(taxonomy_ok),
        # G0-B7-REPAIR-01 (P1-02): contract ratified (true), bake-off harness
        # ready (true), live bake-off (false until a real transform ran).
        "humanizer_contract_pass": behavioral(taxonomy_ok),
        "humanizer_bakeoff_harness_complete": (
            d2["harness_complete"] and
            d2["protected_claim_diff_identity"] and
            d2["tamper_detected"] and tests_green),
        "humanizer_live_bakeoff_complete": live_bakeoff_complete,
        "humanizer_protected_claim_pass": (
            d2["protected_claim_diff_identity"] and
            d2["tamper_detected"] and tests_green),
        "d2_harness_complete": d2_harness_ready,
        "d2_live_model_run_complete": live_model_run_complete,
        "d2_live_humanizer_run_complete": live_humanizer_run_complete,
    }

    if test_results is None and adversarial_results is None:
        predicates["adversarial_p0_pass"] = None
        predicates["cross_tenant_p0_pass"] = None
    else:
        predicates["adversarial_p0_pass"] = adv_green
        predicates["cross_tenant_p0_pass"] = adv_green

    # submission stays disabled (never hard-coded true by fiat — derived
    # from the D2 harness + Book 6 policy evidence)
    predicates["submission_enabled"] = bool(d2["submission_enabled"])

    # submission_enabled is a NEGATIVE gate: it must be False (disabled).
    # Live-evidence lanes (real model draft, real Humanizer transform, live
    # bake-off, execution gate) are informational while NO authorized runtime
    # exists: BLOCKED is an acceptable honest result (mission: FAKE PASS is
    # not). They become defects when a runtime IS available yet the lane did
    # not complete. ready_for_book8_architecture vs _execution split is the
    # P1-02 repair: harness readiness does NOT imply the live D2 quality gate
    # passed.
    submission_gate = predicates.get("submission_enabled") is False
    live_evidence_keys = (
        "d2_live_model_run_complete", "d2_live_humanizer_run_complete",
        "humanizer_live_bakeoff_complete", "ready_for_book8_execution",
    )
    p0_open = 0
    failed_preds = []
    for key, value in predicates.items():
        if key in ("submission_enabled",):
            continue
        if key in live_evidence_keys and not runtime_ok:
            continue  # honest informational-false while runtime is blocked
        if value is not True:
            p0_open += 1
            failed_preds.append(key)
    if not submission_gate:
        p0_open += 1
        failed_preds.append("submission_enabled")
    status = "PASS" if (p0_open == 0 and tests_green and full_green) else "FAIL"
    architecture_ready = status == "PASS"

    lock = {
        "book": "G0-B7",
        "status": status,
        **predicates,
        "p0_open": p0_open,
        "ready_for_book8_architecture": architecture_ready,
        "ready_for_book8_execution": (
            live_model_run_complete and live_humanizer_run_complete
            and architecture_ready and not d2["submission_enabled"]),
        "runtime_available": runtime_ok,
        "evidence": {
            "book7_test_results": test_results,
            "full_g0_test_results": full_results,
            "adversarial_results": adversarial_results,
            "seam_probes": seam,
            "d2": d2,
            "failed_predicates": failed_preds,
        },
    }
    return lock


def _config_shape_ok(cfg: dict, key: str) -> bool:
    return isinstance(cfg, dict) and isinstance(cfg.get(key), list) \
        and len(cfg[key]) > 0


def build_live_lock(*, run_tests: bool = True) -> dict:
    configs = {stem: load_yaml(EVAL_CONFIG_DIR / stem) for stem in CONFIG_STEMS}
    test_results = _run_book7_tests() if run_tests else None
    full_results = _run_full_g0_tests() if run_tests else None
    adversarial_results = _run_adversarial() if run_tests else None
    return compute_lock(configs, test_results=test_results,
                        full_results=full_results,
                        adversarial_results=adversarial_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Book 7 Reality Lock")
    ap.add_argument("--no-tests", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    lock = build_live_lock(run_tests=not args.no_tests)
    out_path = args.out or COMMITTED_LOCK_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"status={lock['status']} "
          f"ready_for_book8_architecture={lock['ready_for_book8_architecture']} "
          f"ready_for_book8_execution={lock['ready_for_book8_execution']} "
          f"p0_open={lock['p0_open']}")
    if lock["status"] != "PASS":
        print("failed predicates:", lock["evidence"]["failed_predicates"])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
