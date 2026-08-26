"""G0 Book 1 policy prototype — policy registry.

Loads the machine-readable registers (actors, ladder, capabilities) into the
typed model space. The registry is the ONLY source the evaluator consults;
anything absent from it does not exist (LAW-B1-004/005).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.policy.models import (  # noqa: E402
    Actor,
    AuthorityLevel,
    Capability,
)

POLICY_DIR = _ROOT / "config" / "g0" / "policy"

_CEILING_MAP = {
    "ACTOR-HUMAN-CLIENT": AuthorityLevel.L5,       # human sovereign within role
    "ACTOR-HUMAN-ADMIN": AuthorityLevel.L5,
    "ACTOR-HERMES-PERSONAL": AuthorityLevel.L1,
    "ACTOR-HERMES-CEO": AuthorityLevel.L2,
    "ACTOR-WORKER": AuthorityLevel.L2,             # task-scoped; narrowed by TaskScope
    "ACTOR-DETERMINISTIC-SERVICE": AuthorityLevel.L3,
    "ACTOR-SOURCE-ADAPTER": AuthorityLevel.L2,
    "ACTOR-POLICY-ENGINE": AuthorityLevel.L3,
    "ACTOR-CANONICAL-DATABASE": AuthorityLevel.L3,
    "ACTOR-ARTIFACT-STORE": AuthorityLevel.L2,
    "ACTOR-EXTERNAL-INTEGRATION": AuthorityLevel.DISABLED,
    "ACTOR-OUTREACH-AGENT": AuthorityLevel.DISABLED,
    "ACTOR-SUBMISSION-AGENT": AuthorityLevel.DISABLED,
    "ACTOR-TRACKER-AGENT": AuthorityLevel.DISABLED,
}


class PolicyRegistry:
    """Immutable view over the policy-as-data registers."""

    def __init__(self, actors: dict[str, Actor], capabilities: dict[str, Capability]):
        self._actors = actors
        self._capabilities = capabilities

    @classmethod
    def load(cls, policy_dir: Path | None = None) -> "PolicyRegistry":
        base = Path(policy_dir) if policy_dir else POLICY_DIR
        actor_doc = yaml.safe_load((base / "actor_catalog.yaml").read_text(encoding="utf-8"))
        cap_doc = yaml.safe_load((base / "capability_registry.yaml").read_text(encoding="utf-8"))

        actors: dict[str, Actor] = {}
        for spec in actor_doc.get("actors", []):
            atype = spec["actor_type"]
            ceiling = (_CEILING_MAP.get(atype, AuthorityLevel.DISABLED)
                       if spec.get("status") != "ACTIVE"
                       else _CEILING_MAP.get(atype, AuthorityLevel.DISABLED))
            if spec.get("status") == "DISABLED" or spec.get("default_authority_ceiling") == "DISABLED":
                ceiling = AuthorityLevel.DISABLED
            actors[atype] = Actor(
                actor_id=atype,
                actor_type=atype,
                tenant_scopes=(),  # instance-level scopes come from runtime identity
                authority_ceiling=ceiling,
                status="ACTIVE" if spec.get("status") == "ACTIVE" else spec.get("status", "DISABLED"),
            )

        capabilities: dict[str, Capability] = {}
        for spec in cap_doc.get("capabilities", []):
            capabilities[spec["capability_id"]] = Capability(
                capability_id=spec["capability_id"],
                minimum_level=AuthorityLevel(spec["minimum_level"]),
                actor_types=tuple(spec.get("allowed_actor_types") or ()),
                resource_types=frozenset(spec.get("resource_types") or ()),
                approval_class=spec["approval_policy"],
                phase_status=spec["phase_status"],
                requires_tenant_scope=bool(spec.get("requires_tenant_scope", True)),
                requires_project_scope=bool(spec.get("requires_project_scope", False)),
                family=spec.get("family", ""),
            )
        return cls(actors, capabilities)

    def get_actor(self, actor_type: str) -> Actor | None:
        return self._actors.get(actor_type)

    def get_capability(self, capability_id: str) -> Capability | None:
        return self._capabilities.get(capability_id)

    @property
    def capability_count(self) -> int:
        return len(self._capabilities)
