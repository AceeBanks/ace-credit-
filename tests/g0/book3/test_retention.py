"""B3.C20 tests — Data Retention, Deletion & Privacy Classes.

Fail-closed:
  * all eight data classes D0..D7 exist with governed retention;
  * deletion semantics are enumerated and class-allowed;
  * deleting raw evidence changes downstream replay status (DELETE_CONTENT ->
    NON_REPLAYABLE; TOMBSTONE -> PARTIAL; ARCHIVE/HOLD keep replayability);
  * a tenant delete cleans sidechains/cache rows for that tenant;
  * audit metadata never retains raw secret/PII fixture content.
"""
from __future__ import annotations

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml
from tools.g0.validate_retention_provenance import (
    KNOWN_DELETION_SEMANTICS,
    REQUIRED_DATA_CLASSES,
    validate_retention,
)
from prototype.g0.source.retention import (
    DeletionSemantic,
    ReplayStatus,
    audit_does_not_retain_raw,
    data_class_by_id,
    deletion_is_allowed,
    load_data_classes,
    replay_status_after_deletion,
    tenant_delete_clean,
)

CFG = SOURCE_CONFIG_DIR / "retention_policy.yaml"


def test_validator_live_config_passes():
    errors: list[str] = []
    validate_retention(load_yaml(CFG), errors)
    assert errors == []


def test_all_data_classes_present():
    classes = load_data_classes()
    assert {c.class_id for c in classes} == REQUIRED_DATA_CLASSES
    for c in classes:
        assert c.retention


def test_deletion_semantics_match_config():
    cfg = load_yaml(CFG)
    assert set(cfg["deletion_semantics"]) == KNOWN_DELETION_SEMANTICS


def test_unknown_class_fails_closed():
    assert data_class_by_id("D99") is None
    assert deletion_is_allowed("D99", DeletionSemantic.DELETE_CONTENT) is False


def test_delete_content_makes_raw_evidence_non_replayable():
    assert (replay_status_after_deletion(DeletionSemantic.DELETE_CONTENT)
            is ReplayStatus.NON_REPLAYABLE)


def test_tombstone_metadata_gives_partial_replay():
    assert (replay_status_after_deletion(DeletionSemantic.TOMBSTONE_METADATA)
            is ReplayStatus.PARTIAL_REPLAY)


def test_revoke_access_blocks_access():
    assert (replay_status_after_deletion(DeletionSemantic.REVOKE_ACCESS)
            is ReplayStatus.ACCESS_REVOKED)


def test_archive_and_hold_preserve_replay():
    assert (replay_status_after_deletion(DeletionSemantic.ARCHIVE)
            is ReplayStatus.COMPATIBLE_REPLAY)
    assert (replay_status_after_deletion(DeletionSemantic.LEGAL_OPERATIONAL_HOLD)
            is ReplayStatus.COMPATIBLE_REPLAY)


def test_audit_class_cannot_delete_content():
    # D6 audit records: legal hold/tombstone allowed, content deletion NOT
    assert deletion_is_allowed("D6", DeletionSemantic.DELETE_CONTENT) is False
    assert deletion_is_allowed("D6", DeletionSemantic.LEGAL_OPERATIONAL_HOLD) is True


def test_tenant_delete_cleans_sidechains_and_cache():
    sidechains = [{"tenant_id": "t1", "trace": "..."},
                  {"tenant_id": "t2", "trace": "..."}]
    caches = [{"tenant_id": "t1", "chunk": "..."}]
    sc, ca = tenant_delete_clean("t1", sidechains, caches)
    assert [r["tenant_id"] for r in sc] == ["t2"]
    assert ca == []


def test_audit_metadata_does_not_retain_raw_secret():
    clean = {"event_id": "e1", "tenant_id": "t1", "action": "GRANTED"}
    leaky = {"event_id": "e2", "raw_secret": "sk-abc123", "tenant_id": "t1"}
    assert audit_does_not_retain_raw(clean) is True
    assert audit_does_not_retain_raw(leaky) is False
