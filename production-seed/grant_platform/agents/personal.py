"""G1 Wave 3 — Personal Hermes runtime adapter.

Client relationship owner. A chat message is persisted as a message, then
reduced to a governed IntentContract (intent_type / authority_scope /
objective) which is persisted in the intents table. Personal Hermes does
NOT execute operational tools — it hands the IntentContract to CEO Hermes.

Promoted from G0 (`prototype/g0/agents/intent_builder.py`): the production
adapter keeps the same contract semantics (ASSERTION labeling, submission
capability normalization to prepare-only) and adds durable persistence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from grant_platform.store.db import Store

SUBMISSION_CAPABILITIES = {
    "submission.prepare", "submission.execute", "submission.certify",
    "submission.sign", "application.submit",
}
PREPARE_ONLY_TARGET = "application.prepare_submission_package"

INTENT_TYPES = {
    "EXPLORE_IDEA", "FIND_GRANTS", "ASSESS_OPPORTUNITY", "BUILD_APPLICATION",
    "UPDATE_PROFILE", "REVIEW_DRAFT", "RESEARCH_FUNDER", "RESEARCH_WINNERS",
    "EXPLAIN_RESULT", "OTHER_CONTROLLED_EXTENSION",
}
AUTHORITY_SCOPES = {"EXPLORE_ONLY", "RESEARCH_ONLY",
                    "RESEARCH_AND_DRAFT_ONLY", "PREPARE_ONLY"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classify_intent_type(message: str) -> str:
    """Deterministic intent-type classification over the client message.

    Never a model call: intent type is a governed structural field, not
    model prose (Book 8 C34 deterministic-first rule applied to intake).
    """
    text = message.lower()
    if any(w in text for w in ("eligible", "qualify", "can we apply")):
        return "ASSESS_OPPORTUNITY"
    if ("need funding" in text or "funding for" in text
            or any(w in text for w in ("write", "draft", "proposal",
                                       "application", "apply", "grant"))):
        return "BUILD_APPLICATION"
    if "research" in text and ("funder" in text or "winner" in text):
        return "RESEARCH_FUNDER"
    if "update" in text or "profile" in text:
        return "UPDATE_PROFILE"
    if "explain" in text or "why" in text:
        return "EXPLAIN_RESULT"
    return "FIND_GRANTS"


def _classify_authority_scope(intent_type: str) -> str:
    """Intent types map to bounded authority scopes. BUILD_APPLICATION is
    PREPARE_ONLY: the platform can research + draft, never submit."""
    if intent_type in ("BUILD_APPLICATION", "ASSESS_OPPORTUNITY"):
        return "PREPARE_ONLY"
    if intent_type in ("RESEARCH_FUNDER", "RESEARCH_WINNERS"):
        return "RESEARCH_ONLY"
    return "EXPLORE_ONLY"


def normalize_requested_capabilities(requested: list[str]) -> tuple[list[str], list[str]]:
    """Submission capabilities normalize to prepare-only; fail closed."""
    normalized: list[str] = []
    notes: list[str] = []
    for cap in requested:
        if cap in SUBMISSION_CAPABILITIES or cap.startswith("submission."):
            normalized.append(PREPARE_ONLY_TARGET)
            notes.append(f"{cap} normalized to {PREPARE_ONLY_TARGET} "
                         "(submission disabled)")
        else:
            normalized.append(cap)
    return normalized, notes


@dataclass(frozen=True)
class IntentContract:
    intent_id: str
    tenant_id: str
    client_actor_id: str
    organization_id: str
    intent_type: str
    objective: str
    authority_scope: str
    confidence_state: str
    created_at: str
    source_conversation_ref: str = ""
    requested_capabilities: tuple[str, ...] = ()
    normalization_notes: tuple[str, ...] = ()
    version: int = 1
    supersedes_intent_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "tenant_id": self.tenant_id,
            "client_actor_id": self.client_actor_id,
            "organization_id": self.organization_id,
            "intent_type": self.intent_type,
            "objective": self.objective,
            "authority_scope": self.authority_scope,
            "confidence_state": self.confidence_state,
            "requested_capabilities": list(self.requested_capabilities),
            "normalization_notes": list(self.normalization_notes),
            "version": self.version,
            "supersedes_intent_id": self.supersedes_intent_id,
            "source_conversation_ref": self.source_conversation_ref,
            "created_at": self.created_at,
        }


@dataclass
class PersonalReply:
    message_id: str
    text: str
    intent: IntentContract | None = None
    clarifications: list[str] = field(default_factory=list)


class PersonalHermes:
    """Durable Personal Hermes. Constructor-injected Store (Postgres in
    production); stateless besides the store connection."""

    def __init__(self, store: Store, hermes_principal: str = "HERMES_PERSONAL"):
        self.store = store
        self.hermes_principal = hermes_principal

    def receive_message(self, *, conversation_id: str, tenant_id: str,
                        client_actor_id: str, organization_id: str,
                        content: str,
                        requested_capabilities: list[str] | None = None,
                        intent_id: str | None = None) -> PersonalReply:
        """Persist the client message, reduce to an IntentContract, persist
        the intent, and reply. No operational tools are executed here."""
        if self.store.get_conversation(conversation_id, tenant_id) is None:
            self.store.create_conversation({
                "conversation_id": conversation_id, "tenant_id": tenant_id,
                "client_actor_id": client_actor_id,
                "title": content[:80], "project_id": None})
        self.store.create_message({
            "message_id": f"msg-{conversation_id}-{_now()}",
            "conversation_id": conversation_id, "tenant_id": tenant_id,
            "role": "user", "content": content})

        intent_type = _classify_intent_type(content)
        scope = _classify_authority_scope(intent_type)
        caps, notes = normalize_requested_capabilities(
            requested_capabilities or [])
        intent = IntentContract(
            intent_id=intent_id or f"int-{conversation_id}-{_now()}",
            tenant_id=tenant_id, client_actor_id=client_actor_id,
            organization_id=organization_id, intent_type=intent_type,
            objective=content, authority_scope=scope,
            confidence_state="MEDIUM", created_at=_now(),
            source_conversation_ref=f"conv:{conversation_id}",
            requested_capabilities=tuple(caps),
            normalization_notes=tuple(notes))
        self.store.create_intent({
            "intent_id": intent.intent_id, "tenant_id": tenant_id,
            "client_actor_id": client_actor_id,
            "organization_id": organization_id,
            "intent_type": intent.intent_type,
            "objective": intent.objective,
            "authority_scope": intent.authority_scope,
            "confidence_state": intent.confidence_state,
            "version": intent.version,
            "supersedes_intent_id": intent.supersedes_intent_id,
            "source_conversation_ref": intent.source_conversation_ref,
            "payload": intent.to_payload()})

        # Build a contextual reply that references the user's actual request
        msg_preview = content[:120].rstrip()
        if intent_type == "BUILD_APPLICATION":
            reply_text = (
                f"Got it — you're looking for funding for: \"{msg_preview}\"\n\n"
                "Here's what I'll do:\n"
                "1. Search for matching grant opportunities\n"
                "2. Check your eligibility\n"
                "3. Research the funder's priorities and past winners\n"
                "4. Plan and draft a full proposal\n"
                "5. Build the budget and run quality checks\n\n"
                "I'm kicking off the work now — you'll see progress below.")
        elif intent_type == "ASSESS_OPPORTUNITY":
            reply_text = (
                f"Let me check eligibility for: \"{msg_preview}\"\n\n"
                "I'll review the requirements and let you know if you qualify.")
        elif intent_type == "RESEARCH_FUNDER":
            reply_text = (
                f"I'll research the funder for: \"{msg_preview}\"\n\n"
                "Looking into their priorities, past awards, and what makes a strong application.")
        elif intent_type == "UPDATE_PROFILE":
            reply_text = (
                "I'll update your organization profile with the new information.")
        elif intent_type == "EXPLAIN_RESULT":
            reply_text = (
                f"Let me explain: \"{msg_preview}\"\n\n"
                "Here's what's going on and why.")
        else:
            reply_text = (
                f"I understand you'd like to {intent_type.replace('_', ' ').lower()}. "
                f"Here's what I found regarding: \"{msg_preview}\"")
        msg_id = f"msg-{conversation_id}-{_now()}-reply"
        self.store.create_message({
            "message_id": msg_id, "conversation_id": conversation_id,
            "tenant_id": tenant_id, "role": "personal_hermes",
            "content": reply_text})
        return PersonalReply(message_id=msg_id, text=reply_text, intent=intent)
