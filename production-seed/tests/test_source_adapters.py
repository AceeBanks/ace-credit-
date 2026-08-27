"""G1 Wave 2 — real source connectivity tests.

Adapter contract: register/fetch/snapshot/hash/normalize/provenance/
authority/amendment detection. External content stays untrusted.
Revision watcher: material change -> new append-only revision + selective
invalidation; non-material -> nothing invalidated.
Parser lane: extraction with page/section/locator lineage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from grant_platform.sources.adapters import (  # noqa: E402
    CensusCommunityAdapter,
    GeorgiaSourceAdapter,
    GrantsGovAdapter,
    SourceError,
    SourceRegistry,
    USAspendingAdapter,
)
from grant_platform.domain.records import Tenant  # noqa: E402
from grant_platform.sources.watcher import (  # noqa: E402
    MATERIAL_TERMS,
    build_revision_change,
    classify_change,
    parse_document,
)
from grant_platform.store.db import Store  # noqa: E402


def _registry():
    reg = SourceRegistry()
    gg = GrantsGovAdapter(reg)
    ga = GeorgiaSourceAdapter(reg)
    us = USAspendingAdapter(reg)
    census = CensusCommunityAdapter(reg)
    return reg, gg, ga, us, census


def test_adapters_register_with_authority_classes():
    reg, gg, ga, us, census = _registry()
    assert gg.registry.get("grants_gov").authority_class == \
        "OFFICIAL_SOLICITATION"
    assert us.registry.get("usaspending").authority_class == "FUNDER_RECORD"
    assert census.registry.get("census_community").authority_class == \
        "GOVERNMENT_STATISTIC"


def test_unknown_source_denied():
    reg, *_ = _registry()
    with pytest.raises(SourceError):
        reg.get("not-a-source")


def test_capture_emits_immutable_hash_identified_snapshot():
    reg, gg, *_ = _registry()
    snap = gg.capture(tenant_id="tenant-a", resource_type="opportunity",
                      external_resource_id="opp_ga_501",
                      canonical_url="https://grants.gov/opp/501",
                      normalize=lambda b: {"title": "GA Rural"})
    assert snap.snapshot_id.startswith("snap-grants_gov-")
    assert len(snap.content_hash) == 64          # sha256
    assert snap.raw_bytes_hash == snap.content_hash
    assert snap.normalized == {"title": "GA Rural"}
    assert snap.canonical_url.startswith("https://")


def test_snapshot_persists_in_store():
    store = Store.open(":memory:")
    store.create_tenant(Tenant(tenant_id="tenant-a", display_name="A"))
    reg, gg, *_ = _registry()
    snap = gg.capture(tenant_id="tenant-a", resource_type="opportunity",
                      external_resource_id="opp_ga_501",
                      canonical_url="https://grants.gov/opp/501")
    store.create_snapshot({
        "snapshot_id": snap.snapshot_id, "canonical_url": snap.canonical_url,
        "retrieved_at": snap.retrieved_at, "content_hash": snap.content_hash,
        "tenant_id": snap.tenant_id, "payload_ref": snap.payload_ref})
    got = store.latest_snapshot("grants_gov", "tenant-a")
    assert got["snapshot_id"] == snap.snapshot_id
    assert len(store.snapshots_for("tenant-a")) == 1
    store.close()


def test_material_change_creates_revision_and_invalidates():
    reg, gg, *_ = _registry()
    snap1 = gg.capture(tenant_id="t", resource_type="opportunity",
                       external_resource_id="opp",
                       canonical_url="https://grants.gov/opp/1",
                       normalize=lambda b: {"deadline": "2026-10-15"})
    snap2 = gg.capture(tenant_id="t", resource_type="opportunity",
                       external_resource_id="opp",
                       canonical_url="https://grants.gov/opp/1",
                       normalize=lambda b: {"deadline": "2026-11-01"})
    change = build_revision_change(snap1, snap2)
    assert change.material is True
    assert change.changed_terms == ["deadline"]
    assert change.new_revision_id is not None
    assert set(change.invalidated_stages) == {
        "eligibility", "match", "project", "drafting", "assurance",
        "package"}
    # old snapshot untouched (immutable)
    assert snap1.normalized == {"deadline": "2026-10-15"}


def test_non_material_change_no_invalidation():
    reg, gg, *_ = _registry()
    snap1 = gg.capture(tenant_id="t", resource_type="opportunity",
                       external_resource_id="opp",
                       canonical_url="https://grants.gov/opp/1",
                       normalize=lambda b: {"formatting": "old"})
    snap2 = gg.capture(tenant_id="t", resource_type="opportunity",
                       external_resource_id="opp",
                       canonical_url="https://grants.gov/opp/1",
                       normalize=lambda b: {"formatting": "new"})
    change = build_revision_change(snap1, snap2)
    assert change.material is False
    assert change.new_revision_id is None
    assert change.invalidated_stages == []


def test_classify_change_unknown_terms_not_material():
    change = classify_change({"tone": "a"}, {"tone": "b"})
    assert change.material is False


def test_parser_lane_emits_locator_lineage():
    raw = b"## Executive Summary\nWe serve youth.\n## Budget\n$50,000."
    doc = parse_document(raw, "doc-1", "snap-1")
    assert doc.source_snapshot_id == "snap-1"
    assert [s["section"] for s in doc.sections] == ["Executive Summary",
                                                    "Budget"]
    assert doc.sections[0]["page"] == 1
    assert doc.sections[0]["locator"] == "Executive Summary"
    assert "parser:default" in doc.extraction_lineage


def test_external_content_remains_untrusted():
    """Adapter output is data, never authority: a hostile payload cannot
    change eligibility because eligibility is computed by the deterministic
    engine over governed facts, not over raw source text."""
    reg, *_ = _registry()
    # hostile normalized payload cannot introduce a revision id or a
    # material term that was not in the diff catalog
    change = classify_change({"deadline": "2026-10-15"},
                             {"deadline": "2026-10-15",
                              "attacker_field": "ELIGIBLE"})
    assert change.material is False           # attacker_field not material
    assert "attacker_field" not in MATERIAL_TERMS
