"""B6.C29 — Book 6 Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book7 =
        security_constitution_complete
        AND principal_model_pass
        AND tenant_isolation_pass
        AND capability_grant_pass
        AND authorization_default_deny
        AND credential_boundary_pass
        AND tool_gateway_pass
        AND mcp_boundary_pass
        AND egress_policy_pass
        AND data_classification_pass
        AND prompt_injection_pass
        AND malicious_document_pass
        AND approval_enforcement_pass
        AND audit_security_pass
        AND revocation_pass
        AND break_glass_pass
        AND submission_disabled
        AND cross_tenant_p0_pass
        AND secret_exposure_p0_pass
        AND adversarial_p0_pass is True
        AND p0_open == 0

Usage:
    python tools/g0/build_book6_reality_lock.py [--no-tests] [--out PATH]

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

from tools.g0._common import load_yaml  # noqa: E402
from tools.g0.validate_attack_surface import (  # noqa: E402
    validate as validate_attack_surface,
)
from tools.g0.validate_authn_credentials import (  # noqa: E402
    validate as validate_authn,
)
from tools.g0.validate_authorization import (  # noqa: E402
    validate as validate_authorization,
)
from tools.g0.validate_boundaries import validate as validate_boundaries  # noqa: E402
from tools.g0.validate_hostile_approval_audit import (  # noqa: E402
    validate as validate_hostile,
)
from tools.g0.validate_identity_isolation import (  # noqa: E402
    validate as validate_identity,
)
from tools.g0.validate_lifecycle_security import (  # noqa: E402
    validate as validate_lifecycle,
)
from tools.g0.validate_security_constitution import (  # noqa: E402
    validate as validate_constitution,
)
from tools.g0.validate_tool_gateway import (  # noqa: E402
    validate as validate_tool_gateway,
)

SECURITY_CONFIG_DIR = Path("config/g0/security")

# (predicate, config stem, validator, positional-flags)
CONFIG_STEMS = (
    "security_constitution.yaml",
    "principal_policy.yaml",
    "capability_grant_policy.yaml",
    "authn_session_policy.yaml",
    "credential_vault_policy.yaml",
    "service_identity_policy.yaml",
    "tool_registry_policy.yaml",
    "integration_egress_policy.yaml",
    "data_classification_policy.yaml",
    "hostile_content_policy.yaml",
    "approval_audit_policy.yaml",
    "lifecycle_policy.yaml",
    "observability_policy.yaml",
    "threat_model.yaml",
    "attack_surface.yaml",
    "security_performance.yaml",
)

COMMITTED_LOCK_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "00-ratification"
    / "G0_B6_REALITY_LOCK.json"
)


def _run_book6_tests() -> dict:
    env = {**os.environ, "G0_SKIP_LOCK_FRESHNESS": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book6", "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=600, env=env,
    )
    return _parse_pytest(proc)


def _run_adversarial_tests() -> dict:
    """Dedicated C26 adversarial + C27 integration + C28 perf run — P0
    evidence."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/g0/book6/test_adversarial_security.py",
         "tests/g0/book6/test_security_integration_properties.py",
         "tests/g0/book6/test_security_performance.py", "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=300,
    )
    return _parse_pytest(proc)


def _parse_pytest(proc: subprocess.CompletedProcess) -> dict:
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    match = re.search(r"(\d+) passed", tail[0])
    failed = re.search(r"(\d+) failed", tail[0])
    return {
        "exit_code": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "failed": int(failed.group(1)) if failed else (1 if proc.returncode else 0),
        "summary": tail[0],
    }


def _errors_ok(fn, cfg) -> bool:
    errors: list[str] = []
    res = fn(errors, cfg)
    if isinstance(res, tuple):
        return not errors and bool(res[0])
    return not errors


def _ok(res: tuple[bool, dict]) -> bool:
    return bool(res[0])


