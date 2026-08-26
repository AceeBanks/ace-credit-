"""G0-B3-C8 — Source precedence (fact-class × authority) resolver.

Determines which source governs a fact class when sources disagree. Authority
is ALWAYS fact class × source class via an explicit, tested precedence chain;
a higher generic source tier never outranks a specialized authoritative source
for the fact it governs.

Equal-authority conflict: NO automatic last-write-wins. Two claims at the same
resolved authority disagreeing -> CONFLICTED unless a temporal
(source_effective_at) rule resolves it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ConflictResolution(Enum):
    RESOLVED = "RESOLVED"
    CONFLICTED = "CONFLICTED"


@dataclass
class Resolution:
    winner: Optional["Claim"] = None
    resolution: ConflictResolution = ConflictResolution.RESOLVED

    @property
    def resolved(self) -> bool:
        return self.resolution == ConflictResolution.RESOLVED


@dataclass(frozen=True)
class Claim:
    claim_id: str
    fact_class: str
    source_class: str
    source_id: str
    source_effective_at: Optional[str] = None
    value: object = None

    def authority_key(self) -> tuple[str, str]:
        return (self.fact_class, self.source_class)


def source_rank(fact_class: str, source_class: str, matrix: dict) -> int:
    """Position of source_class within the fact's precedence chain.

    Each stage in the chain is a list of {label: {source_classes: [...]}} maps.
    The rank is the lowest (most authoritative) stage index that contains the
    source class. Ungoverned source classes get the lowest precedence.
    """
    chain = matrix.get(fact_class)
    if not chain:
        return len(matrix)
    for idx, stage in enumerate(chain):
        # each stage is a list of {label: {source_classes: [...]}} maps
        entries = stage if isinstance(stage, list) else [stage]
        for _entry in entries:
            for _label, body in _entry.items():
                if source_class in body.get("source_classes", []):
                    return idx
    return len(chain) + 1


def resolve(claims: list[Claim], matrix: dict) -> Resolution:
    """Pick the controlling claim, failing to CONFLICTED on equal-authority
    disagreement unless a temporal (source_effective_at) rule resolves it."""
    if not claims:
        return Resolution(None, ConflictResolution.RESOLVED)
    ranks = {c.claim_id: source_rank(c.fact_class, c.source_class, matrix)
             for c in claims}
    best_rank = min(ranks.values())
    best = [c for c in claims if ranks[c.claim_id] == best_rank]
    values = {c.value for c in best}
    if len(values) == 1:
        return Resolution(best[0], ConflictResolution.RESOLVED)
    # Equal authority, disagreeing values: try temporal resolution (effective date).
    dated = [c for c in best if c.source_effective_at is not None]
    if dated:
        latest = max(dated, key=lambda c: c.source_effective_at or "")
        if all(latest.source_effective_at > (o.source_effective_at or "")
               for o in best if o is not latest):
            return Resolution(latest, ConflictResolution.RESOLVED)
    return Resolution(None, ConflictResolution.CONFLICTED)


def client_controls(fact_class: str, client_controlled: set[str]) -> bool:
    return fact_class in client_controlled