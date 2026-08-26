"""G0-B6 — Shared security dataclasses (principal)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Principal:
    principal_id: str
    principal_type: str
    subject_id: str
    status: str
    authentication_method: str
    tenant_memberships: list[str] = field(default_factory=list)
    created_at: str = ""
    last_authenticated_at: str | None = None
    credential_class: str = "NONE"
    model_or_provider_ref: str | None = None
    parent_task_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "principal_id": self.principal_id,
            "principal_type": self.principal_type,
            "subject_id": self.subject_id,
            "status": self.status,
            "authentication_method": self.authentication_method,
            "tenant_memberships": list(self.tenant_memberships),
            "created_at": self.created_at,
            "last_authenticated_at": self.last_authenticated_at,
            "credential_class": self.credential_class,
            "model_or_provider_ref": self.model_or_provider_ref,
            "parent_task_id": self.parent_task_id,
        }
