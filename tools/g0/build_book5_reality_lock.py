"""B5.C26 — Book 5 Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book6 =
        evidence_constitution_complete
        AND provenance_model_pass
        AND evidence_graph_semantics_pass
        AND decision_record_pass
        AND historical_replay_pass
        AND contradiction_retention_pass
        AND dependency_invalidation_pass
        AND retrieval_authority_pass
        AND graph_rebuild_exit_pass
        AND vector_rebuild_exit_pass
        AND semantica_bakeoff_complete
        AND storage_adr_ratified
        AND tenant_isolation_pass
        AND claim_ledger_pass
        AND client_explanation_pass
        AND audit_evidence_linkage_pass
        AND eval_lineage_pass
        AND d0_d1_evidence_ready
        AND adversarial_p0_pass is True
        AND p0_open == 0

Usage:
    python tools/g0/build_book5_reality_lock.py [--no-tests] [--out PATH]

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
from tools.g0.validate_adversarial_evidence import (  # noqa: E402
    validate as validate_adversarial_catalog,
)
from tools.g0.validate_claim_ledger import validate as validate_claim_ledger  # noqa: E402
from tools.g0.validate_decision_replay import (  # noqa: E402
    check as check_decision_replay,
)
from tools.g0.validate_degraded_modes import validate as validate_degraded  # noqa: E402
from tools.g0.validate_draft_readiness import validate as validate_draft_readiness  # noqa: E402
from tools.g0.validate_eval_lineage import validate as validate_eval_lineage  # noqa: E402
from tools.g0.validate_evidence_constitution import (  # noqa: E402
    validate as validate_evidence_constitution,
)
from tools.g0.validate_explanation_packet import (  # noqa: E402
    validate as validate_explanation,
)
from tools.g0.validate_linkage import validate as validate_linkage  # noqa: E402
from tools.g0.validate_performance_envelope import (  # noqa: E402
    validate as validate_performance,
)
from tools.g0.validate_provenance_graph import (  # noqa: E402
    validate as validate_provenance_graph,
)
from tools.g0.validate_quality_contradiction import (  # noqa: E402
    check as check_quality_contradiction,
)
from tools.g0.validate_research_finding import (  # noqa: E402
    validate as validate_research,
)
from tools.g0.validate_retrieval_projection import (  # noqa: E402
    check as check_retrieval_projection,
)
from tools.g0.validate_visibility import validate as validate_visibility  # noqa: E402

EVIDENCE_CONFIG_DIR = Path("config/g0/evidence")

CONFIG_STEMS = (
    "evidence_constitution.yaml", "evidence_edge_types.yaml",
    "evidence_quality_dimensions.yaml", "contradiction_types.yaml",
    "decision_types.yaml", "invalidation_rules.yaml",
    "retrieval_policies.yaml", "projection_policies.yaml",
    "explanation_policy.yaml", "claim_ledger_policy.yaml",
    "research_finding_policy.yaml", "linkage_policy.yaml",
    "eval_lineage_policy.yaml", "draft_readiness_policy.yaml",
    "performance_envelope.yaml", "visibility_policy.yaml",
    "degraded_modes.yaml", "adversarial_evidence.yaml",
)

COMMITTED_LOCK_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "00-ratification"
    / "G0_B5_REALITY_LOCK.json"
)

_MISSING = object()  # sentinel: caller explicitly provides no bake-off

BAKEOFF_RESULTS_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "05-evidence"
    / "G0_B5_SEMANTICA_BAKEOFF_RESULTS.json"
)

STORAGE_ADR_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "05-evidence"
    / "G0_B5_STORAGE_ADR.md"
)


def _run_book5_tests() -> dict:
    env = {**os.environ, "G0_SKIP_LOCK_FRESHNESS": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book5", "-q", "--tb=no"],
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
        "scope": "tests/g0/book5 excluding G0_B5_REALITY_LOCK.json freshness self-test",
    }


def _run_adversarial_tests() -> dict:
    """Dedicated C24 adversarial + C25 integration run — P0 evidence."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/g0/book5/test_adversarial_evidence.py",
         "tests/g0/book5/test_integration_properties.py", "-q", "--tb=no"],
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
        "scope": "tests/g0/book5/test_adversarial_evidence.py + test_integration_properties.py",
    }


def _errors_ok(fn, *extra) -> bool:
    errors: list[str] = []
    fn(errors, *extra)
    return not errors


def _ok(check_result: tuple[bool, dict]) -> bool:
    return bool(check_result[0])


