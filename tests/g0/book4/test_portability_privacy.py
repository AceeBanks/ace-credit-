"""B4.C23-C25 — Skill boundaries, model independence and privacy scope tests.

C23: Personal sessions do not load the CEO execution skill set by default;
unrelated grant skills do not consume active context.
C24: provider swap preserves canonical task/project state; a fallback lacking
a required capability produces controlled failure/degradation.
C25: deleted Personal memory does not remain retrievable merely because CEO
cached a copy; role duplication is minimized by refs. Plus validator
adversarial injections.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.portability import (  # noqa: E402
    PortabilityError,
    ScopedMemoryStore,
    fallback_capability_check,
    load_skill_set,
    provider_swap,
    verify_no_duplicate_resurrection,
)
from tools.g0.validate_portability import main as _validator_main  # noqa: F401


# --- C23 skill boundaries ----------------------------------------------------

def test_personal_session_does_not_load_ceo_skill_set():
    personal = load_skill_set("PERSONAL_HERMES")
    assert "OPERATIONAL_PLANNING" not in personal["domains"]
    assert "TASK_DECOMPOSITION" not in personal["domains"]
    assert "INTAKE" in personal["domains"]
    assert personal["full_instructions_loaded"] is False  # metadata only


def test_ceo_session_loads_ceo_skills_only():
    ceo = load_skill_set("CEO_HERMES")
    assert "OPERATIONAL_PLANNING" in ceo["domains"]
    assert "INTAKE" not in ceo["domains"]
    assert "CLIENT_EXPLANATION" not in ceo["domains"]


def test_unrelated_grant_skills_not_in_active_context():
    personal = load_skill_set("PERSONAL_HERMES")
    # only the six personal domains + low-level shared utilities are loaded
    assert personal["domains"] == sorted([
        "INTAKE", "CLARIFICATION", "BRAINSTORMING", "CLIENT_EXPLANATION",
        "MEMORY_CANDIDATE_CLASSIFICATION", "FEEDBACK_CAPTURE"])
    assert "grant_research" not in personal["domains"]
    assert personal["shared_utilities"] == sorted(
        ["LOW_LEVEL_UTILITIES", "TYPED_CONTRACT_HELPERS"])


def test_unknown_role_rejected():
    with pytest.raises(PortabilityError, match="unknown role"):
        load_skill_set("OMNIPOTENT_AGENT")


# --- C24 model independence --------------------------------------------------

def test_provider_swap_preserves_identity_and_state():
    swap = provider_swap(
        actor_identity="CEO_HERMES",
        memory_namespaces={"ceo_hermes"},
        old_model="provider-a/model-v1", new_model="provider-b/model-v2")
    assert swap["actor_identity"] == "CEO_HERMES"
    assert swap["memory_namespaces"] == ["ceo_hermes"]
    assert swap["identity_unchanged"] is True
    assert swap["recorded_in"] == "audit/sidechain"


def test_fallback_lacking_capability_degrades_controlled():
    result = fallback_capability_check(
        required={"research.funder", "structured_output_json"},
        fallback_capabilities={"research.funder"})
    assert result["ok"] is False
    assert result["missing"] == ["structured_output_json"]
    assert result["behavior"] == "CONTROLLED_DEGRADATION_OR_BLOCKED"
    # never silently expands authority or pretends the capability exists


def test_fallback_with_full_capability_ok():
    result = fallback_capability_check(
        required={"research.funder"},
        fallback_capabilities={"research.funder", "structured_output_json"})
    assert result["ok"] is True


# --- C25 privacy -------------------------------------------------------------

def test_deleted_personal_memory_not_retrievable_via_ceo_cache():
    personal = ScopedMemoryStore("personal_hermes")
    ceo = ScopedMemoryStore("ceo_hermes")
    personal.store({
        "memory_id": "mem-pref-9", "status": "ACTIVE",
        "user": "user-7", "tenant": "tenant-georgia-youth",
        "privacy_class": "TENANT_PRIVATE"})
    # CEO holds only a REF, never a copy
    ceo.store({"memory_id": "mem-pref-9-ref", "status": "ACTIVE",
               "ref": "mem-pref-9", "user": "user-7",
               "tenant": "tenant-georgia-youth",
               "privacy_class": "TENANT_PRIVATE"})
    personal.delete("mem-pref-9", scope={
        "user": "user-7", "tenant": "tenant-georgia-youth",
        "privacy_class": "TENANT_PRIVATE"})
    assert personal.retrieve("mem-pref-9") is None
    # the CEO ref does not resurrect the deleted record body
    assert verify_no_duplicate_resurrection(
        {"personal_hermes": personal, "ceo_hermes": ceo}, "mem-pref-9") is True


def test_delete_scope_mismatch_rejected():
    store = ScopedMemoryStore("personal_hermes")
    store.store({"memory_id": "mem-1", "status": "ACTIVE",
                 "user": "user-7", "tenant": "tenant-georgia-youth"})
    with pytest.raises(PortabilityError, match="scope mismatch"):
        store.delete("mem-1", scope={"user": "user-7",
                                     "tenant": "tenant-OTHER"})


def test_unknown_memory_delete_rejected():
    store = ScopedMemoryStore("personal_hermes")
    with pytest.raises(PortabilityError, match="unknown memory"):
        store.delete("ghost", scope={"user": "u"})


# --- validator adversarial ---------------------------------------------------

def test_portability_validator_passes():
    import subprocess
    proc = subprocess.run([sys.executable, "tools/g0/validate_portability.py"],
                          cwd=_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout
    assert '"status": "PASS"' in proc.stdout


def test_skill_overlap_fails(monkeypatch):
    import tools.g0.validate_portability as mod
    import yaml
    data = yaml.safe_load(
        (_ROOT / "config/g0/agents/skill_boundaries.yaml")
        .read_text(encoding="utf-8"))
    data["ceo_skill_domains"].append("INTAKE")
    monkeypatch.setattr(mod, "load_yaml",
                        lambda p: data if p.name == "skill_boundaries.yaml"
                        else yaml.safe_load(
                            (_ROOT / "config/g0/agents" / p.name)
                            .read_text(encoding="utf-8")))
    assert mod.main() == 1


def test_privacy_deletion_semantics_missing_fails(monkeypatch):
    import tools.g0.validate_portability as mod
    import yaml
    data = yaml.safe_load(
        (_ROOT / "config/g0/agents/privacy_scope.yaml")
        .read_text(encoding="utf-8"))
    data["deletion_semantics"] = ["EXCLUDE_FROM_FUTURE_RETRIEVAL"]
    monkeypatch.setattr(mod, "load_yaml",
                        lambda p: data if p.name == "privacy_scope.yaml"
                        else yaml.safe_load(
                            (_ROOT / "config/g0/agents" / p.name)
                            .read_text(encoding="utf-8")))
    assert mod.main() == 1
