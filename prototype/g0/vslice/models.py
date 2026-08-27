"""G0-B8-C2..C27 — vertical slice state model.

Typed, durable slice records that answer the Book 8 north-star questions.
Every record is JSON-serializable so the slice survives a cold restart and
can be reconstructed without chat history.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClientProfile:
    """C2 canonical client fixture (with evidence status on every value)."""
    organization_id: str
    legal_name: str
    display_name: str
    entity_type: str
    jurisdiction: str
    ein: str | None
    formation_year: str | None
    status_claim: str | None          # e.g. 501(c)(3)
    mission: str
    problem_addressed: str
    target_population: str
    service_geography: str
    program_activities: list[str]
    current_capacity: str | None
    expansion_goal: str
    requested_funding_use: str
    measurable_future_outcomes: list[str]
    known_historical_outcomes: list[str] = field(default_factory=list)
    unknown_items: list[str] = field(default_factory=list)
    evidence_status: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "ClientProfile":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


@dataclass
class SliceRecord:
    """One durable step of the vertical slice run."""
    stage: str
    record_id: str
    tenant_id: str
    project_id: str
    payload: dict = field(default_factory=dict)
    created_at: str = ""
    decision_refs: list[str] = field(default_factory=list)
    artifact_version_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> "SliceRecord":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})
