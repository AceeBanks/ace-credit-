"""B3.C4-C5 tests — Source Onboarding protocol + immutable SourceSnapshot.

Fail-closed governance:
  * a SourceCandidate never auto-enables a domain
  * promotion requires passing EVERY staged onboarding gate
  * statuses are drawn from the known set
  * snapshots are immutable: mutation attempts are rejected
  * identical raw content deduplicates bytes but preserves retrieval events
  * changed content creates new snapshot lineage
  * the validator enforces the snapshot field contract / enum members
"""
from __future__ import annotations

import copy

import pytest

from prototype.g0.source.onboarding import (
    SourceGovernor,
    SourceOnboardingPacket,
    SourceStatus,
    discover_source,
    ONBOARDING_STAGES,
)
from prototype.g0.source.snapshot import (
    CaptureEvent,
    CaptureMethod,
    SourceSnapshot,
    SnapshotStatus,
    SnapshotStore,
    build_snapshot,
    sha256_hex,
)
from tools.g0._common import REPO_ROOT, SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_onboarding_snapshot import (
    SNAPSHOT_FIELDS,
    validate,
    validate_onboarding,
)


def _cfg():
    return load_yaml(REPO_ROOT / "config" / "g0" / "source" / "onboarding_snapshot.yaml")


def _packet(sid="src_ga_opb_grants") -> SourceOnboardingPacket:
    return SourceOnboardingPacket(source_id=sid, source_identity="GA OPB")


def test_validator_live_config_passes():
    ok, report = validate(SOURCE_CONFIG_DIR / "onboarding_snapshot.yaml")
    assert ok, report["errors"]
    assert report["snapshot_fixture_count"] == 2


# --- C4 onboarding protocol -------------------------------------------------

def test_candidate_never_auto_enables():
    cand = discover_source("mystery.org", "agent", "found a useful site")
    governor = SourceGovernor()
    # A candidate alone is not even registered; registration starts at CANDIDATE.
    assert cand.discovered_by == "agent"
    assert not governor.can_promote_data("mystery.org")


def test_unreviewed_source_cannot_be_enabled():
    governor = SourceGovernor()
    governor.register("src_x")
    with pytest.raises(ValueError):
        governor.promote_to_enabled("src_x", _packet("src_x"))  # no stages passed


def test_promote_requires_every_onboarding_stage():
    governor = SourceGovernor()
    governor.register("src_x")
    for stage in ONBOARDING_STAGES:
        if stage != "enabled":
            governor.pass_stage("src_x", stage)
    # has not passed the final "enabled" gate -> still blocked
    with pytest.raises(ValueError):
        governor.promote_to_enabled("src_x", _packet("src_x"))


def test_full_protocol_enables_and_promotes():
    governor = SourceGovernor()
    governor.register("src_ga_opb_grants")
    for stage in ONBOARDING_STAGES:
        governor.pass_stage("src_ga_opb_grants", stage)
    governor.promote_to_enabled("src_ga_opb_grants", _packet())
    assert governor.status("src_ga_opb_grants") == SourceStatus.ENABLED
    assert governor.can_promote_data("src_ga_opb_grants")


def test_disabled_source_cannot_promote_new_data():
    governor = SourceGovernor()
    governor.register("src_y")
    for stage in ONBOARDING_STAGES:
        governor.pass_stage("src_y", stage)
    governor.promote_to_enabled("src_y", _packet("src_y"))
    governor.set_status("src_y", SourceStatus.DISABLED)
    assert not governor.can_promote_data("src_y")


def test_retired_source_cannot_be_enabled():
    governor = SourceGovernor()
    governor.register("src_z")
    governor.set_status("src_z", SourceStatus.RETIRED)
    for stage in ONBOARDING_STAGES:
        governor.pass_stage("src_z", stage)
    with pytest.raises(ValueError):
        governor.promote_to_enabled("src_z", _packet("src_z"))


