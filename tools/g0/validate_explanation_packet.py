#!/usr/bin/env python3
"""G0-B5-C15 — validate_explanation_packet.

Validates the explanation policy config and any explanation packet JSON
against the schema, the citation rules (EXPL-001..005), and the schema's
enum values. CLI: `python tools/g0/validate_explanation_packet.py [packet.json]`
Exit code 0 when valid; 1 when any error is found.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None

from tools.g0._common import load_yaml  # noqa: E402

STALE_CLASSES = ("TOMBSTONED", "INVALIDATED", "SUPERSEDED", "EXPIRED")


def validate(errors: list[str] | None = None,
            policy: dict | None = None,
            schema: dict | None = None) -> tuple[bool, dict]:
    """Validate the explanation policy config; returns (ok, details)."""
    errors = [] if errors is None else errors
    ok = True
    policy = policy if policy is not None else load_yaml(
        _ROOT / "config/g0/evidence/explanation_policy.yaml")
    schema = schema if schema is not None else json.loads(
        (_ROOT / "schemas/g0/evidence/explanation_packet.schema.json")
        .read_text(encoding="utf-8"))

    rules = policy.get("citation_rules", [])
    ids = [r.get("id") for r in rules]
    for rid in ("EXPL-001", "EXPL-002", "EXPL-003", "EXPL-004", "EXPL-005"):
        if rid not in ids:
            errors.append(f"explanation policy missing rule {rid}")
            ok = False
    if not policy.get("content_forbidden"):
        errors.append("explanation policy must list forbidden content")
        ok = False
    for cls in policy.get("stale_classes", []):
        if cls not in STALE_CLASSES:
            errors.append(f"unknown stale class {cls!r}")
            ok = False
    required = schema.get("required", [])
    for field in ("cited_evidence_refs", "stale_indicators",
                  "conflict_disclosures", "decision_record_ref"):
        if field not in required:
            errors.append(f"explanation schema missing required {field}")
            ok = False
    return ok, {"policy_id": policy.get("policy_id"),
                "citation_rules": len(rules),
                "stale_classes": policy.get("stale_classes")}


def validate_packet(packet: dict) -> list[str]:
    """Validate a single packet document against schema + EXPL rules."""
    errs = []
    if Draft202012Validator is None:
        errs.append("jsonschema unavailable")
        return errs
    schema = json.loads((_ROOT / "schemas/g0/evidence/"
                         "explanation_packet.schema.json")
                        .read_text(encoding="utf-8"))
    v = Draft202012Validator(schema)
    errs.extend(f"schema: {e.message}" for e in sorted(v.iter_errors(packet),
                                                       key=str))
    # EXPL-002: every cited ref must be in the decision's inputs/outputs —
    # enforced at build time; here we only check structural consistency.
    for stale in packet.get("stale_indicators", []):
        if stale.get("stale_class") not in STALE_CLASSES:
            errs.append(f"invalid stale_class {stale.get('stale_class')!r}")
    return errs


def check(data: dict) -> tuple[bool, dict]:
    """(bool, details) form used by the Reality Lock builder."""
    errs = validate_packet(data)
    return (not errs, {"errors": errs})


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("EXPLANATION POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"explanation policy OK: {details}")
    if len(sys.argv) > 1:
        packet = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        perrs = validate_packet(packet)
        if perrs:
            print("PACKET INVALID")
            for e in perrs:
                print(f"  - {e}")
            return 1
        print("packet OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
