"""B0.C4/C5 validators — non-goal freeze + prototype candidate register.

Fail-closed checks:
- unique IDs; known kinds/statuses; required coverage lists satisfied;
- every rationale present and non-trivial;
- lineage: source artifact IDs resolve to the pinned manifest;
  affected decision IDs resolve to the decision register (C4) / candidate
  cross-references resolve (C5);
- C5 GATE: no candidate may be ADOPTED at Book 0 — adoption without the
  responsible book's evidence gate is a hard failure.
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


def _artifact_ids() -> set[str]:
    data = load_yaml(RATIFICATION_CONFIG_DIR / "artifact_manifest.yaml")
    return {a.get("artifact_id") for a in data.get("artifacts", []) if isinstance(a, dict)}


def _decision_ids() -> set[str]:
    data = load_yaml(RATIFICATION_CONFIG_DIR / "decision_register.yaml")
    return {d.get("decision_id") for d in data.get("decisions", []) if isinstance(d, dict)}


def validate_non_goals(config_path) -> tuple[bool, dict]:
    errors: list[str] = []
    data = config_path if isinstance(config_path, dict) else load_yaml(config_path)

    require(isinstance(data, dict), errors, "non_goals must be a mapping")
    if not isinstance(data, dict):
        raise ValidationFailure("non-goals root is not a mapping")

    kinds = set(data.get("valid_kinds") or [])
    items = data.get("non_goals")
    require(isinstance(items, list) and items, errors, "non_goals list must be non-empty")
    if not isinstance(items, list):
        raise ValidationFailure("non-goals has no list")

    known_artifacts = _artifact_ids()
    known_decisions = _decision_ids()
    seen_kinds: set[str] = set()

    for i, ng in enumerate(items):
        ctx = f"non_goal[{i}]"
        if not isinstance(ng, dict):
            errors.append(f"{ctx}: entry must be a mapping")
            continue
        nid = ng.get("non_goal_id")
        for field in ("non_goal_id", "title", "kind", "rationale"):
            require_field(ng, field, errors, f"{ctx} {nid or '?'}")
        kind = ng.get("kind")
        if kind not in kinds:
            errors.append(f"{nid}: unknown kind {kind!r}")
        else:
            seen_kinds.add(kind)
        sources = ng.get("source_artifact_ids") or []
        for sid in sources:
            if sid not in known_artifacts:
                errors.append(f"{nid}: phantom source artifact '{sid}'")
        for did in ng.get("affected_decisions") or []:
            if did not in known_decisions:
                errors.append(f"{nid}: phantom affected decision '{did}'")

    missing_kinds = sorted(kinds - seen_kinds)
    if missing_kinds:
        errors.append(f"no non-goal of kind(s): {missing_kinds}")

    ok = not errors
    report = {
        "non_goal_count": len(items),
        "kinds_present": sorted(seen_kinds),
        "errors": errors,
    }
    return finish("validate_non_goals", ok, report)


def validate_candidates(config_path) -> tuple[bool, dict]:
    errors: list[str] = []
    data = config_path if isinstance(config_path, dict) else load_yaml(config_path)

    require(isinstance(data, dict), errors, "candidate register must be a mapping")
    if not isinstance(data, dict):
        raise ValidationFailure("candidate register root is not a mapping")

    statuses = set(data.get("valid_statuses") or [])
    required_ids = set(data.get("required_candidate_ids") or [])
    candidates = data.get("candidates")
    require(isinstance(candidates, list) and candidates, errors,
            "candidates must be a non-empty list")
    if not isinstance(candidates, list):
        raise ValidationFailure("candidate register has no list")

    known_artifacts = _artifact_ids()
    known_decisions = _decision_ids()
    seen_ids: set[str] = set()
    fields = ("candidate_id", "capability_gap", "hypothesis", "baseline",
              "success_metrics", "kill_criteria", "license_status",
              "security_notes", "responsible_book", "status")

    adopted: list[str] = []
    for i, cand in enumerate(candidates):
        ctx = f"candidate[{i}]"
        if not isinstance(cand, dict):
            errors.append(f"{ctx}: entry must be a mapping")
            continue
        cid = cand.get("candidate_id")
        if cid:
            if cid in seen_ids:
                errors.append(f"duplicate candidate_id '{cid}'")
            else:
                seen_ids.add(cid)
        for field in fields:
            require_field(cand, field, errors, f"{ctx} {cid or '?'}")
        status = cand.get("status")
        if status not in statuses:
            errors.append(f"{cid}: unknown status {status!r}")
        if status == "adopted_with_evidence":
            adopted.append(cid)
        sources = cand.get("source_artifact_ids") or []
        for sid in sources:
            if sid not in known_artifacts:
                errors.append(f"{cid}: phantom source artifact '{sid}'")
        for did in cand.get("affected_decisions") or []:
            if did not in known_decisions:
                errors.append(f"{cid}: phantom affected decision '{did}'")

    missing_required = sorted(required_ids - seen_ids)
    if missing_required:
        errors.append(f"missing mandated candidates: {missing_required}")
    if adopted:
        errors.append(f"GATE VIOLATION — candidates ADOPTED at Book 0 without "
                      f"responsible-book evidence gate: {adopted}")

    ok = not errors
    report = {
        "candidate_count": len(candidates),
        "unique_ids": len(seen_ids),
        "adopted_at_book0": adopted,
        "errors": errors,
    }
    return finish("validate_prototype_candidates", ok, report)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a in ("non_goals", "candidates", "both")]
    which = args[0] if args else "both"
    # Drop the selector so cli_main sees only an optional config path.
    if args:
        sys.argv.remove(args[0])
    code = 0
    if which in ("non_goals", "both"):
        code |= cli_main(validate_non_goals, RATIFICATION_CONFIG_DIR / "non_goals.yaml")
    if which in ("candidates", "both"):
        code |= cli_main(validate_candidates, RATIFICATION_CONFIG_DIR / "prototype_candidates.yaml")
    sys.exit(code)
