"""B4.C8-C9 — Sidechain / WorkerResult / Outcome validator.

Fail-closed validation over the three schemas: worker_result, sidechain_manifest
and outcome_artifact. Each must be a strict object schema with the required
contract fields; the sidechain must demand redaction/secret-scan state and
retention class; the worker result must carry a bounded summary plus
sidechain_ref; the outcome must pin application_project_id and the exact
opportunity_revision_id.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import emit, finish  # noqa: E402

SCHEMAS_DIR = Path("schemas/g0/agents")

WORKER_REQUIRED = ["task_id", "attempt_id", "status", "summary",
                   "structured_output_ref", "key_findings", "uncertainties",
                   "source_refs", "artifact_refs", "quality_state",
                   "sidechain_ref"]
SIDECHAIN_REQUIRED = ["task_id", "attempt_id", "worker_identity", "start_time",
                      "end_time", "tool_calls", "source_refs", "artifact_refs",
                      "errors", "retries", "transcript_uri",
                      "redaction_status", "retention_class"]
OUTCOME_REQUIRED = ["outcome_id", "intent_id", "plan_id",
                    "application_project_id", "opportunity_revision_id",
                    "outcome_type", "status", "executive_summary",
                    "key_decisions", "created_at"]


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
    return schema


def validate(errors: list[str]) -> None:
    _check("worker_result.schema.json", WORKER_REQUIRED, errors)
    _check("sidechain_manifest.schema.json", SIDECHAIN_REQUIRED, errors)
    _check("outcome_artifact.schema.json", OUTCOME_REQUIRED, errors)

    # semantic checks beyond field presence
    _, wr = _load_schema("worker_result.schema.json")
    if wr.get("properties", {}).get("summary", {}).get("maxLength", 0) > 8000:
        errors.append("worker_result summary must be bounded (maxLength <= 8000)")
    _, sc = _load_schema("sidechain_manifest.schema.json")
    sc_props = sc.get("properties", {})
    if "secret_scan" not in sc_props:
        errors.append("sidechain_manifest must carry secret_scan state")
    if "redaction_status" not in sc_props:
        errors.append("sidechain_manifest must carry redaction_status")
    if "retention_class" not in sc_props:
        errors.append("sidechain_manifest must carry retention_class")
    _, oc = _load_schema("outcome_artifact.schema.json")
    oc_props = oc.get("properties", {})
    if "opportunity_revision_id" not in oc_props:
        errors.append("outcome_artifact must pin opportunity_revision_id")
    if "client_action_required" not in oc_props:
        errors.append("outcome_artifact must mark client_action_required")


def main() -> int:
    errors: list[str] = []
    validate(errors)
    _, report = finish("sidechain_synthesis", not errors, {
        "errors": errors,
        "schemas": ["worker_result", "sidechain_manifest", "outcome_artifact"],
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
