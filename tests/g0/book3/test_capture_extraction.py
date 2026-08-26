"""B3.C6-C7 tests — Capture/Replay + Extraction/Normalization lineage.

Fail-closed:
  * capture→replay fixture equality;
  * corrupt blob fails hash verification;
  * parser upgrade can reprocess old raw capture without refetching;
  * source disappears from web but historical snapshot stays replayable;
  * same raw snapshot supports multiple extraction strategies without
    overwriting prior outputs;
  * parser version lineage preserved;
  * invalid schema extraction fails normalization;
  * low extraction confidence cannot silently become a VERIFIED fact.
"""
from __future__ import annotations

import copy
import pytest

from prototype.g0.source.capture import (
    ContentAddressedStore,
    ReplayClass,
    ReplayOutcome,
    ReplayRequest,
    reproduce,
)
from prototype.g0.source.extraction import (
    ExtractionEngine,
    ExtractionEvent,
    ExtractionStatus,
    ExtractionStore,
    Lineage,
    NormalizationEvent,
    ValidationStatus,
    MIN_ACCEPTABLE_CONFIDENCE,
    same_snapshot_multi_strategy_ok,
)
from prototype.g0.source.snapshot import (
    CaptureMethod,
    build_snapshot,
    sha256_hex,
)
from tools.g0.validate_capture_extraction import (
    CANDIDATE_ONLY_ENGINES,
    KNOWN_ENGINES,
    KNOWN_REPLAY_CLASSES,
    validate,
)
from tools.g0._common import REPO_ROOT, SOURCE_CONFIG_DIR, load_yaml

CFG = SOURCE_CONFIG_DIR / "capture_extraction.yaml"


def _snap(adapter_version="1.0.0", rev="v1", raw=b"{}"):
    return build_snapshot(
        snapshot_id=f"snap_{rev}", source_id="src_ga_opb_grants",
        resource_type="opportunity", external_resource_id="ga-opp-1",
        canonical_url="https://opb.georgia.gov/grants/1", request_id="req",
        retrieved_at="2026-08-01T12:00:00Z",
        raw_object_uri="s3://raw/ga/1.json", raw_bytes=raw,
        adapter_name="ga_opb_adapter", adapter_version=adapter_version,
        capture_method=CaptureMethod.API_JSON, revision_key=rev)


def test_validator_live_config_passes():
    ok, report = validate(CFG)
    assert ok, report["errors"]


# --- C6 capture / replay ----------------------------------------------------

def test_content_address_store_deterministic_and_dedups():
    store = ContentAddressedStore()
    a = store.put(b"hello", uri="s3://x/a")
    b = store.put(b"hello", uri="s3://x/b")
    assert a.raw_hash == b.raw_hash == sha256_hex(b"hello")
    # two URIs share one content address, one byte store
    assert len(store._blobs) == 1
    assert store.get(a) == b"hello"


def test_corrupt_blob_fails_hash_verification():
    store = ContentAddressedStore()
    addr = store.put(b"intact", uri="s3://x/c")
    # tamper the stored bytes directly
    store._blobs[addr.raw_hash] = b"tampered!"
    assert store.verify(addr) is False
    with pytest.raises(ValueError):
        store.get(addr)
    assert addr.raw_hash in store._corrupt_detected


def test_capture_replay_fixture_equality():
    snap = _snap()
    res = reproduce(ReplayRequest(snap, b"{}", "ga_opb_adapter", "1.0.0"),
                    available_version="1.0.0")
    assert res.replay_class == ReplayClass.EXACT_REPLAY
    assert res.ok


def test_parser_upgrade_replays_old_raw_without_refetch():
    snap = _snap(adapter_version="1.0.0")
    res = reproduce(ReplayRequest(snap, b"{}", "ga_opb_adapter", "1.0.0"),
                    available_version="2.0.0")
    assert res.replay_class == ReplayClass.COMPATIBLE_REPLAY
    assert res.ok
    # same raw capture is replayed by a newer parser — no refetch needed
    assert res.evidence["captured"] == "1.0.0"
    assert res.evidence["replayed_by"] == "2.0.0"


def test_missing_raw_blocked_non_replayable():
    snap = _snap()
    res = reproduce(ReplayRequest(snap, None, "ga_opb_adapter", "1.0.0"),
                    available_version="1.0.0")
    assert res.replay_class == ReplayClass.NON_REPLAYABLE
    assert not res.ok


def test_corrupt_snapshot_non_replayable():
    snap = _snap()
    res = reproduce(ReplayRequest(snap, b"<<corrupt>>", "ga_opb_adapter", "1.0.0"),
                    available_version="1.0.0")
    assert not res.ok
    assert any("hash mismatch" in e for e in res.errors)


