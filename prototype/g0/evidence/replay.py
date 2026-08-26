"""B5.C8 — Temporal replay prototype.

Three modes that are never conflated:
  * HISTORICAL_EXACT — exact pinned inputs/configs of the original decision
    (current state can NEVER substitute);
  * HISTORICAL_REEVALUATE — historical evidence, current evaluator/policy;
  * CURRENT_REEVALUATE — current evidence + current evaluator, to assess
    whether the old decision remains valid.

EVID-LAW-007: replay never silently substitutes current facts. A missing
historical dependency is a P0 integrity failure, never a silent skip.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REPLAY_MODES = ("HISTORICAL_EXACT", "HISTORICAL_REEVALUATE",
                "CURRENT_REEVALUATE")


class ReplayError(ValueError):
    """Raised when a replay would violate historical integrity."""


@dataclass
class ReplayPacket:
    decision: dict
    pinned_input_refs: list[dict]
    configuration_refs: list[str]
    policy_refs: list[str]
    source_snapshot_refs: list[str]
    engine_metadata: dict
    mode: str = "HISTORICAL_EXACT"

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": dict(self.decision),
            "pinned_input_refs": list(self.pinned_input_refs),
            "configuration_refs": list(self.configuration_refs),
            "policy_refs": list(self.policy_refs),
            "source_snapshot_refs": list(self.source_snapshot_refs),
            "engine_metadata": dict(self.engine_metadata),
            "mode": self.mode,
        }


DETERMINISTIC_DECISION_TYPES = (
    "ELIGIBILITY", "REQUIREMENT_COVERAGE", "BUDGET_VALIDATION",
    "FACT_PROMOTION", "MATCH_RANKING", "CONFLICT_RESOLUTION")


def require_engine_metadata(decision: dict) -> None:
    """DEC-002/ADV-34: deterministic decisions must pin engine/model
    metadata before replay; missing metadata fails closed."""
    if decision.get("decision_type") in DETERMINISTIC_DECISION_TYPES \
            and not decision.get("model_or_engine_ref"):
        raise ReplayError(
            f"missing historical engine metadata for deterministic decision "
            f"{decision.get('decision_id')} (DEC-002)")


def build_replay_packet(*, decision: dict,
                        source_snapshot_resolver) -> ReplayPacket:
    """Assemble the replay packet; every pinned input must resolve to a
    historical object or the packet fails integrity (P0)."""
    require_engine_metadata(decision)
    pinned = decision.get("input_refs", [])
    snapshot_refs = []
    for inp in pinned:
        ref = inp.get("ref")
        resolved = source_snapshot_resolver(ref, revision=inp.get("version_or_revision_id"))
        if resolved is None:
            raise ReplayError(
                f"missing historical dependency {ref!r} — P0 integrity "
                "failure; no reconstruction will be fabricated")
        snap = resolved.get("snapshot_ref") or resolved.get("ref")
        if snap:
            snapshot_refs.append(snap)
    return ReplayPacket(
        decision=decision, pinned_input_refs=list(pinned),
        configuration_refs=decision.get("configuration_refs", []),
        policy_refs=[decision.get("policy_ref", "")],
        source_snapshot_refs=snapshot_refs,
        engine_metadata={
            "model_or_engine_ref": decision.get("model_or_engine_ref"),
            "policy_ref": decision.get("policy_ref"),
        })


def replay_deterministic(packet: ReplayPacket, evaluator) -> dict:
    """Re-run a deterministic decision from the pinned packet."""
    return evaluator(packet.to_dict())


def historical_exact_inputs(packet: ReplayPacket) -> list[dict]:
    """HISTORICAL_EXACT returns the exact pinned inputs — current state is
    never consulted (EVID-LAW-007)."""
    return [dict(i) for i in packet.pinned_input_refs]


def current_state_must_not_substitute(packet: ReplayPacket,
                                      current_inputs: list[dict]) -> None:
    """Guard: replacing a historical input with its current version must
    fail for HISTORICAL_EXACT."""
    historical_refs = {(i["ref"], i.get("version_or_revision_id"))
                       for i in packet.pinned_input_refs}
    current_refs = {(i["ref"], i.get("version_or_revision_id"))
                    for i in current_inputs}
    substituted = current_refs - historical_refs
    if substituted and packet.mode == "HISTORICAL_EXACT":
        raise ReplayError(
            f"HISTORICAL_EXACT replay cannot substitute current state for: "
            f"{sorted(substituted)}")
