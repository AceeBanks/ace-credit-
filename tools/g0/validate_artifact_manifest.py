"""B0.C1 validator — R0/G0 artifact manifest.

Fail-closed checks:
- required file exists and parses;
- unique artifact IDs and unique paths;
- every artifact has version/status/authority_class/created_or_observed_at;
- authority_class is a declared class; status is a known enum;
- every referenced path exists in the repository;
- recorded blob_sha matches current file content (stale-authority drift detection);
- supersession graph (supersedes / superseded_by) is acyclic and consistent.
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
    blob_sha,
    cli_main,
    finish,
    load_yaml,
    require,
    require_field,
)

KNOWN_STATUS = {"active", "superseded", "withdrawn", "archived"}


def validate(config_path) -> tuple[bool, dict]:
    errors: list[str] = []
    # Accept either a config path or an already-loaded mapping for test fixtures.
    data = config_path if isinstance(config_path, dict) else load_yaml(config_path)

    require(isinstance(data, dict), errors, "manifest must be a mapping")
    if not isinstance(data, dict):
        raise ValidationFailure("artifact manifest root is not a mapping")

    classes = data.get("authority_classes")
    require(isinstance(classes, list) and len(classes) >= 5, errors,
            "authority_classes must be a non-trivial list")

    artifacts = data.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, errors,
            "artifacts must be a non-empty list")
    if not isinstance(artifacts, list):
        raise ValidationFailure("artifact manifest has no artifact list")

    seen_ids: dict[str, int] = {}
    seen_paths: set[str] = set()
    by_id: dict[str, dict] = {}
    stale: list[str] = []

    for i, art in enumerate(artifacts):
        ctx = f"artifact[{i}]"
        require(isinstance(art, dict), errors, f"{ctx}: entry must be a mapping")
        if not isinstance(art, dict):
            continue
        aid = art.get("artifact_id")
        for field in ("artifact_id", "path", "version", "status",
                      "authority_class", "created_or_observed_at"):
            require_field(art, field, errors, f"{ctx} {aid or '?'}")

        if aid:
            if aid in seen_ids:
                errors.append(f"duplicate artifact_id '{aid}' "
                              f"(entries {seen_ids[aid]} and {i})")
            else:
                seen_ids[aid] = i
                by_id[aid] = art
            if isinstance(classes, list) and art.get("authority_class") not in classes:
                errors.append(f"{aid}: unknown authority_class "
                              f"'{art.get('authority_class')}'")
            if art.get("status") not in KNOWN_STATUS:
                errors.append(f"{aid}: unknown status '{art.get('status')}'")

        rel = art.get("path")
        if isinstance(rel, str) and rel:
            if rel in seen_paths:
                errors.append(f"duplicate path '{rel}'")
            seen_paths.add(rel)
            abs_path = REPO_ROOT / rel
            if not abs_path.exists():
                errors.append(f"{aid}: referenced artifact does not exist: {rel}")
            elif art.get("blob_sha"):
                actual = blob_sha(abs_path)
                if actual != art["blob_sha"]:
                    stale.append(rel)
                    errors.append(
                        f"{aid}: content drift — recorded blob_sha does not match "
                        f"current file ({rel}). Artifact changed after manifest pinning.")

    # supersession consistency + cycle detection
    for aid, art in by_id.items():
        sup_by = art.get("superseded_by")
        supersedes = art.get("supersedes") or []
        if sup_by and sup_by not in by_id:
            errors.append(f"{aid}: superseded_by unknown artifact '{sup_by}'")
        for s in supersedes:
            if s not in by_id:
                errors.append(f"{aid}: supersedes unknown artifact '{s}'")

    # iterative walk of the superseded_by chain per artifact
    cycles = []
    for aid in by_id:
        visited: set[str] = set()
        cur = aid
        while True:
            art = by_id.get(cur)
            nxt = art.get("superseded_by") if art else None
            if not nxt or nxt not in by_id:
                break
            if nxt == aid or nxt in visited:
                cycles.append(f"{aid}->{nxt}")
                break
            visited.add(cur)
            cur = nxt

    if cycles:
        errors.append(f"supersession cycle detected: {cycles}")

    if stale:
        errors.append(
            f"stale authority detected: {len(stale)} pinned artifact(s) changed "
            f"after manifest pinning")

    ok = not errors
    report = {
        "artifact_count": len(artifacts),
        "unique_ids": len(seen_ids),
        "authority_class_counts": _tally(artifacts, "authority_class"),
        "stale_content": stale,
        "supersession_cycles": cycles,
        "errors": errors,
    }
    return finish("validate_artifact_manifest", ok, report)


def _tally(items: list, key: str) -> dict:
    out: dict[str, int] = {}
    for it in items:
        if isinstance(it, dict) and key in it:
            out[str(it[key])] = out.get(str(it[key]), 0) + 1
    return out


if __name__ == "__main__":
    import sys
    sys.exit(cli_main(validate, RATIFICATION_CONFIG_DIR / "artifact_manifest.yaml"))