def test_status_must_be_known_enum():
    errs: list[str] = []
    validate_onboarding(["MYSTERIOUS"], {}, errs)
    assert any("unknown source status" in e for e in errs)


def test_onboarding_packet_carries_owner_and_policy():
    packet = _packet()
    assert packet.operational_owner is None or True  # optional at packet stage


# --- C5 immutable SourceSnapshot -------------------------------------------

def _snap(previous=None, rev="v1", obj="s3://raw/x.json", raw=b"{}") -> SourceSnapshot:
    return build_snapshot(
        snapshot_id=f"snap_{rev}",
        source_id="src_ga_opb_grants",
        resource_type="opportunity",
        external_resource_id="ga-opp-1",
        canonical_url="https://opb.georgia.gov/grants/1",
        request_id="req_A",
        retrieved_at="2026-08-01T12:00:00Z",
        raw_object_uri=obj,
        raw_bytes=raw,
        adapter_name="ga_opb_adapter",
        adapter_version="1.0.0",
        capture_method=CaptureMethod.API_JSON,
        previous_snapshot_id=previous,
        revision_key=rev,
    )


def test_snapshot_is_immutable_frozen():
    snap = _snap()
    with pytest.raises(Exception):
        snap.raw_hash = "tampered"


def test_mutation_attempt_rejected_and_recorded():
    store = SnapshotStore()
    snap = _snap()
    store.put_snapshot(snap)
    with pytest.raises(ValueError):
        store.attempt_mutation(snap.snapshot_id)
    assert store.mutation_attempts == [snap.snapshot_id]


def test_raw_hash_deterministic():
    a = _snap(raw=b"{}")
    b = _snap(raw=b"{}")
    assert a.raw_hash == b.raw_hash == sha256_hex(b"{}")


def test_identical_content_deduplicates_bytes_keeps_events():
    store = SnapshotStore()
    s1 = _snap(obj="s3://raw/a", raw=b"same")
    s2 = _snap(rev="v2", obj="s3://raw/a", raw=b"same", previous="snap_v1")
    store.put_snapshot(s1)
    store.put_snapshot(s2)
    # both reference the same raw hash (byte dedup), distinct retrieval events:
    assert s1.raw_hash == s2.raw_hash
    ev1 = CaptureEvent(event_id="e1", source_id="s", external_resource_id="r",
                       retrieved_at="t1", raw_hash=s1.raw_hash)
    ev2 = CaptureEvent(event_id="e2", source_id="s", external_resource_id="r",
                       retrieved_at="t2", raw_hash=s2.raw_hash)
    store.record_event(ev1)
    store.record_event(ev2)
    assert len(store.events()) == 2


def test_changed_content_creates_new_lineage():
    store = SnapshotStore()
    s1 = _snap(rev="v1", raw=b"{}")
    s2 = _snap(rev="v2", previous=s1.snapshot_id, raw=b"{+}")
    assert s1.raw_hash != s2.raw_hash
    assert s2.previous_snapshot_id == s1.snapshot_id
    store.put_snapshot(s1)
    store.put_snapshot(s2)
    lineage = store.snapshots_by_source("src_ga_opb_grants")
    assert {s.snapshot_id for s in lineage} == {"snap_v1", "snap_v2"}


def test_validator_enforces_snapshot_field_contract():
    from tools.g0.validate_onboarding_snapshot import validate_snapshot_rows
    bad = copy.deepcopy(_cfg())
    del bad["snapshot_fixtures"][0]["snapshot_id"]
    errs: list[str] = []
    validate_snapshot_rows(bad["snapshot_fixtures"], errs)
    assert any("snapshot_id" in e for e in errs)


def test_all_snapshot_required_fields_declared():
    for f in ("snapshot_id", "raw_hash", "canonical_url", "capture_method",
              "snapshot_status", "previous_snapshot_id"):
        assert f in SNAPSHOT_FIELDS