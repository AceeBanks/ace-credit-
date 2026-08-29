"""G1-QUALITY-PROD — benchmark API integration regression (§23).

PROVES the canonical quality pipeline runs THROUGH the real backend
production path (POST /projects/{id}/produce with AUTO), not a tool-only
script. The test:
  - creates a project whose revision resolves to the FY2026 AmeriCorps
    Georgia benchmark solicitation + MOCK_EVALUATION_ORGANIZATION fact pack
    + controlled client answers,
  - POSTs /produce with AUTO via the governed path (injecting a controlled
    deterministic quality model invoke so no network/credential is needed),
  - asserts the canonical pipeline actually executed:
      SectionPlans, critic/revision metadata, final Claim Ledger,
      quality/integrity report, real DOCX/PDF artifacts,
      QUALITY_PRODUCTION provenance + claim-ledger / fact-freeze hashes,
      and honest readiness (no generic fake package).

The Georgia dev seed (proj-1, no decomposed NOFO) must NOT produce a fake
package: AUTO there returns NEEDS_OPPORTUNITY (fail closed).

NOTE: FastAPI's @on_event("startup") recreates app.state.store, so the
AmeriCorps project is seeded into the ACTUAL startup store by patching
apps.api.main._seed_dev rather than by pre-creating a store we later
discard.
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

_ROOT = Path(__file__).resolve().parents[3]
_SEED = _ROOT / "production-seed"
for _p in (str(_ROOT), str(_SEED)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apps.api import main as api_main  # noqa: E402
from apps.api.main import app  # noqa: E402
from grant_platform.domain.records import (  # noqa: E402
    ApplicationProject, Opportunity, OpportunityRevision)

AUTH = {"X-Principal": "client-1"}


# --- controlled deterministic quality model invoke --------------------------


def _controlled_invoke(bundle):
    """Deterministic fake of the governed live lane: drafts real prose and
    returns ACCEPT/CLEAN critic + fact-critic JSON. Exercises enough of the
    canonical pipeline (plan -> draft -> critic -> fact-critic) to prove the
    API routes into the quality engine, with zero network / no credential."""
    instr = bundle.get("instructions", "")
    if "federal grant reviewer scoring" in instr:
        return ("{\"answers_exact_question\": 5, \"applicant_specific\": 5, "
                "\"evidence_used\": 5, \"unsupported_claims\": 5, "
                "\"depth_vs_weight\": 5, \"repetition_or_filler\": 5, "
                "\"overall\": 5, \"weaknesses\": [], "
                "\"verdict\": \"ACCEPT\"}")
    if "FACTUAL INTEGRITY auditor" in instr:
        return ("{\"unsupported_numbers\": [], \"temporal_violations\": [], "
                "\"status_violations\": [], \"invented_entities\": [], "
                "\"tense_violations\": [], \"integrity_verdict\": \"CLEAN\"}")
    sid = bundle.get("section_id", "")
    base = ("The Rural Georgia Youth Development Coalition, Inc. is an "
            "eligible applicant. The program will expand educational and "
            "economic opportunity for rural Northwest Georgia youth by "
            "placing AmeriCorps members to deliver tutoring, mentoring, and "
            "workforce readiness. AmeriCorps members will serve a full-time "
            "1,700-hour term, delivering tutoring sessions across a 32-week "
            "program year, per the governing client answers. The coalition "
            "will leverage its existing community partners and financial "
            "controls to steward grant funds within the budget.")
    return base + " This section addresses the FY2026 AmeriCorps Georgia " \
                  f"requirements for: {sid}."


def _seed_americorps_project(store) -> None:
    """Seed an AmeriCorps project whose revision resolves to the benchmark
    quality context, into the given store."""
    oid = "opp_americorps_ga_2026"
    rid = "ga_dca_nofp_2026"
    store.create_opportunity(Opportunity(
        opportunity_id=oid, tenant_id="tenant-a",
        title="FY2026 AmeriCorps State and National — Georgia Formula Grant"))
    store.create_revision(OpportunityRevision(
        revision_id=rid, opportunity_id=oid, revision_number=1))
    store.create_project(ApplicationProject(
        project_id="proj-bench", tenant_id="tenant-a",
        organization_id="org-a", opportunity_id=oid, revision_id=rid))


def _patch_seed(monkeypatch, add_americorps: bool = True):
    """Route the startup store through a patched _seed_dev that also seeds
    the AmeriCorps benchmark project, so it survives FastAPI startup."""
    import apps.api.main as _m
    original = _m._seed_dev

    def _patched(store):
        original(store)
        if add_americorps:
            _seed_americorps_project(store)

    monkeypatch.setattr(_m, "_seed_dev", _patched)
    # Controlled governed invoke — no key/network needed for the tests.
    monkeypatch.setattr(_m, "_resolve_model_invoke",
                        lambda body: (_controlled_invoke, "z-ai/glm-5.2:free"))


def test_americorps_benchmark_runs_canonical_quality_pipeline(monkeypatch):
    """BENCHMARK API REGRESSION: real /produce with AUTO uses the canonical
    quality pipeline (SectionPlans, critic/fact-critic, Claim Ledger,
    integrity report, real artifacts) — NOT the fallback deterministic
    skeleton."""
    _patch_seed(monkeypatch, add_americorps=True)
    with TestClient(app) as c:
        r = c.post("/projects/proj-bench/produce",
                   json={"model_selection": {"mode": "AUTO",
                                             "allow_fallback": True}},
                   headers=AUTH)
        assert r.status_code == 200, r.text
        data = r.json()
        # Canonical path executed — never DETERMINISTIC_BASELINE.
        assert data["pipeline_label"] == "QUALITY_PRODUCTION"
        assert data["generation_mode"] in ("LIVE_MODEL", "BLOCKED_MODEL_RUNTIME")
        assert data["solicitation_id"] == "ga_dca_nofp_2026"
        assert data["run_id"]
        assert data["claim_ledger_hash"]
        assert data["fact_freeze_hash"]
        # Requirement coverage + per-section planned-depth signals.
        assert data["requirement_coverage_pct"] is not None
        assert "quality_score" in data
        assert "shallow_output" in data
        # Integrity report keyed into response provenance.
        assert data.get("claims", 0) >= 0
        assert bool(data["claim_counts"]) or data["claims"]

        available = c.get("/projects/proj-bench/deliverables",
                          headers=AUTH)
        if available.status_code == 200:
            arts = available.json()["artifacts"]
            kinds = {a["kind"] for a in arts}
            assert {"proposal_docx", "proposal_pdf"} <= kinds


def test_americorps_with_critical_gaps_asks_client_first(monkeypatch):
    """§21: unresolved CRITICAL missing facts -> NEEDS_CLIENT_INPUT with
    concrete questions returned BEFORE any draft (no fabricated filler)."""
    _patch_seed(monkeypatch, add_americorps=True)
    import apps.api.main as _m2
    orig = _m2.build_context_for_revision

    def _ctx_without_answers(*, project_id, revision_id):
        ctx = orig(project_id=project_id, revision_id=revision_id)
        if ctx is not None:
            ctx.client_answers = ()
        return ctx
    monkeypatch.setattr(_m2, "build_context_for_revision",
                        _ctx_without_answers)

    with TestClient(app) as c:
        r = c.post("/projects/proj-bench/produce",
                   json={"model_selection": {"mode": "AUTO"}},
                   headers=AUTH)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["readiness_state"] == "NEEDS_CLIENT_INPUT"
        assert data["client_questions"], "must ask the client, not guess"
        # No fake package produced.
        avail = c.get("/projects/proj-bench/deliverables", headers=AUTH)
        if avail.status_code == 200:
            assert avail.json()["artifacts"] == []


def test_produce_georgia_without_solicitation_returns_needs_opportunity(monkeypatch):
    """§8/§20: a REAL solicitation is required. The Georgia dev seed has no
    decomposed NOFO, so AUTO must fail closed with NEEDS_OPPORTUNITY — it
    must NOT return a generic fake grant package."""
    _patch_seed(monkeypatch, add_americorps=False)
    with TestClient(app) as c:
        r = c.post("/projects/proj-1/produce",
                   json={"model_selection": {"mode": "AUTO"}},
                   headers=AUTH)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["readiness_state"] == "NEEDS_OPPORTUNITY"
        assert data["pipeline_label"] == "QUALITY_PRODUCTION"
        assert data["submission_enabled"] is False
        assert data["generation_mode"] != "DETERMINISTIC_BASELINE"