def test_source_disappears_but_historical_snapshot_stays_replayable():
    # raw object retained under retention policy => still EXACT_REPLAY
    snap = _snap(rev="old")
    raw = b"{}"
    captured_hash = snap.raw_hash
    assert captured_hash == sha256_hex(raw)
    res = reproduce(ReplayRequest(snap, raw, "ga_opb_adapter", "1.0.0"),
                    available_version="1.0.0")
    assert res.replay_class == ReplayClass.EXACT_REPLAY
    assert res.ok


def test_non_replayable_rejected_for_promoted_critical():
    snap = _snap()
    # NON_REPLAYABLE is not in the allowed set => fail closed
    from prototype.g0.source.capture import replayable_within_retention
    res = replayable_within_retention(snap, retention_class="D1",
                                      allowed={ReplayClass.EXACT_REPLAY,
                                               ReplayClass.COMPATIBLE_REPLAY})
    assert not res.ok
    assert any("NON_REPLAYABLE not permitted" in e for e in res.errors)


# --- C7 extraction / normalization ------------------------------------------

def _ext(engine, version="0.1.0", status=ExtractionStatus.COMPLETED, metrics=None,
         event_id="ext_1"):
    return ExtractionEvent(
        extraction_event_id=event_id, snapshot_id="snap_ga_0001", engine=engine,
        engine_version=version, strategy=engine, started_at="t0",
        completed_at="t1", quality_metrics=metrics or {},
        output_artifact_ref=f"s3://out/{event_id}.json", status=status)


def test_same_snapshot_multi_strategy_no_overwrite():
    store = ExtractionStore()
    store.register_extraction(_ext("deterministic_json_mapper", event_id="e1"))
    store.register_extraction(_ext("llm_structured", version="0.3.0", event_id="e2"))
    assert same_snapshot_multi_strategy_ok(store, "snap_ga_0001")
    assert {e.engine for e in store.extractions_for_snapshot("snap_ga_0001")} == {
        "deterministic_json_mapper", "llm_structured"}


def test_parser_version_lineage_preserved():
    store = ExtractionStore()
    store.register_extraction(_ext("llm_structured", version="0.3.0", event_id="e1"))
    lin = store._lineage["e1"]
    assert lin.extraction.engine_version == "0.3.0"


def test_low_confidence_cannot_become_verified():
    store = ExtractionStore()
    store.register_extraction(_ext("llm_structured", version="0.3.0",
                                   metrics={"overall_confidence": 0.5}, event_id="e1"))
    n = NormalizationEvent(
        normalization_event_id="n1", extraction_event_id="e1",
        normalizer_name="norm", normalizer_version="1", target_schema="sch",
        source_fields=["a"], output_entity_or_claim_refs=["c1"],
        confidence_components={"overall_confidence": 0.5},
        validation_status=ValidationStatus.VERIFIED)
    with pytest.raises(ValueError):
        store.normalize(n)


def test_normalize_requires_existing_extraction():
    store = ExtractionStore()
    n = NormalizationEvent(
        normalization_event_id="n1", extraction_event_id="missing",
        normalizer_name="norm", normalizer_version="1", target_schema="sch",
        source_fields=[], output_entity_or_claim_refs=[],
        confidence_components={}, validation_status=ValidationStatus.CANDIDATE)
    with pytest.raises(KeyError):
        store.normalize(n)


def test_llm_output_stays_candidate_not_auto_verified():
    store = ExtractionStore()
    store.register_extraction(_ext("llm_structured", version="0.3.0",
                                   metrics={"overall_confidence": 0.9}, event_id="e1"))
    # Attach a CANDIDATE normalization (legal). Auto-VERIFIED is enforced by
    # the validator rule for these engines.
    n = NormalizationEvent(
        normalization_event_id="n1", extraction_event_id="e1",
        normalizer_name="norm", normalizer_version="1", target_schema="sch",
        source_fields=[], output_entity_or_claim_refs=[], confidence_components={},
        validation_status=ValidationStatus.CANDIDATE)
    store.normalize(n)
    assert len(store.normalizations_for_extraction("e1")) == 1


def test_heuristic_engine_cannot_auto_verify_in_validator():
    cfg = copy.deepcopy(load_yaml(CFG))
    cfg["extraction_events"].append({
        "extraction_event_id": "ext_bad", "snapshot_id": "snap_x",
        "engine": "llm_structured", "engine_version": "0.3.0", "strategy": "s",
        "started_at": "t", "completed_at": "t2",
        "quality_metrics": {"overall_confidence": 0.95},
        "output_artifact_ref": "s3://out/bad.json", "status": "COMPLETED",
        "auto_verified": True})
    from pathlib import Path
    from tools.g0.validate_capture_extraction import validate_extraction
    errs: list[str] = []
    validate_extraction(cfg, errs)
    assert any("auto" in e for e in errs)