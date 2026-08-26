"""B4.C19 — Cold-restart reconstruction tests.

Proves the system is not secretly dependent on hidden conversational state:
deleting/resetting both Hermes runtime contexts and rebuilding from durable
state still yields client organization, active intent/project, current
opportunity revision, task status, unresolved questions, relevant preferences
and authority state — without archived raw chat. Recovery-quality metric
compares pre/post-reset answers to a standardized operational query.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.reconstruction import (  # noqa: E402
    build_manifest,
    operational_state_answer,
    reconstruct_ceo,
    reconstruct_personal,
    recovery_quality,
)


def _personal_durable() -> dict:
    return {
        "user_scope": "user-7@tenant-georgia-youth",
        "preferences": ["prefers concise explanations",
                        "wants drafts surfaced before full package"],
        "goals": ["fund after-school program"],
        "open_loops": ["partnership letter still required"],
        "organization_summary": "After-School Youth Collective, Atlanta GA",
        "episodic_summary": "brainstormed program name with client",
        "authority_state": "L1",
    }


def _ceo_durable() -> dict:
    return {
        "policy_refs": ["policy:capability-summary"],
        "project_id": "proj-after-school",
        "opportunity_revision_id": "opp-rev-3",
        "intent_id": "int-1",
        "plan_id": "plan-1",
        "task_statuses": ["task:research-a SUCCEEDED",
                          "task:draft-a IN_PROGRESS"],
        "active_blockers": ["partnership letter missing"],
        "promoted_lessons": ["georgia source X needs browser fallback"],
        "unresolved_questions": ["pilot vs permanent program?"],
        "authority_state": "L2",
    }


def test_personal_cold_restart_reconstructs():
    context = reconstruct_personal(_personal_durable())
    assert context["ready"] is True
    assert context["user_scope"] == "user-7@tenant-georgia-youth"
    assert "prefers concise explanations" in context["preferences"]
    assert context["authority_state"] == "L1"
    assert context["organization_summary"]


def test_ceo_cold_restart_reconstructs():
    context = reconstruct_ceo(_ceo_durable())
    assert context["ready"] is True
    assert context["opportunity_revision_id"] == "opp-rev-3"
    assert context["intent_id"] == "int-1"
    assert context["plan_id"] == "plan-1"
    assert "task:draft-a IN_PROGRESS" in context["task_statuses"]
    assert "partnership letter missing" in context["active_blockers"]
    assert context["authority_state"] == "L2"


def test_reconstruction_does_not_require_raw_chat():
    manifest = build_manifest(
        role="CEO_HERMES", tenant_id="tenant-georgia-youth",
        project_id="proj-after-school",
        objects_used=["intent:int-1", "plan:plan-1",
                      "state:opp-rev-3", "task:research-a"],
        excluded_objects=["conv/archived-session-2024"])
    assert manifest.raw_chat_required is False
    assert "conv/archived-session-2024" in manifest.excluded_objects
    # raw chat in objects_used is refused
    with pytest.raises(ValueError, match="raw chat"):
        build_manifest(role="CEO_HERMES", tenant_id="t", project_id="p",
                       objects_used=["conv/raw-chat-1"])


def test_recovery_quality_exact_match():
    pre = reconstruct_ceo(_ceo_durable())
    post = reconstruct_ceo(_ceo_durable())
    metric = recovery_quality(pre, post)
    assert metric["match"] is True
    assert metric["differences"] == []


def test_recovery_quality_detects_material_difference():
    pre = reconstruct_ceo(_ceo_durable())
    drifted = dict(_ceo_durable())
    drifted["opportunity_revision_id"] = "opp-rev-9"  # wrong revision
    post = reconstruct_ceo(drifted)
    metric = recovery_quality(pre, post)
    assert metric["match"] is False
    assert "opportunity_revision" in metric["differences"]


def test_standard_query_covers_all_required_state():
    context = reconstruct_ceo(_ceo_durable())
    answer = operational_state_answer(context)
    state = answer["current_operational_state"]
    # the system must still know organization, revision, tasks, questions,
    # authority after rebuild
    assert "opportunity_revision" in state
    assert "task_statuses" in state
    assert "unresolved_questions" in state
    assert "authority" in state


def test_manifest_schema_is_strict():
    from tools.g0.validate_compaction_reconstruction import (
        validate_reconstruction_schema)
    errors: list[str] = []
    validate_reconstruction_schema(errors)
    assert errors == []


def test_manifest_raw_chat_required_false_in_schema():
    import json
    schema = json.loads(
        (Path(__file__).parents[3] / "schemas/g0/agents"
         / "reconstruction_manifest.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["raw_chat_required"]["const"] is False
    assert "objects_used" in schema["required"]
