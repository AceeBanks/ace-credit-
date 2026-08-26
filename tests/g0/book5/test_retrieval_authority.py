"""G0-B5-C10 — retrieval constitution tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.retrieval import (  # noqa: E402
    RetrievalError,
    RetrievalHit,
    plan_retrieval,
    run_retrieval,
)


def _hit(result_ref: str, tenant: str = "tenant-a",
         staleness_flag: bool | None = None,
         conflict_flag: bool | None = None, **meta) -> RetrievalHit:
    return RetrievalHit(
        result_ref=result_ref, ranking_metadata=meta or {"score": 0.9},
        source_quality={"class": "VERIFIED_HIGH"},
        tenant_scope=tenant, staleness_flag=staleness_flag,
        conflict_flag=conflict_flag)


def test_exact_lookup_preferred_for_identifiers():
    assert plan_retrieval({"target": "ein"}) == "EXACT_STRUCTURED_LOOKUP"
    assert plan_retrieval({"target": "deadline"}) == "EXACT_STRUCTURED_LOOKUP"
    assert plan_retrieval({"exact_lookup_available": True}) == "EXACT_STRUCTURED_LOOKUP"


def test_discovery_uses_vector_lane():
    assert plan_retrieval({"discovery_only": True}) == "VECTOR_SEMANTIC"
    assert plan_retrieval({"needs_traversal": True}) == "GRAPH_TRAVERSAL"
    assert plan_retrieval({"free_text": True}) == "FULL_TEXT"


def test_vector_result_cannot_override_canonical_fact():
    hits = [_hit("fact:deadline", ranking_metadata={"score": 0.99})]
    result = run_retrieval(
        query_id="q1", method="VECTOR_SEMANTIC", query_scope={},
        tenant_scope="tenant-a", hits=hits,
        canonical_facts={"fact:deadline": "2026-10-15"})
    assert result.authority_gate_note is not None
    assert result.results[0].conflict_flag is True


def test_tenant_filter_before_exposure():
    hits = [_hit("a", tenant="tenant-a"), _hit("b", tenant="tenant-b")]
    result = run_retrieval(
        query_id="q2", method="FILTERED_RELATIONAL", query_scope={},
        tenant_scope="tenant-a", hits=hits)
    assert [h.result_ref for h in result.results] == ["a"]
    assert "b" not in [h.result_ref for h in result.results]


def test_stale_and_conflicted_flags_surface():
    hits = [_hit("stale-1", staleness_flag=True, conflict_flag=False)]
    result = run_retrieval(
        query_id="q3", method="EXACT_STRUCTURED_LOOKUP", query_scope={},
        tenant_scope="tenant-a", hits=hits)
    assert result.results[0].staleness_flag is True


def test_unknown_method_fails():
    with pytest.raises(RetrievalError, match="unknown retrieval method"):
        run_retrieval(query_id="q4", method="GUESS", query_scope={},
                      tenant_scope="tenant-a", hits=[])
