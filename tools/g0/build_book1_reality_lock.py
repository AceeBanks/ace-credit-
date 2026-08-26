"""B1.C16 — Book 1 Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book2 =
        constitution_complete
        AND client_phase1_coverage == 1.0
        AND actors_with_authority_ceiling == 1.0
        AND capabilities_with_policy_metadata == 1.0
        AND unknown_defaults_deny
        AND tenant_scope_tests_pass
        AND submission_disabled
        AND drafting_enabled_l2
        AND self_improvement_tests_pass
        AND secret_boundary_tests_pass
        AND adversarial_p0_pass
        AND p0_open == 0

Usage:
    python tools/g0/build_book1_reality_lock.py [--no-tests] [--out PATH]

`--no-tests` skips the pytest run (used by unit tests that inject fixtures);
the emitted lock then reports the test-derived predicates as null rather than
a claim. `submission_disabled` is derived from registry/policy evidence per
the Book 0 handoff (CD-003), not from tool availability.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import POLICY_CONFIG_DIR, load_yaml
from tools.g0.validate_constitution import validate as validate_constitution
from tools.g0.validate_policy_package import validate as validate_package

from prototype.g0.policy.evaluator import evaluate
from prototype.g0.policy.models import (
    Actor,
    AuthorityLevel,
    Decision,
    PolicyContext,
    Reason,
)
from prototype.g0.policy.registry import PolicyRegistry

COMMITTED_LOCK_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "00-ratification"
    / "G0_B1_REALITY_LOCK.json"
)

CONFIGS = {
    "constitution": POLICY_CONFIG_DIR / "constitutional_laws.yaml",
    "package": POLICY_CONFIG_DIR,                 # actor/ladder/capability/approval/failure
}

SUBMISSION_CAPS = ("application.submit", "submission.prepare", "submission.execute",
                   "submission.certify", "submission.sign")
DRAFT_CAPS = ("application.draft_full_proposal", "application.draft_business_plan",
              "application.draft_pitch_deck", "application.draft_goal_sheet",
              "application.draft_section")
TENANT = "tenant-alpha"


def _run_book1_tests() -> dict:
    # Recursion guard: the lock-freshness test itself invokes this builder; the
    # inner pytest run must skip it or we recurse forever.
    env = {**os.environ, "G0_SKIP_LOCK_FRESHNESS": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book1", "-q", "--tb=no"],
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
        "scope": "tests/g0/book1 excluding G0_B1_REALITY_LOCK.json freshness self-test",
    }


def _ceo() -> Actor:
    return Actor("ceo-1", "ACTOR-HERMES-CEO", (TENANT,), AuthorityLevel.L2)


def _ctx(resource_type: str) -> PolicyContext:
    return PolicyContext(tenant_id=TENANT, project_id="proj-1",
                         resource_type=resource_type)


def _evaluator_predicates(policy_dir: Path) -> dict:
    """PDP-level predicates derived from the live policy registers."""
    reg = PolicyRegistry.load(policy_dir)
    caps = {c.capability_id: c for c in reg._capabilities.values()}

    # unknown defaults deny (LAW-B1-005)
    r_unknown_actor = evaluate(reg, None, "opportunity.search", _ctx("opportunity"))
    r_unknown_cap = evaluate(reg, _ceo(), "grant.auto_apply_all", _ctx("opportunity"))
    unknown_defaults_deny = (
        (r_unknown_actor.decision, r_unknown_actor.reason_code)
        == (Decision.DENY, Reason.UNKNOWN_ACTOR)
        and (r_unknown_cap.decision, r_unknown_cap.reason_code)
        == (Decision.DENY, Reason.UNKNOWN_CAPABILITY)
    )

    # tenant scope (LAW-B1-015)
    r_no_tenant = evaluate(reg, _ceo(), "opportunity.search",
                           PolicyContext(tenant_id=None, project_id="proj-1",
                                         resource_type="opportunity"))
    r_cross = evaluate(reg, _ceo(), "opportunity.search",
                       PolicyContext(tenant_id="tenant-beta", project_id="proj-1",
                                     resource_type="opportunity"))
    tenant_scope_tests_pass = (
        (r_no_tenant.decision, r_no_tenant.reason_code)
        == (Decision.DENY, Reason.TENANT_SCOPE_MISSING)
        and (r_cross.decision, r_cross.reason_code)
        == (Decision.DENY, Reason.TENANT_SCOPE_DENIED)
    )

    # submission disabled — registry evidence (CD-003), plus PDP denial
    submission_disabled = all(
        caps[cid].phase_status == "DISABLED" and caps[cid].approval_class == "APX"
        for cid in SUBMISSION_CAPS if cid in caps
    ) and all(
        evaluate(reg, _ceo(), cid, _ctx(next(iter(caps[cid].resource_types)))).decision
        is Decision.DENY for cid in SUBMISSION_CAPS if cid in caps
    )

    # drafting enabled at L2 (LAW-B1-013)
    drafting_enabled_l2 = all(
        caps[cid].phase_status == "ENABLED"
        and AuthorityLevel.rank(caps[cid].minimum_level)
        <= AuthorityLevel.rank(AuthorityLevel.L2)
        for cid in DRAFT_CAPS if cid in caps
    )

    return {
        "unknown_defaults_deny": unknown_defaults_deny,
        "tenant_scope_tests_pass": tenant_scope_tests_pass,
        "submission_disabled": submission_disabled,
        "drafting_enabled_l2": drafting_enabled_l2,
    }


def _client_phase1_coverage(policy_dir: Path) -> float:
    """Fraction of Phase 1 client deliverables with a legal capability path.

    Imported from the B1.C12 coverage matrix so the lock and the tests share
    one source of truth. CR-13 (auto-submit) is excluded: it is deliberately
    blocked, and is instead asserted by the adversarial/submission predicates.
    """
    from tests.g0.book1.test_client_vision_coverage import (  # noqa: E402
        CLIENT_REQUIREMENTS,
        _CAP_RESOURCE,
        _ctx as cov_ctx,
    )
    from prototype.g0.policy.evaluator import evaluate as ev  # noqa: E402

    reg = PolicyRegistry.load(policy_dir)
    covered = 0
    total = 0
    for req in CLIENT_REQUIREMENTS:
        if not req["constitution_allows"]:
            continue
        total += 1
        legal = any(
            ev(reg, _ceo(), cid, cov_ctx(_CAP_RESOURCE[cid])).decision
            in (Decision.ALLOW, Decision.REQUIRE_APPROVAL)
            for cid in req["capability_ids"]
        )
        covered += int(legal)
    return covered / total if total else 0.0


def _yaml_predicates(policy_dir: Path, package_data: dict) -> dict:
    """Register-level predicates from YAML evidence."""
    actors = {a["actor_type"]: a for a in package_data["actors"]["actors"]}
    caps = package_data["capabilities"]["capabilities"]

    actors_with_ceiling = sum(
        1 for a in actors.values() if a.get("default_authority_ceiling"))
    actors_with_authority_ceiling = actors_with_ceiling / len(actors) if actors else 0.0

    ok_pkg, _ = validate_package(package_data)
    capabilities_with_policy_metadata = 1.0 if ok_pkg else 0.0

    # self-improvement cannot self-ratify (LAW-B1-017/018)
    gov = yaml.safe_load((policy_dir / "self_improvement.yaml").read_text(encoding="utf-8"))
    ceo = gov["actor_permissions"]["ACTOR-HERMES-CEO"]
    self_improvement_tests_pass = (
        "promote_own_authority_increase" in ceo["may_not"]
        and "promote_change" not in [m.lower() for m in ceo["may"]]
    )

    # secrets never live with conversational actors (LAW-B1-014)
    secret_boundary_tests_pass = all(
        not a.get("may_hold_credentials")
        for a in actors.values()
        if a["actor_type"].startswith("ACTOR-HERMES") or a["actor_type"] == "ACTOR-WORKER"
    ) and next(
        a for a in actors.values() if a["actor_type"] == "ACTOR-EXTERNAL-INTEGRATION"
    )["status"] == "DISABLED"

    return {
        "actors_with_authority_ceiling": actors_with_authority_ceiling,
        "capabilities_with_policy_metadata": capabilities_with_policy_metadata,
        "self_improvement_tests_pass": self_improvement_tests_pass,
        "secret_boundary_tests_pass": secret_boundary_tests_pass,
    }


def compute_lock(configs: dict, test_results: dict | None = None) -> dict:
    """Compute the Reality Lock from loaded configs (+ optional pytest results).

    `configs` maps "constitution" -> parsed laws doc and "package" -> the
    load_package() dict {actors, ladder, capabilities, approvals, failures}.
    `test_results` None means tests were not executed (reported as null and
    readiness is blocked).
    """
    ok_const, const_report = validate_constitution(configs["constitution"])
    constitution_complete = ok_const and const_report.get("law_count") == 30

    package_data = configs["package"]
    policy_dir = Path(configs.get("policy_dir") or POLICY_CONFIG_DIR)
    preds = _evaluator_predicates(policy_dir)
    preds.update(_yaml_predicates(policy_dir, package_data))
    preds["constitution_complete"] = constitution_complete
    preds["client_phase1_coverage"] = _client_phase1_coverage(policy_dir)

    # p0_open from the contradiction ledger (shared with Book 0 registers);
    # injectable via configs["ledger"] so defect tests can flip it.
    if "ledger" in configs and isinstance(configs["ledger"], dict):
        ledger = configs["ledger"]
    else:
        ledger = load_yaml(_ROOT / "config/g0/ratification/contradiction_ledger.yaml")
    p0_open = len([c for c in ledger.get("contradictions", [])
                   if c.get("severity") == "P0" and c.get("status") != "RESOLVED"])

    if test_results is None:
        preds["adversarial_p0_pass"] = None
    else:
        preds["adversarial_p0_pass"] = (
            test_results["exit_code"] == 0 and test_results["failed"] == 0
        )

    ready = (
        all(v is True for k, v in preds.items() if k != "client_phase1_coverage"
            and k != "actors_with_authority_ceiling"
            and k != "capabilities_with_policy_metadata")
        and preds["client_phase1_coverage"] >= 1.0
        and preds["actors_with_authority_ceiling"] >= 1.0
        and preds["capabilities_with_policy_metadata"] >= 1.0
        and p0_open == 0
    )

    return {
        "book": "G0-B1",
        "status": "PASS" if ready else "FAIL",
        "constitution_complete": preds["constitution_complete"],
        "client_phase1_coverage": round(preds["client_phase1_coverage"], 6),
        "actors_with_authority_ceiling": round(preds["actors_with_authority_ceiling"], 6),
        "capabilities_with_policy_metadata": round(
            preds["capabilities_with_policy_metadata"], 6),
        "unknown_defaults_deny": preds["unknown_defaults_deny"],
        "tenant_scope_tests_pass": preds["tenant_scope_tests_pass"],
        "submission_disabled": preds["submission_disabled"],
        "drafting_enabled_l2": preds["drafting_enabled_l2"],
        "self_improvement_tests_pass": preds["self_improvement_tests_pass"],
        "secret_boundary_tests_pass": preds["secret_boundary_tests_pass"],
        "adversarial_p0_pass": preds["adversarial_p0_pass"],
        "p0_open": p0_open,
        "ready_for_book2": ready,
        "evidence": {
            "test_results": test_results,
            "law_count": const_report.get("law_count"),
        },
    }


def build_live_lock(run_tests: bool = True) -> dict:
    configs = {
        "constitution": load_yaml(CONFIGS["constitution"]),
        "package": {
            "actors": load_yaml(POLICY_CONFIG_DIR / "actor_catalog.yaml"),
            "ladder": load_yaml(POLICY_CONFIG_DIR / "authority_matrix.yaml"),
            "capabilities": load_yaml(POLICY_CONFIG_DIR / "capability_registry.yaml"),
            "approvals": load_yaml(POLICY_CONFIG_DIR / "approval_matrix.yaml"),
            "failures": load_yaml(POLICY_CONFIG_DIR / "failure_matrix.yaml"),
        },
        "policy_dir": str(POLICY_CONFIG_DIR),
    }
    test_results = _run_book1_tests() if run_tests else None
    return compute_lock(configs, test_results=test_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build G0 Book 1 Reality Lock")
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
