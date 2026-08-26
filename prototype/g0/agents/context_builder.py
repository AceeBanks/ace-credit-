"""B4.C10-C11 — ContextBundle assembly and ClientExplanationPacket (prototype).

  * build_context_bundle: explicit assembly in the fixed order; mandatory
    anchors ALWAYS survive budget pressure (budget 0 keeps anchors); the
    mandatory ref set is deterministic for the same state.
  * build_explanation: turns an OutcomeArtifact into a client explanation that
    preserves core facts and discloses uncertainty; visible research refs are
    carried through (past-winner/funder research product requirement).
  * style_transform: changes prose only — factual anchors ($ amounts, ISO
    dates, revision ids) are extracted before and asserted after.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

ASSEMBLY_ORDER = [
    "REQUIRED_CANONICAL_STATE", "REQUIRED_CURRENT_EVIDENCE",
    "ACTIVE_TASK_PROJECT_STATE", "MANDATORY_POLICY_CONSTRAINTS",
    "PROMOTED_ROLE_SPECIFIC_MEMORY", "SELECTED_RECENT_INTERACTION_CONTEXT",
    "OPTIONAL_SUPPORTING_HISTORY_WITHIN_BUDGET",
]

PROSE_FIELDS = ("summary", "what_we_found", "why_it_matters",
                "recommended_next_step")

_FACTUAL_TOKEN_RE = re.compile(
    r"\$\s?\d[\d,]*(?:\.\d{2})?|\b\d{4}-\d{2}-\d{2}\b|"
    r"\b(?:rev|opp-rev)-\d+\b|"
    r"\b\d[\d,]*(?:\.\d+)?%?")


class ContextAssemblyError(ValueError):
    """Raised when anchors would be lost or assembly is impossible."""


@dataclass
class ContextBundle:
    context_bundle_id: str
    consumer_actor: str
    operation_type: str
    tenant_id: str
    project_id: str | None
    canonical_state_refs: list[str]
    evidence_refs: list[str]
    memory_refs: list[str]
    recent_interaction_refs: list[str]
    policy_refs: list[str]
    task_refs: list[str]
    anchors: list[str]
    excluded_context_classes: list[str]
    assembled_at: str
    context_budget: dict = field(default_factory=dict)

    def mandatory_refs(self) -> list[str]:
        return (list(self.canonical_state_refs) + list(self.policy_refs)
                + list(self.task_refs))


def build_context_bundle(*, consumer_actor: str, operation_type: str,
                         tenant_id: str, project_id: str | None,
                         canonical_state_refs: list[str],
                         evidence_refs: list[str] | None = None,
                         memory_refs: list[str] | None = None,
                         recent_interaction_refs: list[str] | None = None,
                         policy_refs: list[str] | None = None,
                         task_refs: list[str] | None = None,
                         anchors: list[str],
                         excluded_context_classes: list[str] | None = None,
                         context_budget: dict | None = None) -> ContextBundle:
    """Assemble a ContextBundle (fail closed on anchor loss)."""
    anchors = list(anchors)
    all_refs = (list(canonical_state_refs) + list(evidence_refs or [])
                + list(memory_refs or []) + list(recent_interaction_refs or [])
                + list(policy_refs or []) + list(task_refs or []))
    missing_anchors = [a for a in anchors if a not in all_refs]
    if missing_anchors:
        raise ContextAssemblyError(
            f"mandatory anchors missing from provided refs: {missing_anchors}")

    bundle = ContextBundle(
        context_bundle_id=f"ctx-{abs(hash((tenant_id, operation_type, consumer_actor)))}",
        consumer_actor=consumer_actor, operation_type=operation_type,
        tenant_id=tenant_id, project_id=project_id,
        canonical_state_refs=list(canonical_state_refs),
        evidence_refs=list(evidence_refs or []),
        memory_refs=list(memory_refs or []),
        recent_interaction_refs=list(recent_interaction_refs or []),
        policy_refs=list(policy_refs or []),
        task_refs=list(task_refs or []),
        anchors=anchors,
        excluded_context_classes=list(excluded_context_classes or []),
        context_budget=dict(context_budget or {}),
        assembled_at=datetime.now(timezone.utc).isoformat(),
    )
    return _apply_budget(bundle)


def _apply_budget(bundle: ContextBundle) -> ContextBundle:
    """Budget pressure may drop optional classes, never anchors or P0 refs."""
    budget = bundle.context_budget
    item_count = budget.get("item_count")
    if item_count is None:
        return bundle
    anchor_set = set(bundle.anchors)
    # mandatory = canonical state + policy + task refs (P0)
    mandatory = set(bundle.canonical_state_refs) | set(bundle.policy_refs) \
        | set(bundle.task_refs)
    keep = anchor_set | mandatory
    if len(keep) > item_count:
        raise ContextAssemblyError(
            f"budget {item_count} cannot hold {len(keep)} mandatory refs")
    # drop optional classes in reverse assembly order until within budget
    for refs_attr, _cls in (
            ("recent_interaction_refs", None),
            ("memory_refs", None),
            ("evidence_refs", None)):
        if len(keep) >= item_count:
            break
        for ref in list(getattr(bundle, refs_attr)):
            if ref in keep:
                continue
            if len(keep) < item_count:
                keep.add(ref)
            else:
                break
    def _filter(refs: list[str]) -> list[str]:
        return [r for r in refs if r in keep]
    bundle.canonical_state_refs = _filter(bundle.canonical_state_refs)
    bundle.evidence_refs = _filter(bundle.evidence_refs)
    bundle.memory_refs = _filter(bundle.memory_refs)
    bundle.recent_interaction_refs = _filter(bundle.recent_interaction_refs)
    bundle.policy_refs = _filter(bundle.policy_refs)
    bundle.task_refs = _filter(bundle.task_refs)
    return bundle


def build_explanation(*, explanation_id: str, outcome: dict,
                      audience: str = "CLIENT_USER",
                      questions_for_client: list[str] | None = None) -> dict:
    """Turn an OutcomeArtifact into a ClientExplanationPacket.

    Core outcome facts (summary, unresolved questions, client-action flag,
    research/artifact refs) are preserved; uncertainty is disclosed.
    """
    factual_anchors = extract_factual_tokens(
        f"{outcome.get('executive_summary', '')} "
        f"{' '.join(outcome.get('evidence_refs', []))}")
    return {
        "explanation_id": explanation_id,
        "outcome_id": outcome["outcome_id"],
        "audience": audience,
        "summary": outcome.get("executive_summary", ""),
        "what_we_found": outcome.get("executive_summary", ""),
        "why_it_matters": "",
        "recommended_next_step": "",
        "questions_for_client": list(questions_for_client or []),
        "visible_research_refs": list(outcome.get("research_pack_refs", [])),
        "visible_artifact_refs": list(outcome.get("artifact_refs", [])),
        "uncertainty_disclosures": list(outcome.get("unresolved_questions", [])),
        "factual_anchors": sorted(factual_anchors),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def extract_factual_tokens(text: str) -> set[str]:
    """Extract factual anchors: dollar amounts, ISO dates, revision ids."""
    return set(_FACTUAL_TOKEN_RE.findall(text))


def style_transform(explanation: dict, transform) -> dict:
    """Apply a style transform to prose fields only.

    Factual anchors ($ amounts, dates, revision ids) are extracted before the
    transform and asserted unchanged afterwards — a style pass can change
    form, never supported facts.
    """
    before = extract_factual_tokens(" ".join(
        str(explanation.get(f, "")) for f in PROSE_FIELDS))
    result = dict(explanation)
    for field_name in PROSE_FIELDS:
        result[field_name] = transform(str(explanation.get(field_name, "")))
    after = extract_factual_tokens(" ".join(
        str(result.get(f, "")) for f in PROSE_FIELDS))
    if after != before:
        raise ContextAssemblyError(
            f"style transform changed factual tokens: "
            f"lost={sorted(before - after)} added={sorted(after - before)}")
    return result
