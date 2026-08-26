"""B4.C19 — Cold-restart reconstruction protocol (prototype).

Proves the system is not secretly dependent on hidden conversational state:
both Hermes roles rebuild from durable state alone, raw chat is never
required, and a recovery-quality metric compares pre/post-reset answers to a
standardized operational state query.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

# Standardized operational state query answered by each role after rebuild
STANDARD_QUERY = "current_operational_state"


@dataclass
class ReconstructionManifest:
    reconstruction_id: str
    role: str
    tenant_id: str
    project_id: str | None
    objects_used: list[str]
    excluded_objects: list[str]
    raw_chat_required: bool = False
    reconstructed_at: str = ""

    def to_dict(self) -> dict:
        return {
            "reconstruction_id": self.reconstruction_id,
            "role": self.role,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "objects_used": list(self.objects_used),
            "excluded_objects": list(self.excluded_objects),
            "raw_chat_required": self.raw_chat_required,
            "reconstructed_at": self.reconstructed_at,
        }


def reconstruct_personal(durable_state: dict) -> dict:
    """Personal Hermes cold restart.

    identity/user scope -> selected preferences/goals/open loops -> active
    organization/project summaries -> recent relevant episodic summary.
    """
    return {
        "role": "PERSONAL_HERMES",
        "user_scope": durable_state.get("user_scope"),
        "preferences": durable_state.get("preferences", []),
        "goals": durable_state.get("goals", []),
        "open_loops": durable_state.get("open_loops", []),
        "organization_summary": durable_state.get("organization_summary"),
        "episodic_summary": durable_state.get("episodic_summary"),
        "authority_state": durable_state.get("authority_state"),
        "ready": True,
    }


def reconstruct_ceo(durable_state: dict) -> dict:
    """CEO Hermes cold restart.

    ratified policy/capability refs -> active application/project state ->
    current intent/plan/task states -> active blockers -> promoted lessons.
    """
    return {
        "role": "CEO_HERMES",
        "policy_refs": durable_state.get("policy_refs", []),
        "project_id": durable_state.get("project_id"),
        "opportunity_revision_id": durable_state.get("opportunity_revision_id"),
        "intent_id": durable_state.get("intent_id"),
        "plan_id": durable_state.get("plan_id"),
        "task_statuses": durable_state.get("task_statuses", []),
        "active_blockers": durable_state.get("active_blockers", []),
        "promoted_lessons": durable_state.get("promoted_lessons", []),
        "unresolved_questions": durable_state.get("unresolved_questions", []),
        "authority_state": durable_state.get("authority_state"),
        "ready": True,
    }


def build_manifest(*, role: str, tenant_id: str, project_id: str | None,
                   objects_used: list[str],
                   excluded_objects: list[str] | None = None) -> ReconstructionManifest:
    if any("raw_chat" in o or "raw-chat" in o or "transcript" in o
           for o in objects_used):
        raise ValueError("reconstruction may not depend on raw chat objects")
    return ReconstructionManifest(
        reconstruction_id=f"recon-{abs(hash((role, tenant_id, project_id)))}",
        role=role, tenant_id=tenant_id, project_id=project_id,
        objects_used=list(objects_used), excluded_objects=list(excluded_objects or []),
        raw_chat_required=False,
        reconstructed_at=datetime.now(timezone.utc).isoformat(),
    )


def operational_state_answer(context: dict) -> dict:
    """Answer the standardized operational state query from reconstructed
    context. Used for the recovery-quality metric."""
    return {
        STANDARD_QUERY: {
            "tenant": context.get("user_scope") or context.get("project_id"),
            "opportunity_revision": context.get("opportunity_revision_id"),
            "intent": context.get("intent_id"),
            "task_statuses": context.get("task_statuses", []),
            "blockers": context.get("active_blockers", []),
            "unresolved_questions": context.get("unresolved_questions", []),
            "authority": context.get("authority_state"),
        }
    }


def recovery_quality(pre_reset: dict, post_reset: dict) -> dict:
    """Compare pre-reset vs post-reset answers to the standardized query.

    Material differences => fail/review. Exact match => full recovery.
    """
    pre = operational_state_answer(pre_reset)
    post = operational_state_answer(post_reset)
    differences = []
    pre_state = pre[STANDARD_QUERY]
    post_state = post[STANDARD_QUERY]
    for key in pre_state:
        if pre_state[key] != post_state[key]:
            differences.append(key)
    return {
        "metric": "operational_state_recovery",
        "match": not differences,
        "differences": differences,
        "pre": pre_state,
        "post": post_state,
    }
