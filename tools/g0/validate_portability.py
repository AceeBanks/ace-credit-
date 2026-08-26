"""B4.C23-C25 — Skill / model / privacy portability validator.

Fail-closed validation over three configs:

  * skill_boundaries.yaml: the six Personal domains, six CEO domains, shared
    low-level utilities, independent role prompts, progressive disclosure,
    SKILL-001/002;
  * model_independence.yaml: identity/model separation, MODEL-001..003;
  * privacy_scope.yaml: the six scope dimensions, four privacy classes, four
    deletion semantics, and the role-duplication rule.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    ValidationFailure,
    emit,
    finish,
    load_yaml,
)

AGENTS_CONFIG_DIR = Path("config/g0/agents")

PERSONAL_DOMAINS = {"INTAKE", "CLARIFICATION", "BRAINSTORMING",
                    "CLIENT_EXPLANATION", "MEMORY_CANDIDATE_CLASSIFICATION",
                    "FEEDBACK_CAPTURE"}
CEO_DOMAINS = {"OPERATIONAL_PLANNING", "TASK_DECOMPOSITION",
               "RESULT_SYNTHESIS", "FAILURE_RETRY_DECISIONS",
               "APPLICATION_WORKFLOW_CONTROL", "IMPROVEMENT_PROPOSAL_GENERATION"}
REQUIRED_SHARED = {"LOW_LEVEL_UTILITIES", "TYPED_CONTRACT_HELPERS"}
SCOPE_DIMENSIONS = {"USER", "TENANT", "ORGANIZATION", "PROJECT_APPLICATION",
                    "AGENT_ROLE", "PRIVACY_CLASS"}
PRIVACY_CLASSES = {"PUBLIC", "TENANT_PRIVATE", "TENANT_SHARED_APPROVED",
                   "RESTRICTED_SENSITIVE"}
DELETION_SEMANTICS = {
    "EXCLUDE_FROM_FUTURE_RETRIEVAL", "SUPERSEDE_OR_CORRECT",
    "REMOVE_USER_SPECIFIC_SUBJECT_TO_RETENTION_AUDIT",
    "PRESERVE_REQUIRED_CANONICAL_AUDIT_EVIDENCE_SEPARATELY",
}


def _load(name: str, errors: list[str]) -> dict | None:
    try:
        return load_yaml(AGENTS_CONFIG_DIR / name)
    except ValidationFailure as exc:
        errors.append(str(exc))
        return None


def main() -> int:
    errors: list[str] = []

    skills = _load("skill_boundaries.yaml", errors)
    if skills is not None:
        personal = set(skills.get("personal_skill_domains", []))
        ceo = set(skills.get("ceo_skill_domains", []))
        if personal != PERSONAL_DOMAINS:
            errors.append("personal_skill_domains must be exactly the six "
                          "frozen domains")
        if ceo != CEO_DOMAINS:
            errors.append("ceo_skill_domains must be exactly the six frozen "
                          "domains")
        if personal & ceo:
            errors.append("role skill domains must not overlap")
        shared = set(skills.get("shared_skills", []))
        if shared != REQUIRED_SHARED:
            errors.append("shared_skills must be exactly the low-level "
                          "utilities")
        if skills.get("role_prompts") != "INDEPENDENT":
            errors.append("role_prompts must be INDEPENDENT")
        pd = skills.get("progressive_disclosure", {})
        if pd.get("metadata_loading") != "LOAD_ROLE_SKILL_METADATA_BROADLY":
            errors.append("progressive_disclosure.metadata_loading must be "
                          "LOAD_ROLE_SKILL_METADATA_BROADLY")
        rules = {r.get("rule_id") for r in skills.get("rules", [])}
        if {"SKILL-001", "SKILL-002"} - rules:
            errors.append("skill rules must include SKILL-001 and SKILL-002")

    models = _load("model_independence.yaml", errors)
    if models is not None:
        sep = models.get("identity_separation", {})
        agent_ids = set(sep.get("agent_identity", []))
        model_exec = set(sep.get("model_execution", []))
        if agent_ids != {"PERSONAL_HERMES_IDENTITY", "CEO_HERMES_IDENTITY",
                         "WORKER_ROLE_IDENTITY"}:
            errors.append("agent_identity must be the three frozen identities")
        if model_exec != {"MODEL_PROVIDER", "MODEL_VERSION",
                          "RUNTIME_SESSION_ID"}:
            errors.append("model_execution must be the three frozen metadata "
                          "fields")
        if agent_ids & model_exec:
            errors.append("agent identity and model execution must not overlap")
        rules = {r.get("rule_id") for r in models.get("rules", [])}
        if {"MODEL-001", "MODEL-002", "MODEL-003"} - rules:
            errors.append("model rules must include MODEL-001..003")

    privacy = _load("privacy_scope.yaml", errors)
    if privacy is not None:
        dims = set(privacy.get("scope_dimensions", []))
        if dims != SCOPE_DIMENSIONS:
            errors.append(f"scope_dimensions must be exactly "
                          f"{sorted(SCOPE_DIMENSIONS)}")
        classes = set(privacy.get("privacy_classes", []))
        if classes != PRIVACY_CLASSES:
            errors.append(f"privacy_classes must be exactly "
                          f"{sorted(PRIVACY_CLASSES)}")
        semantics = set(privacy.get("deletion_semantics", []))
        if semantics != DELETION_SEMANTICS:
            errors.append(f"deletion_semantics must be exactly "
                          f"{sorted(DELETION_SEMANTICS)}")
        if not privacy.get("role_duplication_rule"):
            errors.append("role_duplication_rule must be declared")

    _, report = finish("portability", not errors, {
        "errors": errors,
        "configs": ["skill_boundaries", "model_independence", "privacy_scope"],
    })
    return emit(report)


if __name__ == "__main__":
    sys.exit(main())
