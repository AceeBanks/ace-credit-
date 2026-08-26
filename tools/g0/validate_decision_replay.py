#!/usr/bin/env python3
"""G0-B5-C7-C9 — decision types + invalidation rules validator."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
DECISION_TYPES_PATH = _ROOT / "config/g0/evidence/decision_types.yaml"
INVALIDATION_RULES_PATH = _ROOT / "config/g0/evidence/invalidation_rules.yaml"

REQUIRED_DECISION_TYPES = {
    "ELIGIBILITY", "MATCH_RANKING", "FACT_PROMOTION", "CONFLICT_RESOLUTION",
    "REQUIREMENT_COVERAGE", "BUDGET_VALIDATION", "QA_FACTUALITY",
    "QA_ALIGNMENT", "SUBMISSION_READINESS", "MEMORY_PROMOTION",
    "CHANGE_PROMOTION", "POLICY_AUTHORIZATION"}
VALID_REPLAY_MODES = {"DETERMINISTIC", "MODEL_ASSISTED", "AUDIT_REQUIRED",
                      "DETERMINISTIC_WITH_PROJECTION"}


def load_configs() -> tuple[dict, dict]:
    return (yaml.safe_load(DECISION_TYPES_PATH.read_text(encoding="utf-8")),
            yaml.safe_load(INVALIDATION_RULES_PATH.read_text(encoding="utf-8")))


def validate(errors: list[str] | None = None,
             decision_types: dict | None = None,
             invalidation: dict | None = None) -> list[str]:
    errors = [] if errors is None else errors
    if decision_types is None or invalidation is None:
        dt, inv = load_configs()
        decision_types = decision_types if decision_types is not None else dt
        invalidation = invalidation if invalidation is not None else inv

    dtypes = {d["id"] for d in decision_types.get("decision_types", [])}
    if dtypes != REQUIRED_DECISION_TYPES:
        errors.append(f"decision types mismatch: missing="
                      f"{sorted(REQUIRED_DECISION_TYPES - dtypes)} "
                      f"unknown={sorted(dtypes - REQUIRED_DECISION_TYPES)}")
    for d in decision_types.get("decision_types", []):
        if d.get("replay_mode") not in VALID_REPLAY_MODES:
            errors.append(f"decision {d.get('id')}: invalid replay_mode")
    for rule in ("DEC-001", "DEC-002", "DEC-003", "DEC-004", "DEC-005"):
        if rule not in {h["id"] for h in decision_types.get("hard_rules", [])}:
            errors.append(f"missing decision hard rule {rule}")

    if not invalidation.get("selective_rules"):
        errors.append("invalidation requires selective_rules")
    for rule in ("INV-004", "INV-005", "INV-006", "INV-007"):
        if rule not in {h["id"] for h in invalidation.get("hard_rules", [])}:
            errors.append(f"missing invalidation hard rule {rule}")
    return errors


def check(decision_types: dict, invalidation: dict) -> tuple[bool, dict]:
    errors: list[str] = []
    validate(errors, decision_types=decision_types, invalidation=invalidation)
    return (not errors, {"errors": errors})


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate decision/replay configs")
    ap.add_argument("--decision-types", type=Path, default=None)
    ap.add_argument("--invalidation", type=Path, default=None)
    args = ap.parse_args()
    errors: list[str] = []
    validate(errors,
             decision_types=yaml.safe_load(args.decision_types.read_text(encoding="utf-8"))
             if args.decision_types else None,
             invalidation=yaml.safe_load(args.invalidation.read_text(encoding="utf-8"))
             if args.invalidation else None)
    if errors:
        print("FAIL: decision/replay configs invalid")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: decision types and invalidation rules valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
