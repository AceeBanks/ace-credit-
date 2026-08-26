"""G0 Book 2 — B2.C8 revision & temporal semantics (provisional executable form).

Stable root + immutable revisions. A RevisionSet never mutates a revision;
adding a revision yields a new RevisionSet. Dependent decisions (eligibility,
match, normalized requirements, generated drafts) anchor to the exact revision
they were made against and go stale only when a MATERIAL successor arrives.
Materiality is decided by the revision policy catalog (config/g0/domain/
revision_policy.yaml), never invented inline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Revision:
    """An immutable snapshot of the changed terms for one revision step."""
    revision_id: str
    revision_number: int
    changed_terms: frozenset[str]
    created_at: str
    material: bool = False            # classified once at creation, then frozen


@dataclass(frozen=True)
class DecisionAnchor:
    """A decision (eligibility/match/normalization/draft) made against an exact
    revision. Immutable — a later revision can never rewrite it (B2.C8)."""
    decision_id: str
    revision_id: str
    decision_kind: str = "eligibility"   # eligibility | match | normalized_requirements | draft


@dataclass(frozen=True)
class RevisionSet:
    """Stable root identity with an append-only chain of immutable revisions."""
    root_id: str
    entity_type: str
    revisions: tuple[Revision, ...] = ()

    def add(self, revision: Revision) -> "RevisionSet":
        return RevisionSet(self.root_id, self.entity_type, self.revisions + (revision,))

    def latest(self) -> Revision | None:
        return self.revisions[-1] if self.revisions else None

    def get(self, revision_id: str) -> Revision | None:
        return next((r for r in self.revisions if r.revision_id == revision_id), None)

    def index_of(self, revision_id: str) -> int | None:
        for i, r in enumerate(self.revisions):
            if r.revision_id == revision_id:
                return i
        return None


def material_terms(policy: dict) -> set[str]:
    return {term for cat in policy.get("material_change_categories", [])
            for term in cat.get("affected_terms", [])}


def non_material_terms(policy: dict) -> set[str]:
    return {term for cat in policy.get("non_material_change_categories", [])
            for term in cat.get("affected_terms", [])}


def classify_revision(revision_id: str, revision_number: int, changed_terms,
                      created_at: str, policy: dict) -> Revision:
    """Classify materiality from the policy catalog at creation time; the
    result is then frozen on the immutable Revision."""
    material = bool(set(changed_terms) & material_terms(policy))
    return Revision(revision_id, revision_number, frozenset(changed_terms),
                    created_at, material=material)


def is_stale(anchor: DecisionAnchor, revision_set: RevisionSet) -> bool:
    """A decision is stale iff a MATERIAL revision arrived after the exact
    revision it was anchored to. Non-material successors do NOT invalidate."""
    idx = revision_set.index_of(anchor.revision_id)
    if idx is None:
        return False                     # anchor not in this chain: not ours to judge
    return any(r.material for r in revision_set.revisions[idx + 1:])


def version_chain(versions: list["Any"]) -> list["Any"]:
    """Artifact version lineage: ordered, monotonic, contiguous, same root."""
    ordered = sorted(versions, key=lambda v: v.version_number)
    for v in ordered:
        if v.version_number < 1:
            raise ValueError(f"version number must be >= 1, got {v.version_number}")
    for a, b in zip(ordered, ordered[1:]):
        if a.artifact_id != b.artifact_id:
            raise ValueError("version chain crosses artifact roots")
        if b.version_number != a.version_number + 1:
            raise ValueError(f"version gap: {a.version_number} -> {b.version_number}")
    return ordered
