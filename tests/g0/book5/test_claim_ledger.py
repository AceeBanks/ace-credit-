"""G0-B5-C16 — Application Claim Ledger tests.

Required coverage (plan):
- synthetic testimonial fails support;
- future target not misclassified as achieved outcome;
- numerical claim traces to statistic/budget/fact;
- humanization cannot sever claim ledger mapping silently.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.claim_ledger import (  # noqa: E402
    ASSUMPTION,
    ClaimLedger,
    ClaimLedgerError,
    STALE,
    SUPPORTED,
    UNSUPPORTED,
)
from prototype.g0.evidence.models import EvidenceGraph, make_ref  # noqa: E402


def _graph() -> EvidenceGraph:
    edge_cfg = _load_edge_cfg()
    graph = EvidenceGraph(edge_types_config=edge_cfg,
                          endpoint_rules=edge_cfg.get("edge_endpoint_rules", []))
    for rid, rtype, eid, extra in (
        ("stat:population", "STATISTIC_OBSERVATION", "population", {}),
        ("fact:deadline", "CANONICAL_FACT", "deadline", {}),
        ("snap:testimonial", "SOURCE_SNAPSHOT", "testimonial",
         {"locator": {"origin": "SYNTHETIC"}}),
        ("snap:real", "SOURCE_SNAPSHOT", "real", {}),
    ):
        graph.put_ref(make_ref(ref_id=rid, ref_type=rtype,
                               entity_type="StatisticObservation" if rtype == "STATISTIC_OBSERVATION" else "CanonicalFact" if rtype == "CANONICAL_FACT" else "SourceSnapshot",
                               entity_id=eid, tenant_id="tenant-a",
                               content_hash=f"{rid}-h" * 2, **extra))
    return graph


def _load_edge_cfg() -> dict:
    import yaml
    return yaml.safe_load((_ROOT / "config/g0/evidence/"
                           "evidence_edge_types.yaml").read_text(encoding="utf-8"))


def _entry(**kw) -> dict:
    base = dict(
        artifact_version_id="art-v1", section_id="s1", claim_id="c1",
        claim_text_or_structured_ref="claim text",
        claim_class="ORGANIZATION_LEGAL_STATUS", evidence_refs=[],
        support_status="PENDING", qa_status="PENDING",
    )
    base.update(kw)
    return base


def test_synthetic_testimonial_fails_support():
    ledger = ClaimLedger()
    graph = _graph()
    assessed = ledger.put(
        entry=_entry(claim_id="c-t", claim_class="TESTIMONIAL_SUPPORT",
                     evidence_refs=["snap:testimonial"],
                     claim_text_or_structured_ref="a glowing review"),
        graph=graph)
    assert assessed["support_status"] == UNSUPPORTED
    assert assessed["qa_status"] == "FAILED"
    # a real source snapshot supports the same class
    ok = ledger.put(
        entry=_entry(claim_id="c-r", claim_class="TESTIMONIAL_SUPPORT",
                     evidence_refs=["snap:real"],
                     claim_text_or_structured_ref="a verified letter"),
        graph=graph)
    assert ok["support_status"] == SUPPORTED


def test_future_target_not_misclassified_as_achieved():
    ledger = ClaimLedger()
    graph = _graph()
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry=_entry(claim_id="c-out",
                         claim_class="MEASURABLE_OUTCOME_HISTORICAL",
                         evidence_refs=["stat:population"],
                         claim_text_or_structured_ref="we will serve 500 "
                         "youth by 2027"),
            graph=graph)
    # explicit target flag is accepted and stays a target
    target = ledger.put(
        entry=_entry(claim_id="c-tgt",
                     claim_class="MEASURABLE_OUTCOME_HISTORICAL",
                     is_target=True,
                     evidence_refs=["stat:population"],
                     claim_text_or_structured_ref="we will serve 500 youth "
                     "by 2027"),
        graph=graph)
    assert target["is_target"] is True


def test_numeric_claim_traces_to_statistic_or_fact():
    ledger = ClaimLedger()
    graph = _graph()
    ok = ledger.put(
        entry=_entry(claim_id="c-num", claim_class="POPULATION_COMMUNITY_STATISTICS",
                     evidence_refs=["stat:population"],
                     claim_text_or_structured_ref="32% of youth are unemployed"),
        graph=graph)
    assert ok["support_status"] == SUPPORTED
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry=_entry(claim_id="c-num-bad",
                         claim_class="FUNDING_AMOUNT",
                         evidence_refs=["snap:real"],
                         claim_text_or_structured_ref="we will request $50k"),
            graph=graph)


def test_humanization_cannot_sever_mapping_silently():
    ledger = ClaimLedger()
    graph = _graph()
    ledger.put(
        entry=_entry(claim_id="c-map", claim_class="DATES_DEADLINES",
                     evidence_refs=["fact:deadline"],
                     claim_text_or_structured_ref="deadline is Oct 15"),
        graph=graph)
    # same artifact version + changed text => rejected
    with pytest.raises(ClaimLedgerError):
        ledger.reversion(artifact_version_id="art-v1", claim_id="c-map",
                         new_text="deadline is Dec 1")
    # new artifact version => new claim entry, mapping preserved
    revised = ledger.reversion(artifact_version_id="art-v2", claim_id="c-map",
                               new_text="deadline is Dec 1")
    assert revised["claim_id"] == "c-map-v2"
    assert revised["artifact_version_id"] == "art-v2"
    assert ledger.entry("c-map")["artifact_version_id"] == "art-v1"


def test_tombstoned_evidence_is_stale():
    ledger = ClaimLedger()
    graph = _graph()
    graph.tombstone("fact:deadline")
    assessed = ledger.put(
        entry=_entry(claim_id="c-stale", claim_class="DATES_DEADLINES",
                     evidence_refs=["fact:deadline"],
                     claim_text_or_structured_ref="deadline is Oct 15"),
        graph=graph)
    assert assessed["support_status"] == STALE


def test_assumption_requires_future_representation():
    ledger = ClaimLedger()
    graph = _graph()
    with pytest.raises(ClaimLedgerError):
        ledger.put(
            entry=_entry(claim_id="c-asm",
                         claim_class="BUDGET_ASSUMPTION",
                         support_status=ASSUMPTION,
                         claim_text_or_structured_ref="we spent $40k last year"),
            graph=graph)
