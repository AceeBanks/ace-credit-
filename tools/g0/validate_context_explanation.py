"""B4.C10-C11 — ContextBundle + ClientExplanationPacket validator.

Fail-closed validation over the two schemas and the context budget policy:
strict schemas with the plan-required fields, plus the policy's assembly
order, priority classes, never-inject list, anchor survival rule and
retrieval order.
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

EXPLANATION_REQUIRED = ["explanation_id", "outcome_id", "audience", "summary",
                        "what_we_found", "recommended_next_step",
                        "visible_research_refs", "visible_artifact_refs",
                        "uncertainty_disclosures"]
BUNDLE_REQUIRED = ["context_bundle_id", "consumer_actor", "operation_type",
                   "tenant_id", "project_id", "canonical_state_refs",
                   "evidence_refs", "memory_refs", "recent_interaction_refs",
                   "policy_refs", "task_refs", "anchors",
                   "excluded_context_classes", "assembled_at"]

EXPECTED_ASSEMBLY_ORDER = [
    "REQUIRED_CANONICAL_STATE", "REQUIRED_CURRENT_EVIDENCE",
    "ACTIVE_TASK_PROJECT_STATE", "MANDATORY_POLICY_CONSTRAINTS",
    "PROMOTED_ROLE_SPECIFIC_MEMORY", "SELECTED_RECENT_INTERACTION_CONTEXT",
    "OPTIONAL_SUPPORTING_HISTORY_WITHIN_BUDGET",
]
EXPECTED_PRIORITY_CLASSES = {"P0_MANDATORY", "P1_HIGH", "P2_SUPPORTING",
                             "P3_OPTIONAL"}
NEVER_INJECT = {"ENTIRE_USER_HISTORY", "ENTIRE_WORKER_TRACES",
                "CLOSED_PROJECT_TRANSCRIPTS", "RAW_SECRETS",
                "IRRELEVANT_APPLICATION_DOCUMENTS", "SUPERSEDED_MEMORY"}


def _load_schema(name: str) -> tuple[bool, dict]:
    path = SCHEMAS_DIR / name
    if not path.exists():
        return False, {"error": f"missing schema file {path}"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, {"error": f"{name} is not valid JSON: {exc}"}
    if data.get("type") != "object":
        return False, {"error": f"{name} must be an object schema"}
    if data.get("additionalProperties") is not False:
        return False, {"error": f"{name} must set additionalProperties=false"}
    return True, data


def _check(name: str, required: list[str], errors: list[str]) -> None:
    ok, schema = _load_schema(name)
    if not ok:
        errors.append(schema.get("error", f"{name} invalid"))
        return
    props = set(schema.get("properties", {}))
    missing = [r for r in required if r not in props]
    if missing:
        errors.append(f"{name}: missing properties {missing}")
    missing_req = [r for r in required
                   if r not in set(schema.get("required", []))]
    if missing_req:
        errors.append(f"{name}: missing required fields {missing_req}")


def validate_context_budget_policy(errors: list[str]) -> None:
    try:
        data = load_yaml(AGENTS_CONFIG_DIR / "context_budget_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    if data.get("assembly_order") != EXPECTED_ASSEMBLY_ORDER:
        errors.append("assembly_order must be exactly the seven-stage order")
    classes = set(data.get("priority_classes", {}))
    if classes != EXPECTED_PRIORITY_CLASSES:
        errors.append(f"priority_classes must be {sorted(EXPECTED_PRIORITY_CLASSES)}")
    never = set(data.get("never_default_inject", []))
    missing = NEVER_INJECT - never
    if missing:
        errors.append(f"never_default_inject missing: {sorted(missing)}")
    anchor = data.get("anchor_policy", {})
    if anchor.get("mandatory_anchors_survive") != "ALWAYS":
        errors.append("anchor_policy.mandatory_anchors_survive must be ALWAYS")
    if anchor.get("violation") != "ASSEMBLY_ERROR":
        errors.append("anchor_policy.violation must be ASSEMBLY_ERROR")
    retrieval = data.get("retrieval_order", [])
    if "EXACT_REQUIRED_REFS" not in retrieval:
        errors.append("retrieval_order must prefer EXACT_REQUIRED_REFS")
    if "RECENCY_AS_TIEBREAKER_ONLY" not in retrieval:
        errors.append("recency must be a tiebreaker only, never primary truth")


def main() -> int:
    errors: list[str] = []
    _check("client_explanation_packet.schema.json", EXPLANATION_REQUIRED,
           errors)
    _check("context_bundle.schema.json", BUNDLE_REQUIRED, errors)
    validate_context_budget_policy(errors)
    _, report = finish("context_explanation", not errors, {
        "errors": errors,
        "schemas": ["client_explanation_packet", "context_bundle"],
        "policy": "context_budget_policy.yaml",
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
