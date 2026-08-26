"""G0-B3-C4 — Source onboarding & governance protocol.

Governs the controlled promotion of a source from CANDIDATE to ENABLED.
Hard rule: an agent discovering a useful site may create a SourceCandidate or
research note, but may NOT automatically add that domain to production
allowlists. Promotion must flow through the staged protocol and be ENABLED
explicitly.

Fail-closed: every gate must pass; any unresolved stage blocks ENABLE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SourceStatus(Enum):
    CANDIDATE = "CANDIDATE"
    REVIEWING = "REVIEWING"
    FIXTURE_ONLY = "FIXTURE_ONLY"
    ENABLED = "ENABLED"
    DEGRADED = "DEGRADED"
    DISABLED = "DISABLED"
    RETIRED = "RETIRED"


# Ordered promotional gates, mirroring the constitution's onboarding protocol.
ONBOARDING_STAGES = [
    "identity_ownership_check",
    "terms_robots_access_review",
    "authority_classification",
    "data_shape_analysis",
    "adapter_capture_strategy",
    "fixture_capture",
    "schema_parser_tests",
    "rate_limit_failure_test",
    "security_prompt_injection_test",
    "source_health_policy",
    "enabled",
]


@dataclass
class SourceOnboardingPacket:
    """The onboarding packet a controlled source must carry."""

    source_id: str
    source_identity: str
    legal_access_notes: Optional[str] = None
    authority_fact_classes: list[str] = field(default_factory=list)
    example_resources: list[str] = field(default_factory=list)
    expected_ids: list[str] = field(default_factory=list)
    capture_approach: Optional[str] = None
    parser_approach: Optional[str] = None
    freshness_rule: Optional[str] = None
    failure_behavior: Optional[str] = None
    health_probes: list[str] = field(default_factory=list)
    test_fixture_refs: list[str] = field(default_factory=list)
    security_notes: Optional[str] = None
    operational_owner: Optional[str] = None


class SourceCandidate:
    """A discovered but NOT-yet-approved source.

    An agent may freely create these. Promoting to a production allowlist
    requires running the full onboarding protocol to ENABLED.
    """

    __slots__ = ("source_id", "discovered_by", "notes")

    def __init__(self, source_id: str, discovered_by: str, notes: str = ""):
        self.source_id = source_id
        self.discovered_by = discovered_by
        self.notes = notes


class SourceGovernor:
    """Tracks per-source onboarding state and enforces the staged protocol."""

    def __init__(self) -> None:
        self._statuses: dict[str, SourceStatus] = {}
        self._stages_passed: dict[str, set[str]] = {}
        self._packets: dict[str, SourceOnboardingPacket] = {}

    def register(self, source_id: str) -> None:
        if source_id in self._statuses:
            raise ValueError(f"source already registered: {source_id}")
        self._statuses[source_id] = SourceStatus.CANDIDATE
        self._stages_passed[source_id] = set()

    def status(self, source_id: str) -> SourceStatus:
        if source_id not in self._statuses:
            raise KeyError(f"unknown source: {source_id}")
        return self._statuses[source_id]

    def pass_stage(self, source_id: str, stage: str) -> None:
        if source_id not in self._statuses:
            raise KeyError(f"unknown source: {source_id}")
        if stage not in ONBOARDING_STAGES:
            raise ValueError(f"unknown stage: {stage}")
        self._stages_passed[source_id].add(stage)
        # Progress to REVIEWING once identity/ownership is confirmed.
        if stage == "identity_ownership_check" and self._statuses[source_id] == SourceStatus.CANDIDATE:
            self._statuses[source_id] = SourceStatus.REVIEWING

    def set_status(self, source_id: str, status: SourceStatus) -> None:
        if source_id not in self._statuses:
            raise KeyError(f"unknown source: {source_id}")
        self._statuses[source_id] = status

    def promote_to_enabled(self, source_id: str, packet: SourceOnboardingPacket) -> None:
        """ENABLE only if every onboarding gate has passed and a packet exists."""
        if source_id not in self._statuses:
            raise KeyError(f"unknown source: {source_id}")
        if self._statuses[source_id] == SourceStatus.RETIRED:
            raise ValueError("retired source cannot be enabled")
        if self._statuses[source_id] == SourceStatus.DISABLED:
            raise ValueError("disabled source cannot be enabled without explicit re-review")
        missing = [s for s in ONBOARDING_STAGES if s not in self._stages_passed[source_id]]
        if missing:
            raise ValueError(f"unreviewed source cannot be enabled; missing stages: {missing}")
        # A DISABLED->ENABLED path is allowed only if re-reviewed; we require the
        # caller to have passed the full gate set already (checked above) and
        # reset status accordingly.
        self._packets[source_id] = packet
        self._statuses[source_id] = SourceStatus.ENABLED

    def packet(self, source_id: str) -> Optional[SourceOnboardingPacket]:
        return self._packets.get(source_id)

    def can_promote_data(self, source_id: str, require_enabled: bool = True) -> bool:
        st = self._statuses.get(source_id)
        if st is None:
            return False
        if require_enabled:
            return st == SourceStatus.ENABLED
        return st in (SourceStatus.ENABLED, SourceStatus.DEGRADED)


def discover_source(source_id: str, discovered_by: str, notes: str = "") -> SourceCandidate:
    """The ONLY agent-permitted action on an unknown site: create a candidate."""
    return SourceCandidate(source_id=source_id, discovered_by=discovered_by, notes=notes)