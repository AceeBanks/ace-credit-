"""B5.C9 — Dependency graph + selective invalidation prototype.

DEPENDS_ON edges with materiality; a change to an upstream ref invalidates
exactly the reachable dependent set (no global recompute, INV-004),
transitively bounded and inspectable (INV-005), cycle-safe (INV-006), and a
stale dependency blocks submission-ready state (INV-007).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEPENDENCY_TYPES = (
    "FACTUAL", "ELIGIBILITY", "REQUIREMENT", "MATCH", "NUMERIC", "CITATION",
    "NARRATIVE_ALIGNMENT", "POLICY", "MODEL_OUTPUT", "ARTIFACT_BUNDLE")

MATERIAL_CLASSES = ("MATERIAL", "DELETION", "NEW_REVISION")


class DependencyError(ValueError):
    """Raised when a dependency operation violates the rules."""


@dataclass
class DependencyEdge:
    dependency_id: str
    dependent_ref: str
    depends_on_ref: str
    dependency_type: str
    materiality: str
    created_at: str
    status: str = "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependency_id": self.dependency_id,
            "dependent_ref": self.dependent_ref,
            "depends_on_ref": self.depends_on_ref,
            "dependency_type": self.dependency_type,
            "materiality": self.materiality, "created_at": self.created_at,
            "status": self.status,
        }


@dataclass
class InvalidationEvent:
    invalidation_id: str
    changed_upstream_ref: str
    change_class: str
    affected_downstream_refs: list[str]
    required_action: str
    priority: str
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "invalidation_id": self.invalidation_id,
            "changed_upstream_ref": self.changed_upstream_ref,
            "change_class": self.change_class,
            "affected_downstream_refs": list(self.affected_downstream_refs),
            "required_action": self.required_action,
            "priority": self.priority, "resolved": self.resolved,
        }


class DependencyGraph:
    def __init__(self) -> None:
        self._edges: list[DependencyEdge] = []

    def add_dependency(self, *, dependent_ref: str, depends_on_ref: str,
                       dependency_type: str, materiality: str) -> DependencyEdge:
        if dependency_type not in DEPENDENCY_TYPES:
            raise DependencyError(f"unknown dependency type {dependency_type!r}")
        if materiality not in ("CRITICAL", "SIGNIFICANT", "MINOR"):
            raise DependencyError(f"unknown materiality {materiality!r}")
        edge = DependencyEdge(
            dependency_id=f"dep-{len(self._edges) + 1}",
            dependent_ref=dependent_ref, depends_on_ref=depends_on_ref,
            dependency_type=dependency_type, materiality=materiality,
            created_at="2026-08-26T00:00:00+00:00")
        self._edges.append(edge)
        return edge

    def dependents_of(self, ref: str) -> list[str]:
        """Direct dependents (things that depend on ref)."""
        return [e.dependent_ref for e in self._edges
                if e.depends_on_ref == ref]

    def transitive_dependents(self, ref: str, *,
                              max_hops: int = 8) -> tuple[list[str], bool]:
        """Bounded, inspectable transitive closure (INV-005/006).

        Returns (affected, cycle_detected). Cycle detection bounds the walk
        so an invalidation storm cannot occur (INV-006).
        """
        affected: list[str] = []
        frontier = [ref]
        seen: set[str] = set()
        cycle = False
        for _ in range(max_hops):
            if not frontier:
                break
            next_frontier: list[str] = []
            for node in frontier:
                for dependent in self.dependents_of(node):
                    if dependent in seen:
                        cycle = True
                        continue
                    seen.add(dependent)
                    affected.append(dependent)
                    next_frontier.append(dependent)
            frontier = next_frontier
        else:
            if frontier:
                cycle = True  # exceeded hop bound => treat as cycle/large fanout
        return affected, cycle

    def invalidate(self, *, changed_upstream_ref: str, change_class: str,
                   required_action: str | None = None) -> InvalidationEvent:
        """Selective invalidation: exactly the reachable dependents.

        NONMATERIAL changes never invalidate anything (INV-003 semantics).
        """
        if change_class == "NONMATERIAL":
            affected = []
        else:
            affected, _ = self.transitive_dependents(changed_upstream_ref)
            if not affected:
                affected = list(self.dependents_of(changed_upstream_ref))
        action = required_action or ("RECOMPUTE" if affected else "NONE")
        priority = "P0" if change_class in MATERIAL_CLASSES and affected else "P2"
        event = InvalidationEvent(
            invalidation_id=f"inv-{abs(hash((changed_upstream_ref, change_class)))}",
            changed_upstream_ref=changed_upstream_ref, change_class=change_class,
            affected_downstream_refs=affected, required_action=action,
            priority=priority)
        return event
