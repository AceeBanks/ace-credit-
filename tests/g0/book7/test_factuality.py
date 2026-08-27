"""B7.C8 — Factuality & evidence evaluation tests.

Claim support, citation precision/recall, unsupported claims, the C8 hard
gate (prose cannot offset factuality regression), future-target vs
historical classification, requirement coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.metrics import (  # noqa: E402
    citation_metrics,
    claim_support_metrics,
    factuality_hard_gate,
    future_vs_historical_classification,
    requirement_coverage,
    unsupported_material_claims,
)


def _supported(claim_id, **kw) -> dict:
    return {"claim_id": claim_id, "support_status": "SUPPORTED",
            "material": True, **kw}


def _unsupported(claim_id, **kw) -> dict:
    return {"claim_id": claim_id, "support_status": "UNSUPPORTED",
            "material": True, **kw}


def test_claim_support_rate():
    m = claim_support_metrics([_supported("c1"), _supported("c2"),
                               _unsupported("c3")])
    assert m["material_claim_support_rate"] == round(2 / 3, 4)
    assert m["unsupported"] == 1


def test_claim_support_empty():
    m = claim_support_metrics([])
    assert m["material_claim_support_rate"] == 0.0
    assert m["total"] == 0


def test_unsupported_list():
    entries = [_supported("c1"), _unsupported("c2")]
    assert [c["claim_id"] for c in unsupported_material_claims(entries)] == ["c2"]


def test_citation_precision_and_recall():
    citations = [
        {"claim_id": "c1", "cited_ref": "r1", "resolves": True,
         "supports_claim": True, "required": True},
        {"claim_id": "c2", "cited_ref": "r2", "resolves": True,
         "supports_claim": False, "required": True},
        {"claim_id": "c3", "cited_ref": "r3", "resolves": False,
         "supports_claim": False, "required": False},
    ]
    m = citation_metrics(citations=citations)
    assert m["citation_precision"] == round(1 / 3, 4)
    assert m["citation_recall"] == round(1 / 2, 4)
    assert m["resolvable"] == 2


def test_citation_that_does_not_support_claim_fails_precision():
    citations = [{"claim_id": "c1", "cited_ref": "r1", "resolves": True,
                  "supports_claim": False, "required": True}]
    m = citation_metrics(citations=citations)
    assert m["citation_precision"] == 0.0


def test_hard_gate_blocks_unsupported_increase():
    baseline = claim_support_metrics([_supported("c1"), _supported("c2")])
    candidate = claim_support_metrics([_supported("c1"), _unsupported("c2")])
    gate = factuality_hard_gate(baseline_metrics=baseline,
                                candidate_metrics=candidate)
    assert gate["pass"] is False
    assert "unsupported claims rose" in gate["reason"]


def test_hard_gate_passes_when_factuality_preserved():
    baseline = claim_support_metrics([_supported("c1"), _supported("c2")])
    candidate = claim_support_metrics([_supported("c1"), _supported("c2"),
                                       _supported("c3")])
    gate = factuality_hard_gate(baseline_metrics=baseline,
                                candidate_metrics=candidate)
    assert gate["pass"] is True


def test_hard_gate_blocks_support_rate_drop():
    baseline = claim_support_metrics([_supported("c1"), _supported("c2"),
                                      _unsupported("c3")])
    candidate = claim_support_metrics([_supported("c1"), _unsupported("c2"),
                                       _unsupported("c3"), _unsupported("c4")])
    gate = factuality_hard_gate(baseline_metrics=baseline,
                                candidate_metrics=candidate)
    assert gate["pass"] is False


def test_future_target_classification():
    claims = [
        {"claim_id": "c1", "is_target": True, "classified_as_target": True},
        {"claim_id": "c2", "is_target": False, "classified_as_target": False},
        {"claim_id": "c3", "is_target": True, "classified_as_target": False},
    ]
    m = future_vs_historical_classification(claims=claims)
    assert m["mismatches"] == ["c3"]
    assert m["accuracy"] == round(2 / 3, 4)


def test_requirement_coverage_deterministic():
    reqs = [{"requirement_id": "r1", "mandatory": True},
            {"requirement_id": "r2", "mandatory": True}]
    responses = [{"requirement_id": "r1", "state": "COMPLETED"}]
    m = requirement_coverage(requirements=reqs, responses=responses)
    assert m["coverage"] == 0.5
    assert m["missing"] == ["r2"]


def test_requirement_coverage_full():
    reqs = [{"requirement_id": "r1", "mandatory": True}]
    responses = [{"requirement_id": "r1", "state": "APPROVED_INTERNAL"}]
    m = requirement_coverage(requirements=reqs, responses=responses)
    assert m["coverage"] == 1.0
