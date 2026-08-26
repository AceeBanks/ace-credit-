"""B5.C10 — Retrieval constitution prototype.

Query planning picks the most deterministic lane (RETR-001); retrieval rank
is never authority (RETR-002); vector results can't override canonical facts
(RETR-003); stale/conflicted evidence is flagged (RETR-004); tenant filters
apply before exposure (RETR-005).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

EXACT_TARGETS = {"ein", "deadline", "award_ceiling", "opportunity_revision",
                 "requirement", "decision"}


class RetrievalError(ValueError):
    """Raised when a retrieval violates the constitution."""


@dataclass
class RetrievalHit:
    result_ref: str
    ranking_metadata: dict
    source_quality: dict
    tenant_scope: str
    staleness_flag: bool | None = None
    conflict_flag: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_ref": self.result_ref,
            "ranking_metadata": dict(self.ranking_metadata),
            "source_quality": dict(self.source_quality),
            "staleness_flag": self.staleness_flag,
            "conflict_flag": self.conflict_flag,
            "tenant_scope": self.tenant_scope,
        }


@dataclass
class RetrievalResult:
    query_id: str
    retrieval_method: str
    query_scope: dict
    results: list[RetrievalHit]
    tenant_scope: str
    authority_gate_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "retrieval_method": self.retrieval_method,
            "query_scope": dict(self.query_scope),
            "results": [r.to_dict() for r in self.results],
            "tenant_scope": self.tenant_scope,
            "authority_gate_note": self.authority_gate_note,
        }


def plan_retrieval(query: dict) -> str:
    """RETR-001: most deterministic lane that can answer the question."""
    target = query.get("target", "")
    if target in EXACT_TARGETS or query.get("exact_lookup_available"):
        return "EXACT_STRUCTURED_LOOKUP"
    if query.get("needs_traversal"):
        return "GRAPH_TRAVERSAL"
    if query.get("discovery_only"):
        return "VECTOR_SEMANTIC"
    if query.get("free_text"):
        return "FULL_TEXT"
    return "FILTERED_RELATIONAL"


def run_retrieval(*, query_id: str, method: str, query_scope: dict,
                  tenant_scope: str, hits: list[RetrievalHit],
                  canonical_facts: dict[str, Any] | None = None) -> RetrievalResult:
    """Run a lane and apply the authority gate.

    RETR-003: a vector/semantic hit that conflicts with a canonical fact is
    excluded from operational use (still returned with a flag, never
    authoritative). RETR-005: tenant filters applied before exposure.
    """
    if method not in ("EXACT_STRUCTURED_LOOKUP", "FILTERED_RELATIONAL",
                      "GRAPH_TRAVERSAL", "FULL_TEXT", "VECTOR_SEMANTIC"):
        raise RetrievalError(f"unknown retrieval method {method!r}")
    canonical_facts = canonical_facts or {}
    filtered = [h for h in hits if h.tenant_scope == tenant_scope]
    note = None
    if method == "VECTOR_SEMANTIC" and filtered:
        for h in filtered:
            for key, value in canonical_facts.items():
                if key in h.result_ref and value not in str(h.ranking_metadata):
                    h.conflict_flag = True
        conflicted = [h for h in filtered if h.conflict_flag]
        if conflicted:
            note = ("vector result conflicts with canonical fact — excluded "
                    "from operational use (RETR-003)")
    result = RetrievalResult(query_id=query_id, retrieval_method=method,
                             query_scope=dict(query_scope),
                             results=filtered, tenant_scope=tenant_scope,
                             authority_gate_note=note)
    return result
