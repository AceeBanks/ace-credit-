"""G0 Book 2 — B2.C7 state transition semantics.

Deterministic transition validation against the state machine catalog:
illegal transitions rejected; Phase 1 future states unreachable; capability /
authority / preconditions enforced. Same inputs -> same verdict, always.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransitionVerdict:
    allowed: bool
    reason: str = ""
    capability: str | None = None
    authority_level: str | None = None


def find_transition(spec: dict, current: str, target: str) -> dict | None:
    for t in spec.get("transitions", []):
        if t["from"] == current and t["to"] == target:
            return t
        if t["from"] == "ANY" and t["to"] == target:
            return t
        # reversed directed transitions are not automatic
    return None


def can_transition(spec: dict, current: str, target: str, *,
                   phase1: bool = True,
                   capability: str | None = None,
                   authority_level: str | None = None,
                   satisfied_preconditions: set[str] | None = None) -> TransitionVerdict:
    if target not in spec.get("states", []):
        return TransitionVerdict(False, f"unknown target state '{target}'")
    if current not in spec.get("states", []) and current != "ANY":
        return TransitionVerdict(False, f"unknown current state '{current}'")

    if phase1 and target in spec.get("future_states", []):
        return TransitionVerdict(False, f"'{target}' is a Phase 1 future state (unreachable)")

    t = find_transition(spec, current, target)
    if t is None:
        return TransitionVerdict(False, f"no transition {current}->{target}")

    required_cap = t.get("capability")
    if required_cap and capability is not None and capability != required_cap:
        return TransitionVerdict(False, f"requires capability '{required_cap}'",
                                 capability=required_cap, authority_level=t.get("authority_level"))
    if authority_level is not None:
        order = ["L0", "L1", "L2", "L3", "L4", "L5"]
        required_lvl = t.get("authority_level", "L0")
        if order.index(authority_level) < order.index(required_lvl):
            return TransitionVerdict(False,
                                     f"requires authority {required_lvl}",
                                     capability=required_cap,
                                     authority_level=t.get("authority_level"))
    for pre in t.get("preconditions", []):
        if satisfied_preconditions is not None and pre not in satisfied_preconditions:
            return TransitionVerdict(False, f"precondition '{pre}' unsatisfied",
                                     capability=required_cap,
                                     authority_level=t.get("authority_level"))
    return TransitionVerdict(True, "", capability=required_cap,
                             authority_level=t.get("authority_level"))


def submission_ready_gate(spec: dict, *, eligibility_ineligible: bool,
                          revision_stale: bool,
                          mandatory_unsatisfied: bool) -> bool:
    """B2.C7 11.3 gate: SUBMISSION_READY is blocked by stale eligibility,
    stale revision, or unsatisfied mandatory requirements."""
    return not (eligibility_ineligible or revision_stale or mandatory_unsatisfied)


def revision_stale_blocks(spec: dict, current: str) -> list[str]:
    """States whose transitions into them require revision_current, so a stale
    revision forces re-evaluation/review before those states."""
    blocked = []
    for t in spec.get("transitions", []):
        if t["to"] == current and "revision_current" in t.get("preconditions", []):
            blocked.append(f"{t['from']}->{current}")
    return blocked
