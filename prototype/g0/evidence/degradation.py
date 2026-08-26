"""G0-B5-C23 — Failure & degraded modes prototype.

Every optional component has explicit degraded behavior (DEG-001); every
integrity-critical component fails closed (DEG-002): no untraceable
production state from provenance-write failure, no fabricated reconstruction
from missing/corrupt history, no auto-promotion of conflicted facts when the
contradiction service is down. Degraded mode is recorded for audit (DEG-003).
"""
from __future__ import annotations

from typing import Any


class DegradationError(ValueError):
    """Raised when an integrity-critical operation cannot proceed."""


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "degraded_modes.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


class DegradationManager:
    """Tracks component health and enforces degraded/fail-closed behavior."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._available: dict[str, bool] = {
            c["id"]: True for c in self.policy["components"]}
        self._audit: list[dict] = []

    def component(self, component_id: str) -> dict:
        for c in self.policy["components"]:
            if c["id"] == component_id:
                return c
        raise ValueError(f"unknown component {component_id!r}")

    def set_available(self, component_id: str, available: bool) -> None:
        self.component(component_id)  # validate id
        self._available[component_id] = available

    def available(self, component_id: str) -> bool:
        return self._available.get(component_id, False)

    def degraded_mode(self, component_id: str, fallback_lane: str) -> None:
        """DEG-003: record the degraded mode for audit."""
        self._audit.append({"component": component_id, "mode": "DEGRADED",
                            "fallback_lane": fallback_lane})

    def audit_trail(self) -> list[dict]:
        return list(self._audit)

    # ---- OPTIONAL components: degrade, don't fail core ----

    def graph_projection_status(self) -> dict:
        if self.available("graph_projection"):
            return {"status": "OK"}
        self.degraded_mode("graph_projection", "explicit_substrate")
        return {"status": "DEGRADED",
                "behavior": self.component("graph_projection")[
                    "degraded_behavior"]}

    def vector_store_status(self) -> dict:
        if self.available("vector_store"):
            return {"status": "OK"}
        self.degraded_mode("vector_store", "exact_relational_fulltext")
        return {"status": "DEGRADED",
                "behavior": self.component("vector_store")[
                    "degraded_behavior"]}

    def semantica_status(self) -> dict:
        if self.available("semantica"):
            return {"status": "OK"}
        self.degraded_mode("semantica", "canonical_substrate")
        return {"status": "DEGRADED",
                "behavior": self.component("semantica")["degraded_behavior"]}

    # ---- INTEGRITY-CRITICAL components: fail closed ----

    def record_with_provenance(self, *, material: bool) -> None:
        """Provenance write failure on a material op must fail closed."""
        if material and not self.available("provenance_write"):
            raise DegradationError(
                "provenance write unavailable; material decision cannot "
                "produce untraceable state (DEG-002)")

    def replay(self, *, refs: list[str], corrupt: list[str]) -> dict:
        """Historical evidence missing/corrupt => integrity failure, never
        fabricated reconstruction."""
        if corrupt:
            raise DegradationError(
                f"historical evidence integrity failure for {corrupt}; "
                "reconstruction is never fabricated (DEG-002)")
        return {"refs": list(refs), "integrity": "OK"}

    def promote_conflicted(self, *, conflict_detected: bool) -> None:
        """Contradiction service down: conflicted facts are never promoted."""
        if conflict_detected and not self.available("contradiction_service"):
            raise DegradationError(
                "contradiction service unavailable; conflicted fact must "
                "not be auto-promoted (DEG-002)")
