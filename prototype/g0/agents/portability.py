"""B4.C23-C25 — Skill boundaries, model independence, privacy scope (prototype).

  * load_skill_set: Personal sessions load only Personal skill domains; CEO
    loads only CEO domains; shared utilities are low-level only;
  * provider_swap: changing the model preserves agent identity and memory
    namespaces; the model change is recorded as audit/sidechain metadata;
  * fallback_capability_check: a fallback model lacking a required
    structured-output/tool capability causes a controlled failure/degradation,
    never silent authority expansion;
  * privacy_delete: deletion excludes memory from future retrieval and is
    verified across namespaces — role duplication by refs means a deleted
    Personal record cannot resurface through a CEO copy.
"""
from __future__ import annotations

from dataclasses import dataclass, field

PERSONAL_SKILL_DOMAINS = {"INTAKE", "CLARIFICATION", "BRAINSTORMING",
                          "CLIENT_EXPLANATION",
                          "MEMORY_CANDIDATE_CLASSIFICATION", "FEEDBACK_CAPTURE"}
CEO_SKILL_DOMAINS = {"OPERATIONAL_PLANNING", "TASK_DECOMPOSITION",
                     "RESULT_SYNTHESIS", "FAILURE_RETRY_DECISIONS",
                     "APPLICATION_WORKFLOW_CONTROL",
                     "IMPROVEMENT_PROPOSAL_GENERATION"}
SHARED_SKILLS = {"LOW_LEVEL_UTILITIES", "TYPED_CONTRACT_HELPERS"}


class PortabilityError(ValueError):
    """Raised when a portability/privacy rule is violated."""


def load_skill_set(role: str) -> dict:
    """Progressive disclosure: metadata broadly, instructions on trigger."""
    if role == "PERSONAL_HERMES":
        domains = PERSONAL_SKILL_DOMAINS
    elif role == "CEO_HERMES":
        domains = CEO_SKILL_DOMAINS
    else:
        raise PortabilityError(f"unknown role {role}")
    return {
        "role": role,
        "domains": sorted(domains),
        "shared_utilities": sorted(SHARED_SKILLS),
        "full_instructions_loaded": False,  # metadata only
        "progressive_disclosure": True,
    }


def provider_swap(actor_identity: str, memory_namespaces: set[str],
                  old_model: str, new_model: str) -> dict:
    """Provider swap preserves logical actor identity and namespaces."""
    return {
        "actor_identity": actor_identity,  # unchanged
        "memory_namespaces": sorted(memory_namespaces),  # unchanged
        "old_model": old_model,
        "new_model": new_model,
        "recorded_in": "audit/sidechain",  # never in agent identity
        "identity_unchanged": True,
    }


def fallback_capability_check(required: set[str],
                              fallback_capabilities: set[str]) -> dict:
    """A fallback lacking a required capability must fail/degrade controlled."""
    missing = required - fallback_capabilities
    if missing:
        return {
            "ok": False,
            "missing": sorted(missing),
            "behavior": "CONTROLLED_DEGRADATION_OR_BLOCKED",
        }
    return {"ok": True, "missing": [], "behavior": "NORMAL"}


@dataclass
class ScopedMemoryStore:
    """Namespaces hold refs only; deletion in one role cannot be resurrected
    by another role's copy because copies do not exist."""
    namespace: str
    records: dict[str, dict] = field(default_factory=dict)

    def store(self, record: dict) -> None:
        self.records[record["memory_id"]] = record

    def retrieve(self, memory_id: str) -> dict | None:
        record = self.records.get(memory_id)
        if record and record.get("status") == "DELETED":
            return None
        return record

    def delete(self, memory_id: str, *, scope: dict) -> None:
        """EXCLUDE_FROM_FUTURE_RETRIEVAL + SUPERSEDE_OR_CORRECT semantics."""
        record = self.records.get(memory_id)
        if not record:
            raise PortabilityError(f"unknown memory {memory_id}")
        # scope check: deletion must match the record's own scope
        for dim, value in scope.items():
            if record.get(dim) != value:
                raise PortabilityError(
                    f"deletion scope mismatch on {dim}: "
                    f"{record.get(dim)} != {value}")
        record["status"] = "DELETED"


def verify_no_duplicate_resurrection(stores: dict[str, ScopedMemoryStore],
                                     memory_id: str) -> bool:
    """Deleted Personal memory must not remain retrievable via another role's
    store. Because stores hold refs (not copies), a DELETED record never
    resurfaces in another namespace."""
    for namespace, store in stores.items():
        record = store.records.get(memory_id)
        if record and record.get("status") != "DELETED":
            return False
    return True
