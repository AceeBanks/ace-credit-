"""G1 Wave 1 — object storage abstraction.

S3-compatible interface; local-filesystem implementation for dev/CI.
Canonical metadata lives in Postgres (Store); objects are content/version
identifiable payloads keyed by (kind, id, version).

The abstraction keeps the S3 path open without a cloud dependency in dev.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


class ObjectStore:
    def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Store payload, return its content hash."""
        raise NotImplementedError

    def get(self, key: str) -> bytes | None:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        raise NotImplementedError


class LocalObjectStore(ObjectStore):
    """Filesystem-backed store: ./g1-objects/<kind>/<id>/v<n>.<ext>."""

    def __init__(self, root: str | Path = "g1-objects"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # key is a relative path like "snapshots/snap_1/v1.pdf"; forbid
        # path traversal
        p = (self.root / key).resolve()
        if not str(p).startswith(str(self.root.resolve())):
            raise ValueError(f"invalid object key {key!r}")
        return p

    def put(self, key: str, data: bytes,
            content_type: str = "application/octet-stream") -> str:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def get(self, key: str) -> bytes | None:
        p = self._path(key)
        if not p.exists():
            return None
        return p.read_bytes()

    def delete(self, key: str) -> bool:
        p = self._path(key)
        if p.exists():
            p.unlink()
            return True
        return False
