"""G0-B3-C5 — SourceSnapshot and CaptureEvent: the immutable unit of captured outside state.

An immutable, content-addressed snapshot of a single captured resource. The raw
body is not stored inline; it is referenced by a raw_object_uri + hash, and
corrective changes create a NEW snapshot (or a metadata correction event with
lineage) — never an in-place mutation.

Separating a CaptureEvent (a retrieval occurrence) from the deduplicated raw
object lets identical content share bytes while preserving every retrieval's
timing.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CaptureMethod(Enum):
    API_JSON = "API_JSON"
    API_XML = "API_XML"
    BULK_FILE = "BULK_FILE"
    HTML = "HTML"
    PDF = "PDF"
    DOCX = "DOCX"
    IMAGE = "IMAGE"
    MANUAL_UPLOAD = "MANUAL_UPLOAD"
    USER_FORM = "USER_FORM"
    OTHER = "OTHER"  # governed extension


class SnapshotStatus(Enum):
    CAPTURED = "CAPTURED"
    VERIFIED_INTEGRITY = "VERIFIED_INTEGRITY"
    PARTIAL = "PARTIAL"
    FAILED_CAPTURE = "FAILED_CAPTURE"
    REDACTED = "REDACTED"
    TOMBSTONED = "TOMBSTONED"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class SourceSnapshot:
    """Immutable unit of captured outside state. All fields are meaningful
    capture metadata; the record must not be mutated in place."""

    snapshot_id: str
    source_id: str
    tenant_id: Optional[str]
    resource_type: str
    external_resource_id: str
    canonical_url: str
    request_id: str
    request_fingerprint: str
    retrieved_at: str
    source_effective_at: Optional[str]
    source_published_at: Optional[str]
    http_status: Optional[int]
    http_headers_subset: dict
    content_type: Optional[str]
    content_length: Optional[int]
    raw_object_uri: str
    raw_hash: str
    raw_hash_algorithm: str
    adapter_name: str
    adapter_version: str
    capture_method: CaptureMethod
    previous_snapshot_id: Optional[str] = None
    revision_key: Optional[str] = None
    source_etag: Optional[str] = None
    source_last_modified: Optional[str] = None
    snapshot_status: SnapshotStatus = SnapshotStatus.CAPTURED

    @property
    def is_immutable(self) -> bool:
        return True


@dataclass(frozen=True)
class CaptureEvent:
    """A single retrieval occurrence. Multiple events may reference the same
    content-addressed raw hash (deduplicated bytes) without duplicating them."""

    event_id: str
    source_id: str
    external_resource_id: str
    retrieved_at: str
    raw_hash: str
    request_id: Optional[str] = None
    http_status: Optional[int] = None


class SnapshotStore:
    """Content-addressed snapshot/retrieval store with an immutable ledger."""

    def __init__(self) -> None:
        self._snapshots: dict[str, SourceSnapshot] = {}
        self._events: list[CaptureEvent] = []
        self._mutations: list[str] = []

    @property
    def mutation_attempts(self) -> list[str]:
        return list(self._mutations)

    def put_snapshot(self, snap: SourceSnapshot) -> None:
        if snap.snapshot_id in self._snapshots:
            raise ValueError(f"snapshot already present: {snap.snapshot_id}")
        self._snapshots[snap.snapshot_id] = snap

    def get_snapshot(self, snapshot_id: str) -> Optional[SourceSnapshot]:
        return self._snapshots.get(snapshot_id)

    def snapshots_by_source(self, source_id: str) -> list[SourceSnapshot]:
        return [s for s in self._snapshots.values() if s.source_id == source_id]

    def record_event(self, event: CaptureEvent) -> None:
        self._events.append(event)

    def events(self) -> list[CaptureEvent]:
        return list(self._events)

    def attempt_mutation(self, snapshot_id: str) -> None:
        """An attempted in-place mutation is recorded and REJECTED (fail-closed)."""
        self._mutations.append(snapshot_id)
        raise ValueError(
            f"SourceSnapshot is immutable; correction requires a NEW snapshot, "
            f"not an in-place update to {snapshot_id}"
        )


def build_snapshot(
    *,
    snapshot_id: str,
    source_id: str,
    resource_type: str,
    external_resource_id: str,
    canonical_url: str,
    request_id: str,
    retrieved_at: str,
    raw_object_uri: str,
    raw_bytes: bytes,
    adapter_name: str,
    adapter_version: str,
    capture_method: CaptureMethod,
    tenant_id: Optional[str] = None,
    http_status: Optional[int] = None,
    http_headers_subset: Optional[dict] = None,
    content_type: Optional[str] = None,
    previous_snapshot_id: Optional[str] = None,
    revision_key: Optional[str] = None,
    raw_hash_algorithm: str = "sha256",
) -> SourceSnapshot:
    """Deterministically derive the raw_hash from the raw bytes."""
    h = sha256_hex(raw_bytes) if raw_hash_algorithm == "sha256" else _unsupported(raw_hash_algorithm)
    return SourceSnapshot(
        snapshot_id=snapshot_id,
        source_id=source_id,
        tenant_id=tenant_id,
        resource_type=resource_type,
        external_resource_id=external_resource_id,
        canonical_url=canonical_url,
        request_id=request_id,
        request_fingerprint=f"req:{request_id}",
        retrieved_at=retrieved_at,
        source_effective_at=None,
        source_published_at=None,
        http_status=http_status,
        http_headers_subset=http_headers_subset or {},
        content_type=content_type,
        content_length=len(raw_bytes),
        raw_object_uri=raw_object_uri,
        raw_hash=h,
        raw_hash_algorithm=raw_hash_algorithm,
        adapter_name=adapter_name,
        adapter_version=adapter_version,
        capture_method=capture_method,
        previous_snapshot_id=previous_snapshot_id,
        revision_key=revision_key,
        snapshot_status=SnapshotStatus.CAPTURED,
    )


def _unsupported(algo: str) -> str:
    raise ValueError(f"unsupported hash algorithm: {algo}")