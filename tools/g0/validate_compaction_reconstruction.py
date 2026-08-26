"""B4.C17-C19 — Compaction + reconstruction validator.

Fail-closed validation over:

  * config/g0/agents/compaction_policy.yaml: the six stages in order, the
    eleven mandatory anchors, the four COMPACT rules, manifest fields;
  * schemas/g0/agents/reconstruction_manifest.schema.json: strict schema with
    the plan-required fields and raw_chat_required=false.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    ValidationFailure,
    emit,
    finish,
    load_yaml,
)

AGENTS_CONFIG_DIR = Path("config/g0/agents")
SCHEMAS_DIR = Path("schemas/g0/agents")

EXPECTED_STAGES = [
    "STAGE0_NO_COMPACTION", "STAGE1_DROP_DISPOSABLE_REDUNDANT",
    "STAGE2_SNIP_HISTORICAL_LOW_VALUE", "STAGE3_MICRO_SUMMARIZE_EPISODES_TASKS",
    "STAGE4_COLLAPSE_INACTIVE_PROJECT_CONTEXT",
    "STAGE5_MODEL_ASSISTED_SEMANTIC_COMPACTION",
]
EXPECTED_ANCHORS = {
    "TENANT_USER_IDENTITY_REFS", "ACTIVE_INTENT_OBJECTIVE", "AUTHORITY_SCOPE",
    "EXACT_ACTIVE_OPPORTUNITY_REVISION", "UNRESOLVED_CRITICAL_CLARIFICATION",
    "ELIGIBILITY_STATE", "DEADLINE_CRITICAL_STATE", "ACTIVE_BLOCKERS",
    "HUMAN_APPROVALS_DENIALS", "SOURCE_EVIDENCE_REFS_FOR_CURRENT_TASK",
    "SAFETY_SECURITY_CONSTRAINTS",
}
REQUIRED_COMPACT_RULES = {f"COMPACT-{n:03d}" for n in range(1, 5)}
MANIFEST_FIELDS = {"REMOVED_ITEMS", "SUMMARIZED_ITEMS", "ANCHORS_RETAINED",
                   "SUMMARY_GENERATOR_VERSION", "SOURCE_REFS",
                   "BEFORE_AFTER_BUDGET"}
RECONSTRUCTION_REQUIRED = ["reconstruction_id", "role", "tenant_id",
                           "project_id", "objects_used", "excluded_objects",
                           "raw_chat_required", "reconstructed_at"]


def validate_compaction_policy(errors: list[str],
                               cfg: dict | None = None) -> None:
    try:
        data = cfg if cfg is not None else load_yaml(
            AGENTS_CONFIG_DIR / "compaction_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    if data.get("stages") != EXPECTED_STAGES:
        errors.append("stages must be the six compaction stages in order")
    anchors = set(data.get("mandatory_anchors", []))
    missing = EXPECTED_ANCHORS - anchors
    if missing:
        errors.append(f"mandatory_anchors missing: {sorted(missing)}")
    unknown = anchors - EXPECTED_ANCHORS
    if unknown:
        errors.append(f"mandatory_anchors unknown: {sorted(unknown)}")
    rules = data.get("rules", [])
    seen: set[str] = set()
    for rule in rules:
        rid = rule.get("rule_id")
        if not rid:
            errors.append("compaction rule missing rule_id")
            continue
        if rid in seen:
            errors.append(f"{rid}: duplicate rule id")
        seen.add(rid)
    if seen != REQUIRED_COMPACT_RULES:
        errors.append(f"compaction rules must be exactly "
                      f"{sorted(REQUIRED_COMPACT_RULES)}; got {sorted(seen)}")
    manifest = set(data.get("manifest_fields", []))
    missing_fields = MANIFEST_FIELDS - manifest
    if missing_fields:
        errors.append(f"manifest_fields missing: {sorted(missing_fields)}")


def validate_reconstruction_schema(errors: list[str]) -> None:
    path = SCHEMAS_DIR / "reconstruction_manifest.schema.json"
    if not path.exists():
        errors.append(f"missing schema file {path}")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"reconstruction_manifest.schema.json invalid: {exc}")
        return
    if data.get("type") != "object":
        errors.append("reconstruction_manifest must be an object schema")
    if data.get("additionalProperties") is not False:
        errors.append("reconstruction_manifest must set "
                      "additionalProperties=false")
    props = set(data.get("properties", {}))
    missing = [r for r in RECONSTRUCTION_REQUIRED if r not in props]
    if missing:
        errors.append(f"reconstruction_manifest missing properties {missing}")
    missing_req = [r for r in RECONSTRUCTION_REQUIRED
                   if r not in set(data.get("required", []))]
    if missing_req:
        errors.append(f"reconstruction_manifest missing required {missing_req}")
    if data.get("properties", {}).get("raw_chat_required", {}).get("const") \
            is not False:
        errors.append("reconstruction_manifest raw_chat_required must be "
                      "const false")


def main() -> int:
    errors: list[str] = []
    validate_compaction_policy(errors)
    validate_reconstruction_schema(errors)
    _, report = finish("compaction_reconstruction", not errors, {
        "errors": errors,
        "policy": "compaction_policy.yaml",
        "schema": "reconstruction_manifest.schema.json",
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