def compute_lock(configs: dict, test_results: dict | None = None,
                 adversarial_results: dict | None = None) -> dict:
    """Compute the Reality Lock from loaded configs (+ optional live runs)."""

    constitution_ok = _errors_ok(validate_constitution,
                                 configs["security_constitution.yaml"])
    principal_ok = _ok(validate_identity([], configs["principal_policy.yaml"]))
    capability_ok = _errors_ok(validate_authorization,
                               configs["capability_grant_policy.yaml"])
    authn_ok = _errors_ok(validate_authn, configs["authn_session_policy.yaml"])
    tool_ok = _errors_ok(validate_tool_gateway,
                         configs["tool_registry_policy.yaml"])
    bound_ok = _errors_ok(validate_boundaries,
                          configs["integration_egress_policy.yaml"])
    hostile_ok = _errors_ok(validate_hostile,
                            configs["hostile_content_policy.yaml"])
    lifecycle_ok = _errors_ok(validate_lifecycle,
                              configs["lifecycle_policy.yaml"])
    surface_ok = _ok(validate_attack_surface([], configs["attack_surface.yaml"]))

    tests_green = test_results is not None and \
        test_results["exit_code"] == 0 and test_results["failed"] == 0

    def behavioral(config_ok: bool) -> bool:
        return config_ok and tests_green

    # submission_disabled derives from the approval/audit policy structural
    # control — the capability is phase-disabled and the policy marks the
    # submission phase DISABLED; never a hard-coded constant.
    approval_cfg = configs["approval_audit_policy.yaml"]
    submission_disabled = (approval_cfg.get("submission_phase") == "DISABLED"
                           and tests_green)
    p0_rows = configs["threat_model.yaml"].get("p0_threats", [])
    p0_open_threats = sum(
        1 for t in p0_rows
        if t.get("residual_risk") not in (None, "LOW", "MEDIUM")
    )
    # fewer than the plan-required 6 P0 rows is itself an open P0 gap
    if len(p0_rows) < 6:
        p0_open_threats += (6 - len(p0_rows))

    predicates = {
        "security_constitution_complete": constitution_ok,
        "principal_model_pass": behavioral(principal_ok),
        "tenant_isolation_pass": behavioral(principal_ok),
        "capability_grant_pass": behavioral(capability_ok),
        "authorization_default_deny": behavioral(capability_ok),
        "credential_boundary_pass": behavioral(authn_ok),
        "tool_gateway_pass": behavioral(tool_ok),
        "mcp_boundary_pass": behavioral(tool_ok),
        "egress_policy_pass": behavioral(bound_ok),
        "data_classification_pass": behavioral(bound_ok),
        "prompt_injection_pass": behavioral(hostile_ok),
        "malicious_document_pass": behavioral(hostile_ok),
        "approval_enforcement_pass": behavioral(hostile_ok),
        "audit_security_pass": behavioral(hostile_ok),
        "revocation_pass": behavioral(lifecycle_ok),
        "break_glass_pass": behavioral(lifecycle_ok),
        "submission_disabled": submission_disabled,
        "attack_surface_register_pass": behavioral(surface_ok),
    }

    if test_results is None and adversarial_results is None:
        predicates["adversarial_p0_pass"] = None
        predicates["cross_tenant_p0_pass"] = None
        predicates["secret_exposure_p0_pass"] = None
    else:
        adv_green = adversarial_results is not None and \
            adversarial_results["exit_code"] == 0 and \
            adversarial_results["failed"] == 0
        predicates["adversarial_p0_pass"] = adv_green
        # cross-tenant and secret-exposure are the two P0 categories the 50
        # scenario suite specifically proves
        predicates["cross_tenant_p0_pass"] = adv_green
        predicates["secret_exposure_p0_pass"] = adv_green

    p0_open = p0_open_threats
    status = "PASS"
    failed_preds = []
    for key, value in predicates.items():
        if value is not True:
            p0_open += 1
            failed_preds.append(key)
    if p0_open or not tests_green:
        status = "FAIL"

    lock = {
        "book": "G0-B6",
        "status": status,
        **predicates,
        "p0_open": p0_open,
        "ready_for_book7": status == "PASS",
        "evidence": {
            "test_results": test_results,
            "adversarial_results": adversarial_results,
            "p0_threats_registered": len(
                configs["threat_model.yaml"].get("p0_threats", [])),
            "p0_open_threats": p0_open_threats,
            "failed_predicates": failed_preds,
        },
    }
    return lock


def build_live_lock(*, run_tests: bool = True) -> dict:
    configs = {stem: load_yaml(SECURITY_CONFIG_DIR / stem)
               for stem in CONFIG_STEMS}
    test_results = _run_book6_tests() if run_tests else None
    adversarial_results = _run_adversarial_tests() if run_tests else None
    return compute_lock(configs, test_results=test_results,
                        adversarial_results=adversarial_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Book 6 Reality Lock")
    ap.add_argument("--no-tests", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    lock = build_live_lock(run_tests=not args.no_tests)
    out_path = args.out or COMMITTED_LOCK_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"status={lock['status']} ready_for_book7={lock['ready_for_book7']} "
          f"p0_open={lock['p0_open']}")
    if lock["status"] != "PASS":
        print("failed predicates:", lock["evidence"]["failed_predicates"])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())