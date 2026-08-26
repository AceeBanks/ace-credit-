"""B0.C3 validator — contradiction & drift ledger.

Fail-closed checks:
- required file exists and parses;
- unique contradiction IDs;
- known severity (P0|P1|P2) and status (OPEN|RESOLVED);
- claims, sources, resolution, and resolution authority present;
- every cited source artifact resolves to the pinned artifact manifest;
- every affected decision resolves to the decision register (no phantom links);
- GATE: zero unresolved P0 contradictions — an OPEN P0 fails validation.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (
    RATIFICATION_CONFIG_DIR,
    ValidationFailure,
    cli_main,
    finish,
    load_yaml,
    require,
    require_field,
)


def _decision_ids() -> set[str]:
    data = load_yaml(RATIFICATION_CONFIG_DIR / "decision_register.yaml")
    return {d.get("decision_id") for d in data.get("decisions", []) if isinstance(d, dict)}


def _artifact_ids() -> set[str]:
    data = load_yaml(RATIFICATION_CONFIG_DIR / "artifact_manifest.yaml")
    return {a.get("artifact_id") for a in data.get("artifacts", []) if isinstance(a, dict)}


def validate(config_path) -> tuple[bool, dict]:
    errors: list[str] = []
    data = config_path if isinstance(config_path, dict) else load_yaml(config_path)

    require(isinstance(data, dict), errors, "contradiction ledger must be a mapping")
    if not isinstance(data, dict):
        raise ValidationFailure("contradiction ledger root is not a mapping")

    severities = set(data.get("valid_severities") or [])
    statuses = set(data.get("valid_statuses") or [])
    contradictions = data.get("contradictions")
    require(isinstance(contradictions, list) and contradictions, errors,
            "contradictions must be a non-empty list")
    if not isinstance(contradictions, list):
        raise ValidationFailure("ledger has no contradictions list")

    known_artifacts = _artifact_ids()
    known_decisions = _decision_ids()

    seen: set[str] = set()
    open_p0: list[str] = []
    open_p1_p2: list[str] = []
    severity_counts: dict[str, int] = {}

    for i, c in enumerate(contradictions):
        ctx = f"contradiction[{i}]"
        require(isinstance(c, dict), errors, f"{ctx}: entry must be a mapping")
        if not isinstance(c, dict):
            continue
        cid = c.get("contradiction_id")
        for field in ("contradiction_id", "title", "severity", "status",
                      "claim_a", "claim_b", "source_a", "source_b",
                      "resolution", "resolution_authority"):
            require_field(c, field, errors, f"{ctx} {cid or '?'}")

        if not cid or cid in seen:
            if cid:
                errors.append(f"duplicate contradiction_id '{cid}'")
            continue
        seen.add(cid)

        sev = c.get("severity")
        if sev not in severities:
            errors.append(f"{cid}: unknown severity {sev!r}")
        else:
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        status = c.get("status")
        if status not in statuses:
            errors.append(f"{cid}: unknown status {status!r}")

        for side in ("source_a", "source_b"):
            sources = c.get(side)
            if isinstance(sources, list) and sources:
                for sid in sources:
                    if sid not in known_artifacts:
                        errors.append(f"{cid}: {side} id '{sid}' does not resolve "
                                      f"to the artifact manifest")
            else:
                errors.append(f"{cid}: {side} cites no artifacts — unanchored claim")

        affected = c.get("affected_decisions") or []
        for did in affected:
            if did not in known_decisions:
                errors.append(f"{cid}: affected_decision '{did}' does not exist "
                              f"in the decision register")

        resolved_via_decision = bool(affected)
        if status == "OPEN" and sev == "P0":
            open_p0.append(cid)

    # The Book 0 gate: zero unresolved P0. Open P1/P2 are permitted but visible.
    if open_p0:
        errors.append(f"GATE VIOLATION — unresolved P0 contradictions remain: {open_p0}")

    ok = not errors
    report = {
        "contradiction_count": len(contradictions),
        "unique_ids": len(seen),
        "severity_counts": severity_counts,
        "open_p0": open_p0,
        "open_p1_p2": open_p1_p2,
        "errors": errors,
    }
    return finish("validate_contradictions", ok, report)


if __name__ == "__main__":
    sys.exit(cli_main(validate, RATIFICATION_CONFIG_DIR / "contradiction_ledger.yaml"))
