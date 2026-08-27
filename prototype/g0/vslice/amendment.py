"""G0-B8-C29/C30/C31/C32 — amendment/revision chaos drill + selective invalidation.

When an opportunity revision changes after drafting, the machine must:

1. create a new immutable OpportunityRevision (append-only chain);
2. classify materiality from the governed policy catalog;
3. preserve the old revision and old draft/history untouched;
4. mark decisions anchored to the superseded revision stale;
5. selectively invalidate ONLY the downstream components whose decision
   anchor is stale — no global wipe/rebuild;
6. recompute the affected components;
7. explain the change to the client.

A non-material revision (e.g. formatting) must NOT invalidate downstream
decisions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from prototype.g0.domain.revisions import (
    DecisionAnchor,
    Revision,
    RevisionSet,
    classify_revision,
    is_stale,
)

# governed catalog mirror: material terms invalidate downstream work;
# non-material terms do not. Kept in sync with the Book 2 revision policy.
_REVISION_POLICY = {
    "material_change_categories": [
        {"category": "deadline", "affected_terms": ["deadline"]},
        {"category": "funding", "affected_terms": ["funding_ceiling",
                                                    "funding_amount"]},
        {"category": "eligibility", "affected_terms": ["eligibility_rules",
                                                       "service_area"]},
        {"category": "requirements", "affected_terms": ["required_attachments",
                                                        "program_requirements"]},
    ],
    "non_material_change_categories": [
        {"category": "formatting", "affected_terms": ["formatting",
                                                      "cover_sheet_style"]},
    ],
}

# stages whose decision anchor makes them downstream of a revision
_DOWNSTREAM_STAGES = ("eligibility", "match", "project", "drafting",
                      "assurance", "package")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AmendmentDrillResult:
    new_revision: dict
    material: bool
    changed_terms: list[str]
    stale_stages: list[str]           # selectively invalidated
    recomputed_stages: list[str]
    preserved_history: list[str]      # old revision ids + artifact refs kept
    explanation: str
    decisions: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def run_amendment_drill(*, revision_set: RevisionSet,
                       old_revision_id: str, new_revision_id: str,
                       changed_terms: list[str], revision_number: int,
                       stage_anchors: dict[str, DecisionAnchor],
                       preserved_artifacts: list[str]) -> AmendmentDrillResult:
    """Apply one amendment: create the new revision, classify materiality,
    selectively invalidate stale downstream stages, preserve history."""
    new_revision = classify_revision(
        revision_id=new_revision_id, revision_number=revision_number,
        changed_terms=changed_terms, created_at=_now(),
        policy=_REVISION_POLICY)
    updated_set = revision_set.add(new_revision)

    stale_stages: list[str] = []
    recomputed: list[str] = []
    decisions: list[dict] = []
    for stage in _DOWNSTREAM_STAGES:
        anchor = stage_anchors.get(stage)
        if anchor is None:
            continue
        if is_stale(anchor, updated_set):
            stale_stages.append(stage)
            recomputed.append(stage)
            decisions.append({
                "stage": stage, "decision_id": anchor.decision_id,
                "anchor_revision": anchor.revision_id,
                "status": "STALE_REQUIRES_RECOMPUTE",
                "new_revision": new_revision_id,
            })
        else:
            decisions.append({
                "stage": stage, "decision_id": anchor.decision_id,
                "anchor_revision": anchor.revision_id,
                "status": "FRESH_KEPT",
                "new_revision": new_revision_id,
            })

    explanation = (
        f"Amendment {new_revision_id} is {'MATERIAL' if new_revision.material else 'NON_MATERIAL'}; "
        f"changed terms: {sorted(changed_terms)}. "
        + ("Selectively invalidated: " + ", ".join(stale_stages) + "."
           if stale_stages else "No downstream stage invalidated.")
        + f" Old revision {old_revision_id} and {len(preserved_artifacts)} "
        "artifact(s) preserved for history.")

    return AmendmentDrillResult(
        new_revision={"revision_id": new_revision.revision_id,
                      "revision_number": new_revision.revision_number,
                      "material": new_revision.material,
                      "changed_terms": sorted(new_revision.changed_terms),
                      "created_at": new_revision.created_at},
        material=new_revision.material,
        changed_terms=list(changed_terms),
        stale_stages=stale_stages, recomputed_stages=recomputed,
        preserved_history=[old_revision_id] + preserved_artifacts,
        explanation=explanation, decisions=decisions)
