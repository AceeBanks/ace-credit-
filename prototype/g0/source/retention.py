"""G0-B3-C20 — Data retention, deletion & privacy classes.

Defines lifecycle before raw source and client data accumulate. Fail-closed:
  * every data class has a governed retention policy and allowed deletion
    semantics;
  * deleting raw evidence changes the replay status of downstream material
    (DELETE_CONTENT -> NON_REPLAYABLE, TOMBSTONE_METADATA -> PARTIAL_REPLAY,
    REVOKE_ACCESS -> access denied, ARCHIVE/HOLD -> still replayable);
  * a tenant delete cleans sidechains/cache rows for that tenant;
  * audit metadata never retains raw secret/PII fixture content.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml


class DeletionSemantic(Enum):
    DELETE_CONTENT = "DELETE_CONTENT"
    TOMBSTONE_METADATA = "TOMBSTONE_METADATA"
    REVOKE_ACCESS = "REVOKE_ACCESS"
    ARCHIVE = "ARCHIVE"
    LEGAL_OPERATIONAL_HOLD = "LEGAL_OPERATIONAL_HOLD"


class ReplayStatus(Enum):
    EXACT_REPLAY = "EXACT_REPLAY"
    COMPATIBLE_REPLAY = "COMPATIBLE_REPLAY"
    PARTIAL_REPLAY = "PARTIAL_REPLAY"
    NON_REPLAYABLE = "NON_REPLAYABLE"
    ACCESS_REVOKED = "ACCESS_REVOKED"


@dataclass(frozen=True)
class DataClass:
    class_id: str          # D0..D7
    name: str
    retention: str
    allowed_deletions: frozenset[DeletionSemantic]


def load_data_classes() -> list[DataClass]:
    cfg = load_yaml(SOURCE_CONFIG_DIR / "retention_policy.yaml")
    classes: list[DataClass] = []
    for row in cfg.get("data_classes", []):
        classes.append(DataClass(
            class_id=row["class_id"], name=row["name"], retention=row["retention"],
            allowed_deletions=frozenset(DeletionSemantic(s)
                                        for s in row.get("deletion_semantics", []))))
    return classes


def data_class_by_id(class_id: str, classes: list[DataClass] | None = None) -> DataClass | None:
    for c in (classes or load_data_classes()):
        if c.class_id == class_id:
            return c
    return None


def deletion_is_allowed(class_id: str, semantic: DeletionSemantic,
                        classes: list[DataClass] | None = None) -> bool:
    dc = data_class_by_id(class_id, classes)
    if dc is None:
        return False  # unknown class: fail closed
    return semantic in dc.allowed_deletions


def replay_status_after_deletion(semantic: DeletionSemantic) -> ReplayStatus:
    """What happens to downstream replay/evidence status when raw evidence is
    deleted under a given semantic (fail-closed, never silently unchanged)."""
    if semantic is DeletionSemantic.DELETE_CONTENT:
        return ReplayStatus.NON_REPLAYABLE
    if semantic is DeletionSemantic.TOMBSTONE_METADATA:
        return ReplayStatus.PARTIAL_REPLAY
    if semantic is DeletionSemantic.REVOKE_ACCESS:
        return ReplayStatus.ACCESS_REVOKED
    # ARCHIVE / LEGAL_OPERATIONAL_HOLD preserve replayability
    return ReplayStatus.COMPATIBLE_REPLAY


def tenant_delete_clean(tenant_id: str, sidechain_rows: list[dict],
                        cache_rows: list[dict]) -> tuple[list, list]:
    """A tenant delete must not leave the tenant's rows in sidechains/cache."""
    sidechains = [r for r in sidechain_rows if r.get("tenant_id") != tenant_id]
    caches = [r for r in cache_rows if r.get("tenant_id") != tenant_id]
    return sidechains, caches


def audit_does_not_retain_raw(audit_event: dict) -> bool:
    """Audit metadata may persist after deletion but must not embed the raw
    secret/PII fixture content itself."""
    raw_fields = {"raw_secret", "raw_pii", "full_payload", "secret_value"}
    return not (set(audit_event.keys()) & raw_fields)
