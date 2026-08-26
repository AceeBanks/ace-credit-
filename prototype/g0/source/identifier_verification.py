"""G0-B3-C14 — External identifier verification protocol.

Operationalizes the Book 2 identifier model against external sources. An ID
claimed in chat never becomes verified automatically; verification requires a
verifying source snapshot + method. Conflicting verified IDs trigger identity
conflict; the same value in different namespaces remains distinct.

Verification states:
  UNVERIFIED, USER_ASSERTED, SOURCE_ASSERTED, VERIFIED_OFFICIAL,
  CONFLICTED, EXPIRED/SUPERSEDED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VerificationState(Enum):
    UNVERIFIED = "UNVERIFIED"
    USER_ASSERTED = "USER_ASSERTED"
    SOURCE_ASSERTED = "SOURCE_ASSERTED"
    VERIFIED_OFFICIAL = "VERIFIED_OFFICIAL"
    CONFLICTED = "CONFLICTED"
    EXPIRED_SUPERSEDED = "EXPIRED/SUPERSEDED"


class VerificationMethod(Enum):
    USER_PROVIDED = "USER_PROVIDED"
    SOURCE_MATCH = "SOURCE_MATCH"
    OFFICIAL_RECORD_MATCH = "OFFICIAL_RECORD_MATCH"
    GEOGRAPHY_RESOLVER = "GEOGRAPHY_RESOLVER"
    ISSUER_PORTAL = "ISSUER_PORTAL"


@dataclass
class VerificationEvent:
    identifier_namespace: str
    value: str
    entity_id: str
    verifying_snapshot_id: Optional[str]
    method: VerificationMethod
    effective_period: tuple[str, str | None]  # (start, end|None)
    result: VerificationState


class IdentifierRegistry:
    def __init__(self) -> None:
        self._events: dict[str, VerificationEvent] = {}
        # entity_id -> {namespace: [events]}
        self._by_entity: dict[str, dict[str, list[VerificationEvent]]] = {}
        self._identity_conflicts: list[str] = []

    def add(self, ev: VerificationEvent) -> None:
        key = self._event_key(ev)
        self._events[key] = ev
        self._by_entity.setdefault(ev.entity_id, {}).setdefault(
            ev.identifier_namespace, []).append(ev)
        self._check_conflicts(ev)

    def state(self, entity_id: str, namespace: str) -> VerificationState:
        events = self._by_entity.get(entity_id, {}).get(namespace, [])
        if not events:
            return VerificationState.UNVERIFIED
        current = max(events, key=lambda e: e.effective_period[0])
        return current.result

    def _event_key(self, ev: VerificationEvent) -> str:
        return f"{ev.entity_id}:{ev.identifier_namespace}:{ev.value}:{ev.method.value}"

    def _check_conflicts(self, new_ev: VerificationEvent) -> None:
        """Two differing VERIFIED values in the same namespace => identity conflict."""
        events = self._by_entity.get(new_ev.entity_id, {}).get(
            new_ev.identifier_namespace, [])
        verified = {e.value for e in events
                    if e.result in (VerificationState.VERIFIED_OFFICIAL,
                                    VerificationState.SOURCE_ASSERTED,
                                    VerificationState.USER_ASSERTED)}
        if len(verified) > 1:
            self._identity_conflicts.append(
                f"identity conflict on {new_ev.entity_id}/{new_ev.identifier_namespace}")


def chat_claim_is_not_verified() -> VerificationState:
    """An external ID claimed in chat is UNVERIFIED, never auto-verified."""
    return VerificationState.UNVERIFIED