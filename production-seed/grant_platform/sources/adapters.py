"""G1 Wave 2 — governed source adapters.

Source Adapter Law: every source must register, fetch, snapshot,
hash/version, normalize, retain provenance, classify authority, and detect
amendments. External source content remains untrusted — crawlers/parsers
never outrank official solicitation truth.

Status is honest and explicit per adapter:
- LIVE: real endpoint exercised
- DEV: interface + fixture-backed fetch (no network in CI)
- MOCK: simulated payload for tests

Snapshots are immutable and content-addressed; a change produces a NEW
snapshot, never a mutation (Book 5 law).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


AUTHORITY_CLASSES = ("OFFICIAL_SOLICITATION", "GOVERNMENT_STATISTIC",
                     "FUNDER_RECORD", "RECIPIENT_RECORD", "REFERENCE")


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    name: str
    status: str                  # LIVE | DEV | MOCK
    authority_class: str
    endpoint: str | None = None


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    source_id: str
    tenant_id: str
    resource_type: str
    external_resource_id: str
    canonical_url: str
    content_hash: str
    retrieved_at: str
    payload_ref: str             # object storage ref
    raw_bytes_hash: str = ""
    normalized: dict = field(default_factory=dict)


class SourceError(Exception):
    pass


class SourceRegistry:
    """Project-owned registry of governed sources. Unknown sources are
    denied; no caller-supplied arbitrary endpoint."""

    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}

    def register(self, rec: SourceRecord) -> None:
        self._sources[rec.source_id] = rec

    def get(self, source_id: str) -> SourceRecord:
        if source_id not in self._sources:
            raise SourceError(f"unknown source {source_id}")
        return self._sources[source_id]

    def all(self) -> list[SourceRecord]:
        return list(self._sources.values())


class BaseSourceAdapter:
    """Fetch -> snapshot contract. The fetch callable is bound at
    construction (network in DEV/LIVE lanes; fixture callable in CI)."""

    source_id = "base"

    def __init__(self, registry: SourceRegistry,
                 fetch: Callable[[str], tuple[bytes, str]],
                 authority_class: str,
                 status: str = "DEV"):
        self.registry = registry
        self.fetch = fetch
        self.status = status
        registry.register(SourceRecord(
            source_id=self.source_id, name=self.source_id,
            status=status, authority_class=authority_class))

    def capture(self, tenant_id: str, resource_type: str,
                external_resource_id: str, canonical_url: str,
                normalize: Callable[[bytes], dict] | None = None) -> Snapshot:
        """Fetch, hash, normalize, and emit an immutable snapshot."""
        rec = self.registry.get(self.source_id)
        raw, payload_ref = self.fetch(canonical_url)
        raw_hash = sha256_hex(raw)
        normalized = normalize(raw) if normalize else {}
        snap = Snapshot(
            snapshot_id=f"snap-{self.source_id}-{raw_hash[:12]}",
            source_id=self.source_id, tenant_id=tenant_id,
            resource_type=resource_type,
            external_resource_id=external_resource_id,
            canonical_url=canonical_url, content_hash=raw_hash,
            retrieved_at=_now(), payload_ref=payload_ref,
            raw_bytes_hash=raw_hash, normalized=normalized)
        return snap


class GrantsGovAdapter(BaseSourceAdapter):
    """Grants.gov / Simpler opportunity adapter (DEV: interface +
    fixture-backed; LIVE when a real feed is configured)."""

    source_id = "grants_gov"

    def __init__(self, registry: SourceRegistry,
                 fetch: Callable[[str], tuple[bytes, str]] | None = None,
                 status: str = "DEV"):
        if fetch is None:
            fetch = self._dev_fetch
        super().__init__(registry, fetch,
                         authority_class="OFFICIAL_SOLICITATION",
                         status=status)

    @staticmethod
    def _dev_fetch(url: str) -> tuple[bytes, str]:
        # fixture-backed development fetch: deterministic, no network
        body = (
            '{"opportunity_id":"opp_ga_501","title":"Georgia Rural '
            'Community Impact Grant FY2026","deadline":"2026-10-15",'
            '"funding_ceiling":50000}').encode()
        return body, "dev:fixture:grants_gov"


class GeorgiaSourceAdapter(BaseSourceAdapter):
    """Georgia state sources (DEV)."""

    source_id = "georgia_state"

    def __init__(self, registry: SourceRegistry,
                 fetch: Callable[[str], tuple[bytes, str]] | None = None,
                 status: str = "DEV"):
        if fetch is None:
            fetch = self._dev_fetch
        super().__init__(registry, fetch,
                         authority_class="OFFICIAL_SOLICITATION",
                         status=status)

    @staticmethod
    def _dev_fetch(url: str) -> tuple[bytes, str]:
        body = b'{"state":"Georgia","program":"Rural Community Impact"}'
        return body, "dev:fixture:georgia"


class USAspendingAdapter(BaseSourceAdapter):
    """USAspending funder/recipient records (DEV)."""

    source_id = "usaspending"

    def __init__(self, registry: SourceRegistry,
                 fetch: Callable[[str], tuple[bytes, str]] | None = None,
                 status: str = "DEV"):
        if fetch is None:
            fetch = self._dev_fetch
        super().__init__(registry, fetch,
                         authority_class="FUNDER_RECORD", status=status)

    @staticmethod
    def _dev_fetch(url: str) -> tuple[bytes, str]:
        body = b'{"funder":"State of Georgia","award_count":12}'
        return body, "dev:fixture:usaspending"


class CensusCommunityAdapter(BaseSourceAdapter):
    """Census / community statistics (DEV)."""

    source_id = "census_community"

    def __init__(self, registry: SourceRegistry,
                 fetch: Callable[[str], tuple[bytes, str]] | None = None,
                 status: str = "DEV"):
        if fetch is None:
            fetch = self._dev_fetch
        super().__init__(registry, fetch,
                         authority_class="GOVERNMENT_STATISTIC",
                         status=status)

    @staticmethod
    def _dev_fetch(url: str) -> tuple[bytes, str]:
        body = b'{"county":"Dade","poverty_rate_pct":18.2,"year":2023}'
        return body, "dev:fixture:census"
