"""G0-B5-C17 — Research Finding tests.

Required coverage (plan):
- finding requires evidence;
- limitation preserved;
- award sample size represented;
- research finding can be shown to client and consumed by drafting context.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402
from prototype.g0.evidence.research import (  # noqa: E402
    ResearchFindingError,
    client_view,
    validate_finding,
)


def _graph() -> EvidenceGraph:
    import yaml
    edge_cfg = yaml.safe_load((_ROOT / "config/g0/evidence/"
                               "evidence_edge_types.yaml")
                              .read_text(encoding="utf-8"))
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    for rid in ("stat:community", "snap:winner-records", "snap:award-range"):
        graph.put_ref(make_ref(ref_id=rid, ref_type="STATISTIC_OBSERVATION"
                               if "stat" in rid else "SOURCE_SNAPSHOT",
                               entity_type="StatisticObservation"
                               if "stat" in rid else "SourceSnapshot",
                               entity_id=rid.split(":")[1], tenant_id="tenant-a",
                               content_hash=f"{rid}-h" * 2))
    return graph


def _finding(**kw) -> dict:
    base = dict(
        finding_id="f1", research_type="COMMUNITY_NEED",
        statement="youth unemployment is elevated in the service region",
        evidence_refs=["stat:community"], quality="MEDIUM",
        applicability="supports needs narrative; not a funding fact",
        limitations=["single region sample"], created_by="worker:research",
    )
    base.update(kw)
    return base


def test_finding_requires_evidence():
    graph = _graph()
    with pytest.raises(ResearchFindingError):
        validate_finding(finding=_finding(evidence_refs=[]), graph=graph)


def test_limitation_preserved():
    graph = _graph()
    finding = validate_finding(
        finding=_finding(research_type="HISTORICAL_WINNER_PATTERN",
                         award_sample_size=4,
                         limitations=["sample of 4 winners; descriptive only"],
                         statement="past winners tended to propose youth "
                         "workforce programs"),
        graph=graph)
    assert finding["limitations"] == ["sample of 4 winners; descriptive only"]
    view = client_view(finding)
    assert view["limitations"] == finding["limitations"]


def test_award_sample_size_represented():
    graph = _graph()
    with pytest.raises(ResearchFindingError):
        validate_finding(
            finding=_finding(research_type="AWARD_RANGE",
                             evidence_refs=["snap:award-range"]),
            graph=graph)
    ok = validate_finding(
        finding=_finding(research_type="AWARD_RANGE",
                         evidence_refs=["snap:award-range"],
                         award_sample_size=12),
        graph=graph)
    assert ok["award_sample_size"] == 12


def test_causal_language_rejected_on_weak_sample():
    graph = _graph()
    with pytest.raises(ResearchFindingError):
        validate_finding(
            finding=_finding(research_type="HISTORICAL_WINNER_PATTERN",
                             award_sample_size=12,
                             statement="winners always propose workforce "
                             "programs"),
            graph=graph)


def test_finding_shown_to_client_and_consumed():
    graph = _graph()
    finding = validate_finding(finding=_finding(), graph=graph)
    view = client_view(finding)
    assert view["statement"] == finding["statement"]
    assert view["quality"] == "MEDIUM"
    # usable as drafting context: carries statement + applicability
    context = {"statement": finding["statement"],
               "applicability": finding["applicability"]}
    assert context["applicability"].startswith("supports needs narrative")
