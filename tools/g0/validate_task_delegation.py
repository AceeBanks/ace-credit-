"""B4.C6-C7 — TaskPlan / TaskContract delegation validator.

Fail-closed validation over:

  * schemas/g0/agents/task_plan.schema.json and task_contract.schema.json:
    strict object schemas with the plan-required fields;
  * config/g0/agents/worker_context_policy.yaml: refs-only context
    minimization, the five never-inject classes, stateless default, scratch
    retention and denied unlisted ref access.
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

PLAN_REQUIRED = ["plan_id", "intent_id", "objective", "steps", "dependencies",
                 "required_capabilities", "created_by", "version"]
CONTRACT_REQUIRED = ["task_id", "plan_id", "tenant_id", "project_id",
                     "worker_role", "objective", "capability_id",
                     "inputs_refs", "allowed_context_refs", "required_outputs",
                     "authority_scope", "side_effect_policy", "expires_at"]
NEVER_INJECT = {"FULL_CEO_PROMPT_HISTORY", "RAW_CLIENT_TRANSCRIPT",
                "OTHER_TASK_SCRATCH", "RAW_SECRETS", "CLOSED_PROJECT_CHATTER"}


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


def _check_schema(name: str, required: list[str], errors: list[str]) -> None:
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


def validate_worker_context_policy(errors: list[str]) -> None:
    try:
        data = load_yaml(AGENTS_CONFIG_DIR / "worker_context_policy.yaml")
    except ValidationFailure as exc:
        errors.append(str(exc))
        return
    if data.get("context_minimization") != "REFS_AND_BOUNDED_EXTRACTS_ONLY":
        errors.append("context_minimization must be "
                      "REFS_AND_BOUNDED_EXTRACTS_ONLY")
    never = set(data.get("never_inject", []))
    missing = NEVER_INJECT - never
    if missing:
        errors.append(f"never_inject missing: {sorted(missing)}")
    if data.get("worker_memory_default") != "STATELESS_ACROSS_TASKS":
        errors.append("worker_memory_default must be STATELESS_ACROSS_TASKS")
    if not data.get("persistent_worker_memory_rule"):
        errors.append("persistent_worker_memory_rule must be declared")
    if data.get("scratch_retention") != "EXPIRES_AFTER_CONFIGURED_RETENTION":
        errors.append("scratch_retention must be "
                      "EXPIRES_AFTER_CONFIGURED_RETENTION")
    ref_policy = data.get("context_ref_policy", {})
    if ref_policy.get("unlisted_ref_access") != "DENIED":
        errors.append("context_ref_policy.unlisted_ref_access must be DENIED")


def main() -> int:
    errors: list[str] = []
    _check_schema("task_plan.schema.json", PLAN_REQUIRED, errors)
    _check_schema("task_contract.schema.json", CONTRACT_REQUIRED, errors)
    validate_worker_context_policy(errors)
    _, report = finish("task_delegation", not errors, {
        "errors": errors,
        "schemas": ["task_plan", "task_contract"],
        "policy": "worker_context_policy.yaml",
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
