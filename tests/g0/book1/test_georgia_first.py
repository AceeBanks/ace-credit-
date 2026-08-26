"""B1.C13 tests — Georgia-First Operating Assumption.

Georgia is the first client's operating state and the early proof-state
priority (Blueprint Amendment 001 supersedes any earlier California default).
The constitution must remain jurisdiction-agnostic:

- no constitutional clause (policy config or Book 1 constitution docs) may
  hard-code California (or any single state) as the first-state proof;
- the Georgia-first amendment is recorded as the governing source;
- source fetch, opportunity snapshot, winner research and application drafting
  are all legal at L2 (the early Georgia proof path).
"""
from __future__ import annotations

import re
from pathlib import Path

from prototype.g0.policy.evaluator import evaluate
from prototype.g0.policy.models import Actor, AuthorityLevel, Decision, PolicyContext
from prototype.g0.policy.registry import PolicyRegistry

_ROOT = Path(__file__).resolve().parents[3]

CONSTITUTION_DOCS = sorted((_ROOT / "docs/grant-sector/g0/01-constitution").glob("*.md"))
POLICY_CONFIGS = sorted((_ROOT / "config/g0/policy").glob("*.yaml"))

GEORGIA_AMENDMENT = (
    _ROOT / "docs/grant-sector/G0_BLUEPRINT_AMENDMENT_001_GEORGIA_FIRST_EARLY_DRAFTING.md"
)

_CALIFORNIA_PATTERN = re.compile(r"\bCalifornia\b|\bCA\b", re.IGNORECASE)


def test_georgia_amendment_exists_and_is_authoritative():
    assert GEORGIA_AMENDMENT.exists(), "Georgia-first amendment doc missing"
    source_map = (_ROOT / "docs/grant-sector/g0/01-constitution"
                  / "G0_B1_CONSTITUTION_SOURCE_MAP.md").read_text(encoding="utf-8")
    assert "GEORGIA_FIRST" in source_map, "B1.C13 not wired into constitution source map"


def test_no_constitution_clause_hard_codes_california():
    """LAW: jurisdiction-agnostic product model; Georgia is proof priority only."""
    offenders = []
    for path in CONSTITUTION_DOCS + POLICY_CONFIGS:
        text = path.read_text(encoding="utf-8")
        for m in _CALIFORNIA_PATTERN.finditer(text):
            offenders.append(f"{path.name}:{text[:m.start()].count(chr(10)) + 1}")
    assert not offenders, f"California hard-coded in constitution/policy: {offenders}"


def test_contradiction_cd001_resolved():
    """California-first vs Georgia-first contradiction is closed (P1 RESOLVED)."""
    ledger = (_ROOT / "config/g0/ratification/contradiction_ledger.yaml").read_text(
        encoding="utf-8")
    assert "CD-001" in ledger
    assert "RESOLVED" in ledger.split("contradiction_id: CD-001")[1].split(
        "contradiction_id:")[0]


def test_l2_georgia_proof_path_is_legal():
    """source fetch, snapshot, winner research, drafting all legal at L2."""
    reg = PolicyRegistry.load()
    ceo = Actor("ceo-1", "ACTOR-HERMES-CEO", ("tenant-alpha",), AuthorityLevel.L2)

    def legal(cid: str, resource_type: str, *, project: str | None = "proj-1") -> bool:
        r = evaluate(reg, ceo, cid, PolicyContext(
            tenant_id="tenant-alpha", project_id=project, resource_type=resource_type))
        return r.decision in (Decision.ALLOW, Decision.REQUIRE_APPROVAL)

    assert legal("opportunity.fetch", "opportunity")          # source fetch
    assert legal("opportunity.snapshot", "opportunity")       # snapshot
    assert legal("research.winner", "research_pack")          # winner research
    assert legal("application.draft_full_proposal", "application_draft")


def test_georgia_lane_capabilities_exist_at_l2():
    """Registry evidence: the Georgia proof lane is fully typed at L2."""
    reg = PolicyRegistry.load()
    for cid in ("opportunity.search", "opportunity.fetch", "opportunity.snapshot",
                "research.winner", "application.create_draft_project",
                "application.draft_section"):
        cap = reg.get_capability(cid)
        assert cap is not None, cid
        assert cap.phase_status == "ENABLED", cid
        assert AuthorityLevel.rank(cap.minimum_level) <= AuthorityLevel.rank(
            AuthorityLevel.L2), cid
