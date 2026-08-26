"""B0.C2 validator — R0 decision register.

Fail-closed checks:
- required file exists and parses;
- unique decision IDs;
- every decision has a known primary status and a known category;
- statement / rationale / implementation_implications / affected_books present;
- every decision cites at least one source artifact AND every cited artifact ID
  resolves to the pinned artifact manifest (no phantom lineage);
- RATIFIED_WITH_CONDITION decisions must carry explicit conditions;
- supersedes_decision_id references are consistent and acyclic;
- every declared required category is covered by at least one decision.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (
    REPO_ROOT,
    RATIFICATION_CONFIG_DIR,
    ValidationFailure,
    cli_main,
    finish,
    load_yaml,
    require,
    require_field,
)


def _artifact_ids() -> set[str]:
    data = load_yaml(RATIFICATION_CONFIG_DIR / "artifact_manifest.yaml")
    ids = {a.get("artifact_id") for a in data.get("artifacts", []) if isinstance(a, dict)}
    return {i for i in ids if i}


def validate(config_path) -> tuple[bool, dict]:
    errors: list[str] = []
    # Accept either a config path or an already-loaded mapping so tests can
    # inject mutated fixtures without touching disk.
    data = config_path if isinstance(config_path, dict) else load_yaml(config_path)

    require(isinstance(data, dict), errors, "decision register must be a mapping")
    if not isinstance(data, dict):
        raise ValidationFailure("decision register root is not a mapping")

    required_categories = data.get("required_categories") or []
    valid_statuses = set(data.get("valid_statuses") or [])
    require(bool(required_categories), errors, "required_categories must be declared")
    require(bool(valid_statuses), errors, "valid_statuses must be declared")

    decisions = data.get("decisions")
    require(isinstance(decisions, list) and decisions, errors,
            "decisions must be a non-empty list")
    if not isinstance(decisions, list):
        raise ValidationFailure("decision register has no decisions list")

    known_artifacts = _artifact_ids()
    require(bool(known_artifacts), errors,
            "artifact manifest resolved to zero artifacts — cannot verify lineage")

    seen: dict[str, int] = {}
    by_id: dict[str, dict] = {}
    covered_categories: set[str] = set()
    status_counts: dict[str, int] = {}

    for i, dec in enumerate(decisions):
        ctx = f"decision[{i}]"
        require(isinstance(dec, dict), errors, f"{ctx}: entry must be a mapping")
        if not isinstance(dec, dict):
            continue
        did = dec.get("decision_id")
        for field in ("decision_id", "title", "status", "category", "statement",
                      "rationale", "source_artifact_ids", "conditions",
                      "affected_books", "implementation_implications"):
            require_field(dec, field, errors, f"{ctx} {did or '?'}")

        if did:
            if did in seen:
                errors.append(f"duplicate decision_id '{did}' "
                              f"(entries {seen[did]} and {i})")
            else:
                seen[did] = i
                by_id[did] = dec
            status = dec.get("status")
            if status not in valid_statuses:
                errors.append(f"{did}: unknown status {status!r}")
            else:
                status_counts[status] = status_counts.get(status, 0) + 1
            category = dec.get("category")
            if isinstance(category, str) and category.strip():
                covered_categories.add(category)
                if required_categories and category not in required_categories:
                    errors.append(f"{did}: category {category!r} is not in the "
                                  f"declared required_categories")
            elif did:
                errors.append(f"{did}: missing or empty 'category'")

        sources = dec.get("source_artifact_ids")
        if isinstance(sources, list) and sources:
            for sid in sources:
                if sid not in known_artifacts:
                    errors.append(f"{did}: source_artifact_id '{sid}' does not "
                                  f"resolve to the artifact manifest (phantom lineage)")
        else:
            errors.append(f"{did}: no source artifacts cited — claims without evidence")

        conditions = dec.get("conditions")
        if dec.get("status") == "RATIFIED_WITH_CONDITION" and \
                (not isinstance(conditions, list) or not conditions):
            errors.append(f"{did}: RATIFIED_WITH_CONDITION requires at least one condition")

        sup = dec.get("supersedes_decision_id")
        if sup and isinstance(sup, str) and sup not in {d.get("decision_id") for d in decisions if isinstance(d, dict)}:
            errors.append(f"{did}: supersedes unknown decision '{sup}'")

    # supersession cycle detection (iterative)
    cycles: list[str] = []
    for did in by_id:
        visited: set[str] = set()
        cur = did
        while True:
            nxt = by_id[cur].get("supersedes_decision_id") if cur in by_id else None
            if not nxt or nxt not in by_id:
                break
            if nxt == did or nxt in visited:
                cycles.append(f"{did}->{nxt}")
                break
            visited.add(cur)
            cur = nxt
    if cycles:
        errors.append(f"supersession cycle detected: {cycles}")

    missing_categories = [c for c in required_categories if c not in covered_categories]
    if missing_categories:
        errors.append(f"coverage failure — required categories with no decision: {missing_categories}")

    ok = not errors
    report = {
        "decision_count": len(decisions),
        "unique_ids": len(seen),
        "status_counts": status_counts,
        "categories_covered": sorted(covered_categories),
        "missing_categories": missing_categories,
        "phantom_source_ids": [],
        "supersession_cycles": cycles,
        "errors": errors,
    }
    return finish("validate_decision_register", ok, report)


if __name__ == "__main__":
    sys.exit(cli_main(validate, RATIFICATION_CONFIG_DIR / "decision_register.yaml"))
