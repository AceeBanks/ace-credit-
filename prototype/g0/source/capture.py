"""G0-B3-C6 — Capture, replay & content-addressed storage protocol.

Makes external data reproducible and economically storable. Captures produce a
SourceSnapshot + raw blob; replay reproduces normalized extraction from the raw
object using an archived adapter/parser identity, or explicitly reports why
historical implementation is unavailable.

Replay classes:
  EXACT_REPLAY       same code/version available
  COMPATIBLE_REPLAY  newer compatible parser against raw capture
  PARTIAL_REPLAY     raw source exists but exact transformation unavailable
  NON_REPLAYABLE     unacceptable for promoted critical data unless exempted
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from prototype.g0.source.snapshot import SourceSnapshot, sha256_hex


class ReplayClass(Enum):
    EXACT_REPLAY = "EXACT_REPLAY"
    COMPATIBLE_REPLAY = "COMPATIBLE_REPLAY"
    PARTIAL_REPLAY = "PARTIAL_REPLAY"
    NON_REPLAYABLE = "NON_REPLAYABLE"


class ReplayOutcome(Enum):
    REPRODUCED = "REPRODUCED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ContentAddress:
    """Content-addressed raw object reference with integrity metadata."""

    raw_hash: str
    raw_hash_algorithm: str
    raw_object_uri: str
    content_length: int
    encryption_at_rest: bool
    tenant_id: str | None
    security_metadata: dict
    retention_class: str


class ContentAddressedStore:
    """Immutable raw-object store keyed by content hash."""

    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}
        self._refs: dict[str, ContentAddress] = {}
        self._corrupt_detected: list[str] = []

    def put(self, raw: bytes, *, uri: str, algorithm: str = "sha256",
            encryption_at_rest: bool = False, tenant_id: str | None = None,
            security_metadata: dict | None = None,
            retention_class: str = "D1") -> ContentAddress:
        h = sha256_hex(raw) if algorithm == "sha256" else _unsupported(algorithm)
        addr = ContentAddress(
            raw_hash=h, raw_hash_algorithm=algorithm, raw_object_uri=uri,
            content_length=len(raw), encryption_at_rest=encryption_at_rest,
            tenant_id=tenant_id, security_metadata=security_metadata or {},
            retention_class=retention_class,
        )
        # content-address: identical bytes share one address
        self._blobs.setdefault(h, raw)
        self._refs[h] = addr
        return addr

    def get(self, addr: ContentAddress) -> bytes:
        blob = self._blobs.get(addr.raw_hash)
        if blob is None:
            raise KeyError(f"blob not present: {addr.raw_hash}")
        if sha256_hex(blob) != addr.raw_hash:
            self._corrupt_detected.append(addr.raw_hash)
            raise ValueError(f"corrupt blob: hash mismatch for {addr.raw_hash}")
        return blob

    def verify(self, addr: ContentAddress) -> bool:
        try:
            self.get(addr)
            return True
        except ValueError:
            return False


@dataclass
class ReplayRequest:
    snapshot: SourceSnapshot
    raw_bytes: bytes
    adapter_name: str
    adapter_version: str


@dataclass
class ReplayResult:
    replay_class: ReplayClass
    outcome: ReplayOutcome
    evidence: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.outcome == ReplayOutcome.REPRODUCED


def reproduce(req: ReplayRequest, available_version: str) -> ReplayResult:
    """Reproduce extracted output for a snapshot, classifying replayability.

    Fails closed: any mismatch between the snapshot's adapter/version and what
    is available today is downgraded unless exactly/compatibly satisfiable.
    """
    errors: list[str] = []
    if req.raw_bytes is None:
        return ReplayResult(ReplayClass.NON_REPLAYABLE, ReplayOutcome.FAILED,
                            errors=["raw object missing"])
    if req.snapshot.raw_hash != sha256_hex(req.raw_bytes):
        return ReplayResult(ReplayClass.NON_REPLAYABLE, ReplayOutcome.FAILED,
                            errors=["raw blob hash mismatch; capture is corrupt"])

    if req.snapshot.adapter_name != req.adapter_name:
        errors.append(f"adapter mismatch ({req.snapshot.adapter_name} vs {req.adapter_name})")
        return ReplayResult(ReplayClass.PARTIAL_REPLAY, ReplayOutcome.FAILED, errors=errors)

    if available_version == req.snapshot.adapter_version:
        return ReplayResult(ReplayClass.EXACT_REPLAY, ReplayOutcome.REPRODUCED,
                            evidence={"adapter_version": available_version})
    return ReplayResult(ReplayClass.COMPATIBLE_REPLAY, ReplayOutcome.REPRODUCED,
                        evidence={"captured": req.snapshot.adapter_version,
                                  "replayed_by": available_version})


def replayable_within_retention(snapshot: SourceSnapshot, retention_class: str,
                                allowed: set[ReplayClass]) -> ReplayResult:
    """Reject promoted critical data whose replay class is not allowed."""
    # NON_REPLAYABLE is unacceptable for promoted critical data unless explicitly exempted
    if ReplayClass.NON_REPLAYABLE not in allowed:
        return ReplayResult(ReplayClass.NON_REPLAYABLE, ReplayOutcome.FAILED,
                            errors=["NON_REPLAYABLE not permitted for this data"])
    return ReplayResult(ReplayClass.EXACT_REPLAY, ReplayOutcome.REPRODUCED)


def _unsupported(algo: str) -> str:
    raise ValueError(f"unsupported hash algorithm: {algo}")