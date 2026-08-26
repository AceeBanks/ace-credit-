"""B0.C6 — Book 0 Ratification Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book1_ratification =
        artifact_manifest_complete
        AND all_major_decisions_classified
        AND p0_open == 0
        AND prototype_candidates_bounded
        AND non_goals_frozen
        AND supersession_cycles == 0
        AND stale_authority_detected == False
        AND book0_tests_all_pass

Usage:
    python tools/g0/build_book0_reality_lock.py [--no-tests] [--out PATH]

`--no-tests` skips the pytest run (used by unit tests that inject fixtures);
the emitted lock then reports book0_tests_all_pass as null rather than a claim.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import RATIFICATION_CONFIG_DIR, load_yaml
from tools.g0.validate_artifact_manifest import validate as validate_manifest
from tools.g0.validate_contradictions import validate as validate_contradictions
from tools.g0.validate_decision_register import validate as validate_decisions
from tools.g0.validate_freeze_registers import (
    validate_candidates,
    validate_non_goals,
)

CONFIGS = {
    "manifest": RATIFICATION_CONFIG_DIR / "artifact_manifest.yaml",
    "decisions": RATIFICATION_CONFIG_DIR / "decision_register.yaml",
    "contradictions": RATIFICATION_CONFIG_DIR / "contradiction_ledger.yaml",
    "non_goals": RATIFICATION_CONFIG_DIR / "non_goals.yaml",
    "candidates": RATIFICATION_CONFIG_DIR / "prototype_candidates.yaml",
}

VALIDATORS = {
    "manifest": validate_manifest,
    "decisions": validate_decisions,
    "contradictions": validate_contradictions,
    "non_goals": validate_non_goals,
    "candidates": validate_candidates,
}


def _run_book0_tests() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book0", "-q", "--tb=no"],
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
    }


def compute_lock(
    data: dict[str, object],
    test_results: dict | None = None,
) -> dict:
    """Compute the Reality Lock from pre-loaded register data.

    `data` maps register name -> parsed mapping. `test_results` is the dict from
    _run_book0_tests(); None means tests were not executed (reported as null).
    """
    validator_reports: dict[str, dict] = {}
    for name, fn in VALIDATORS.items():
        ok, report = fn(data[name])
        report["ok"] = ok
        validator_reports[name] = report

    manifest = validator_reports["manifest"]
    decisions = validator_reports["decisions"]
    contradictions = validator_reports["contradictions"]
    non_goals = validator_reports["non_goals"]
    candidates = validator_reports["candidates"]

    supersession_cycles = (
        len(manifest.get("supersession_cycles") or [])
        + len(decisions.get("supersession_cycles") or [])
    )
    stale_authority = bool(manifest.get("stale_content"))
    p0_open = len(contradictions.get("open_p0") or [])

    predicates = {
        "artifact_manifest_complete": manifest["ok"],
        "all_major_decisions_classified": decisions["ok"]
        and not decisions.get("missing_categories"),
        "p0_open_zero": p0_open == 0,
        "prototype_candidates_bounded": candidates["ok"]
        and not candidates.get("adopted_at_book0"),
        "non_goals_frozen": non_goals["ok"],
        "supersession_cycles_zero": supersession_cycles == 0,
        "stale_authority_absent": not stale_authority,
    }
    if test_results is None:
        predicates["book0_tests_all_pass"] = None
    else:
        predicates["book0_tests_all_pass"] = (
            test_results["exit_code"] == 0 and test_results["failed"] == 0
        )

    # Readiness is the conjunction of every predicate; a null (not-run) predicate
    # blocks readiness — absence of evidence is not evidence of pass.
    ready = all(v is True for v in predicates.values())

    lock = {
        "book": "G0-B0",
        "status": "PASS" if ready else "FAIL",
        **predicates,
        "p0_open": p0_open,
        "supersession_cycles": supersession_cycles,
        "stale_authority_detected": stale_authority,
        "decision_count": decisions.get("unique_ids"),
        "contradiction_count": contradictions.get("unique_ids"),
        "candidate_count": candidates.get("unique_ids"),
        "non_goal_count": non_goals.get("non_goal_count"),
        "tests": test_results,
        "validator_reports": {
            name: {k: v for k, v in rep.items() if k != "errors"}
            for name, rep in validator_reports.items()
        },
        "errors": [
            f"{name}: {e}"
            for name, rep in validator_reports.items()
            for e in rep.get("errors", [])
        ],
        "ready_for_book1_ratification": ready,
    }
    return lock


def main(argv: list[str]) -> int:
    run_tests = "--no-tests" not in argv
    out_path = None
    if "--out" in argv:
        out_path = Path(argv[argv.index("--out") + 1])

    data = {name: load_yaml(CONFIGS[name]) for name in CONFIGS}
    test_results = _run_book0_tests() if run_tests else None
    lock = compute_lock(data, test_results)

    rendered = json.dumps(lock, indent=2)
    print(rendered)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered + "\n", encoding="utf-8")
    return 0 if lock["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
