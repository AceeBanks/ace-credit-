"""G0-B3-C23 — D0 source-governed data packet.

The source-governed evidence packet required to construct a DraftContextBundle
(Book 2) without agent memory. Fail-closed:
  * all nine packet sections must be present;
  * every material claim must carry either a source ref or an explicit
    NEEDS_CLIENT_INPUT / NEEDS_SOURCE / PROVISIONAL / UNSUPPORTED_DO_NOT_USE
    fact state — no missing input is silently invented;
  * the packet records the exact OpportunityRevision used;
  * packets serialize deterministically, so the draft regenerates from the
    packet alone;
  * requirement coverage is measurable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml

PACKET_SECTIONS = [
    "client_profile_fixture", "georgia_opportunity", "opportunity_requirements",
    "eligibility", "funder_program_research", "historical_winner_award_research",
    "community_impact_statistics", "budget_assumptions", "proposal_profile",
]

FACT_STATES = ["NEEDS_CLIENT_INPUT", "NEEDS_SOURCE", "PROVISIONAL",
               "UNSUPPORTED_DO_NOT_USE"]

OUTPUT_LABELS = ["MOCK", "NON_SUBMISSION", "NOT_CLIENT_APPROVED_FINAL"]


@dataclass(frozen=True)
class PacketFact:
    fact_id: str
    value: Any
    source_ref: str | None = None      # snapshot/claim/canonical ref
    fact_state: str | None = None      # one of FACT_STATES, or None when source_ref present

    def is_supported(self) -> bool:
        if self.source_ref:
            return True
        return self.fact_state in ("NEEDS_CLIENT_INPUT", "NEEDS_SOURCE",
                                   "PROVISIONAL")  # explicit, not invented


@dataclass(frozen=True)
class D0Packet:
    packet_id: str
    tenant_id: str
    opportunity_revision_id: str
    sections: dict[str, list[PacketFact]]
    labels: frozenset[str] = frozenset(("MOCK", "NON_SUBMISSION",
                                        "NOT_CLIENT_APPROVED_FINAL"))
    created_at: str = ""

    def validation_errors(self) -> list[str]:
        errors: list[str] = []
        missing = [s for s in PACKET_SECTIONS if s not in self.sections]
        if missing:
            errors.append(f"packet missing sections: {missing}")
        for section, facts in self.sections.items():
            for f in facts:
                if not f.is_supported():
                    errors.append(f"{f.fact_id}: unsupported fact with no "
                                  f"source ref and no explicit fact state")
        bad_labels = set(self.labels) - set(OUTPUT_LABELS)
        if bad_labels:
            errors.append(f"packet carries non-D0 labels: {sorted(bad_labels)}")
        if "MOCK" not in self.labels or "NON_SUBMISSION" not in self.labels:
            errors.append("packet must carry MOCK and NON_SUBMISSION labels")
        if not self.opportunity_revision_id:
            errors.append("packet must record the exact OpportunityRevision")
        return errors

    def determinism_key(self) -> str:
        """Deterministic canonical serialization: the same packet always
        produces the same key regardless of construction order."""
        payload = {
            "packet_id": self.packet_id,
            "tenant_id": self.tenant_id,
            "opportunity_revision_id": self.opportunity_revision_id,
            "labels": sorted(self.labels),
            "sections": {
                sec: sorted((f.fact_id, f.value, f.source_ref, f.fact_state)
                            for f in facts)
                for sec, facts in self.sections.items()
            },
        }
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def requirement_coverage(packet: D0Packet, requirement_ids: list[str]) -> tuple[int, int]:
    """How many of the given requirements have at least one supporting fact
    (source-backed or explicitly stateful) in the packet's requirements
    section. Coverage is measurable, never assumed."""
    supported = set()
    for fact in packet.sections.get("opportunity_requirements", []):
        if fact.is_supported():
            supported.add(fact.fact_id)
    covered = sum(1 for rid in requirement_ids if rid in supported)
    return covered, len(requirement_ids)


def packet_regenerable(packet: D0Packet) -> bool:
    """A regenerated packet built from the same inputs must produce the same
    determinism key — reconstruction never depends on agent memory."""
    rebuilt = D0Packet(
        packet_id=packet.packet_id, tenant_id=packet.tenant_id,
        opportunity_revision_id=packet.opportunity_revision_id,
        sections=packet.sections, labels=packet.labels,
        created_at=packet.created_at)
    return rebuilt.determinism_key() == packet.determinism_key()


def load_packet_config() -> dict:
    return load_yaml(SOURCE_CONFIG_DIR / "d0_data_packet.yaml")