def _load_bakeoff() -> dict | None:
    if not BAKEOFF_RESULTS_PATH.exists():
        return None
    try:
        return json.loads(BAKEOFF_RESULTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def compute_lock(configs: dict, test_results: dict | None = None,
                 adversarial_results: dict | None = None,
                 bakeoff: dict | None = _MISSING,
                 adr_text: str | None = None) -> dict:
    """Compute the Reality Lock from loaded configs (+ optional live runs)."""

    evidence_ok = _errors_ok(validate_evidence_constitution,
                             configs["evidence_constitution"])
    provenance_ok = _errors_ok(validate_provenance_graph,
                               configs["evidence_edge_types"])
    decision_ok = _ok(check_decision_replay(configs["decision_types"],
                                            configs["invalidation_rules"]))
    quality_ok = _ok(check_quality_contradiction(
        configs["evidence_quality_dimensions"],
        configs["contradiction_types"]))
    retrieval_ok = _ok(check_retrieval_projection(
        configs["retrieval_policies"], configs["projection_policies"]))
    explanation_ok = _ok(validate_explanation([], configs["explanation_policy"]))
    claim_ok = _ok(validate_claim_ledger([], configs["claim_ledger_policy"]))
    research_ok = _ok(validate_research([], configs["research_finding_policy"]))
    linkage_ok = _ok(validate_linkage([], configs["linkage_policy"]))
    eval_ok = _ok(validate_eval_lineage([], configs["eval_lineage_policy"]))
    draft_ok = _ok(validate_draft_readiness([], configs["draft_readiness_policy"]))
    perf_ok = _ok(validate_performance([], configs["performance_envelope"]))
    vis_ok = _ok(validate_visibility([], configs["visibility_policy"]))
    degrad_ok = _ok(validate_degraded([], configs["degraded_modes"]))
    adv_catalog_ok = _ok(validate_adversarial_catalog(
        [], configs["adversarial_evidence"]))

    # bake-off and ADR are file-based evidence
    if bakeoff is _MISSING:
        bakeoff = _load_bakeoff()
    bakeoff_complete = bool(
        bakeoff and bakeoff.get("semantica_correct", 0) >= 9
        and bakeoff.get("baseline_correct", 0) >= 9)
    w7_ok = any(
        r.get("workload") == "W7_rebuild_exit" and r.get("correct")
        for r in (bakeoff or {}).get("workloads", [])
        if r.get("candidate") == "semantica")
    adr_text = adr_text if adr_text is not None else (
        STORAGE_ADR_PATH.read_text(encoding="utf-8")
        if STORAGE_ADR_PATH.exists() else "")
    adr_ratified = ("RATIFIED" in adr_text and "Pattern A" in adr_text)

    tests_green = test_results is not None and \
        test_results["exit_code"] == 0 and test_results["failed"] == 0

    def behavioral(config_ok: bool) -> bool:
        return config_ok and tests_green

    predicates = {
        "evidence_constitution_complete": evidence_ok,
        "provenance_model_pass": provenance_ok,
        "evidence_graph_semantics_pass": provenance_ok,
        "decision_record_pass": decision_ok,
        "historical_replay_pass": behavioral(decision_ok),
        "contradiction_retention_pass": quality_ok,
        "dependency_invalidation_pass": behavioral(decision_ok),
        "retrieval_authority_pass": retrieval_ok,
        "graph_rebuild_exit_pass": bakeoff_complete and w7_ok,
        "vector_rebuild_exit_pass": behavioral(retrieval_ok and vis_ok),
        "semantica_bakeoff_complete": bakeoff_complete,
        "storage_adr_ratified": adr_ratified,
        "tenant_isolation_pass": behavioral(provenance_ok and vis_ok),
        "claim_ledger_pass": claim_ok and research_ok,
        "client_explanation_pass": explanation_ok,
        "audit_evidence_linkage_pass": linkage_ok,
        "eval_lineage_pass": eval_ok,
        "d0_d1_evidence_ready": draft_ok,
    }

    if test_results is None and adversarial_results is None:
        predicates["adversarial_p0_pass"] = None
    else:
        adv_green = adversarial_results is not None and \
            adversarial_results["exit_code"] == 0 and \
            adversarial_results["failed"] == 0
        predicates["adversarial_p0_pass"] = (
            adv_catalog_ok and adv_green)

    p0_open = 0
    status = "PASS"
    failed_preds = []
    for key, value in predicates.items():
        if value is not True:
            p0_open += 1
            failed_preds.append(key)
    if p0_open or not tests_green:
        status = "FAIL"

    lock = {
        "book": "G0-B5",
        "status": status,
        **predicates,
        "p0_open": p0_open,
        "ready_for_book6": status == "PASS",
        "evidence": {
            "test_results": test_results,
            "adversarial_results": adversarial_results,
            "bakeoff_summary": (bakeoff or {}).get("semantica_correct"),
            "storage_adr_present": bool(adr_text),
            "failed_predicates": failed_preds,
        },
    }
    return lock


def build_live_lock(*, run_tests: bool = True) -> dict:
    configs = {stem.removesuffix(".yaml"): load_yaml(EVIDENCE_CONFIG_DIR / stem)
               for stem in CONFIG_STEMS}
    test_results = _run_book5_tests() if run_tests else None
    adversarial_results = _run_adversarial_tests() if run_tests else None
    return compute_lock(configs, test_results=test_results,
                        adversarial_results=adversarial_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Book 5 Reality Lock")
    ap.add_argument("--no-tests", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    lock = build_live_lock(run_tests=not args.no_tests)
    out_path = args.out or COMMITTED_LOCK_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"status={lock['status']} ready_for_book6={lock['ready_for_book6']} "
          f"p0_open={lock['p0_open']}")
    if lock["status"] != "PASS":
        print("failed predicates:", lock["evidence"]["failed_predicates"])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
