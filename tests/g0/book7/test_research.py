"""B7.C10 — Research quality evaluation tests.

Evidence grounding, limitation disclosure, causal caution on weak samples,
provenance completeness, future-target vs historical distinction.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.domain_eval import (  # noqa: E402
    evaluate_research_quality,
    future_target_not_historical,
)
from prototype.g0.evidence.research import (  # noqa: E402
    ResearchFindingError,
    validate_finding,
)


def _finding(**kw) -> dict:
    data = {
        "finding_id": "f1",
        "research_type": "HISTORICAL_WINNER_PATTERN",
        "subject_refs": ["org:ga"],
        "statement": "Recipients were mostly nonprofits in past cycles.",
        "evidence_refs": ["ref:award-1"],
        "quality": "VERIFIED",
        "applicability": "informational",
        "limitations": ["small sample"],
        "award_sample_size": 5,
        "created_at": "2026-08-26T00:00:00Z",
        "created_by": "research-worker",
    }
    data.update(kw)
    return data


def test_research_quality_measures_grounding():
    findings = [_finding(), _finding()]
    r = evaluate_research_quality(findings=findings)
    assert r["with_evidence"] == 2
    assert r["total"] == 2
    assert r["causal_caution_failures"] == 0


def test_weak_sample_without_limitations_fails_causal_caution():
    findings = [_finding(limitations=[])]
    r = evaluate_research_quality(findings=findings)
    assert r["weak_samples"] == 1
    assert r["causal_caution_failures"] == 1


def test_validate_finding_requires_evidence():
    from prototype.g0.evidence.models import EvidenceGraph
    graph = EvidenceGraph()
    with pytest.raises(ResearchFindingError):
        validate_finding(finding=_finding(evidence_refs=[]), graph=graph)


def test_validate_finding_causal_language_rejected():
    from prototype.g0.evidence.models import EvidenceGraph
    graph = EvidenceGraph()
    finding = _finding(
        statement="Winning is caused by being a nonprofit with a strong "
                  "mission statement.")
    with pytest.raises(ResearchFindingError):
        validate_finding(finding=finding, graph=graph)


def test_validate_finding_requires_sample_size_on_patterns():
    from prototype.g0.evidence.models import EvidenceGraph
    graph = EvidenceGraph()
    with pytest.raises(ResearchFindingError):
        validate_finding(finding=_finding(award_sample_size=None), graph=graph)


def test_future_target_not_historical():
    claims = [
        {"claim_id": "c1", "is_target": True, "classified_as_target": True},
        {"claim_id": "c2", "is_target": True, "classified_as_target": False},
    ]
    r = future_target_not_historical(claims=claims)
    assert r["pass"] is False
    assert r["failures"] == ["c2"]


def test_future_target_all_classified_correctly():
    claims = [
        {"claim_id": "c1", "is_target": True, "classified_as_target": True},
        {"claim_id": "c2", "is_target": False, "classified_as_target": False},
    ]
    assert future_target_not_historical(claims=claims)["pass"] is True
