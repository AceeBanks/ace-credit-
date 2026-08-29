"""G1-QUALITY-PROD — canonical quality pipeline unit tests.

Covers the pre-generation gates (NEEDS_OPPORTUNITY / NEEDS_CLIENT_INPUT /
GENERATION_UNAVAILABLE), provenance hashing (claim-ledger + fact-freeze),
and shallow-output detection. Drafting itself is exercised end-to-end
through the API integration tests (test_quality_pipeline_api.py) with a
controlled governed invoke; here we assert the deterministic, no-model
behaviors (gates do not require a live model and are cheap to test).
"""
from __future__ import annotations

import sys
from types import SimpleNamespace

from pathlib import Path as _P
_ROOT = _P(__file__).resolve().parents[1]
for _p in (str(_ROOT), str(_ROOT.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from grant_platform.factory.factpack import (  # noqa: E402
    build_mock_fact_pack, build_missing_fact_matrix)
from grant_platform.factory.quality_contexts import (  # noqa: E402
    unit_test_context)
from grant_platform.factory.quality_pipeline import (  # noqa: E402
    QualityPipelinePackage,
    assess_shallow_output,
    produce_application_quality)


class _ProfileStub:
    """Minimal solicitation-profile stand-in to exercise the gates without
    needing the full AmeriCorps profile (gates short-circuit before it)."""
    snapshot = SimpleNamespace(source_id="stub")


def test_no_profile_is_needs_opportunity():
    """Without a decomposed solicitation profile the pipeline returns
    NEEDS_OPPORTUNITY — never a generic fake package."""
    pkg = produce_application_quality(
        project_id="proj-x", profile=None,
        fact_pack=build_mock_fact_pack(), model_invoke=lambda b: "",
        client_answers=())
    assert pkg.gate == "NEEDS_OPPORTUNITY"
    assert pkg.readiness_state == "NEEDS_OPPORTUNITY"
    assert pkg.submission_enabled is False
    assert pkg.factory is None


def test_no_fact_pack_is_needs_opportunity():
    pkg = produce_application_quality(
        project_id="proj-x", profile=_ProfileStub(), fact_pack=None,
        model_invoke=lambda b: "", client_answers=())
    assert pkg.gate == "NEEDS_OPPORTUNITY"
    assert pkg.readiness_state == "NEEDS_OPPORTUNITY"


def test_no_model_invoke_is_generation_unavailable():
    """No live model -> GENERATION_UNAVAILABLE (fail closed). The
    deterministic skeleton is never a client deliverable."""
    fp = build_mock_fact_pack()
    pkg = produce_application_quality(
        project_id="proj-x", profile=unit_test_context().profile,
        fact_pack=fp, model_invoke=None,
        client_answers=unit_test_context().client_answers)
    assert pkg.gate == "GENERATION_UNAVAILABLE"
    assert pkg.readiness_state == "GENERATION_UNAVAILABLE"


def test_unresolved_critical_facts_ask_client_first():
    """§21: CRITICAL missing facts with no answers -> NEEDS_CLIENT_INPUT with
    concrete questions, returned BEFORE any drafting."""
    ctx = unit_test_context(project_id="proj-a",
                            with_answers=False)
    pkg = produce_application_quality(
        project_id="proj-a", profile=ctx.profile, fact_pack=ctx.fact_pack,
        client_answers=(), applicant_status=ctx.applicant_status,
        as_of=ctx.as_of, research_block=ctx.research_block,
        ceiling=ctx.ceiling, client_budget_lines=ctx.client_budget_lines,
        model_invoke=lambda b: "prose", missing_matrix=ctx.matrix)
    assert pkg.gate == "NEEDS_CLIENT_INPUT"
    assert pkg.readiness_state == "NEEDS_CLIENT_INPUT"
    assert pkg.client_questions
    assert any("member" in q.lower() for q in pkg.client_questions)


def test_ok_package_summary_carries_provenance_and_hashes():
    """A successful quality package records pipeline provenance, run id,
    claim-ledger and fact-freeze hashes, and never claims submission."""
    factory = SimpleNamespace(
        status="BLOCKED",
        readiness_state="QA_BLOCKED",
        draft=SimpleNamespace(generation_mode="LIVE_MODEL",
                              model_runs=[]),
        model_runs=[],
        integrity=None,
        claims=0,
        claim_counts={},
    )
    factory.summary = lambda: {"status": "BLOCKED",
                               "readiness_state": "QA_BLOCKED",
                               "generation_mode": "LIVE_MODEL",
                               "claims": 0, "claim_counts": {}, }
    pkg = QualityPipelinePackage(
        factory=factory,
        gate="OK",
        provenance={
            "pipeline_version": "G1-QUALITY-PROD-01",
            "pipeline_label": "QUALITY_PRODUCTION",
            "project_id": "p", "run_id": "r-1",
            "solicitation_id": "ga_dca_nofp_2026",
            "quality_passes": {"sections_planned": 5},
            "integrity": {"total": 3},
            "requirement_coverage_pct": 100.0,
            "claim_ledger_hash": "abc", "fact_freeze_hash": "def",
            "model_provenance": [],
        },
        pipeline_label="QUALITY_PRODUCTION")
    s = pkg.summary()
    assert s["pipeline_label"] == "QUALITY_PRODUCTION"
    assert s["run_id"] == "r-1"
    assert s["claim_ledger_hash"] == "abc"
    assert s["fact_freeze_hash"] == "def"
    assert s["submission_enabled"] is False


def test_shallow_output_detects_thin_sections():
    """§22: shallow output is detected from planned-depth ratio and rubric
    coverage — not page count."""
    plans = {
        "program_design": SimpleNamespace(
            section_id="program_design", target_word_range=(400, 600),
            points=50),
        "organizational_capability": SimpleNamespace(
            section_id="organizational_capability",
            target_word_range=(300, 500), points=25),
    }
    sections = {
        "program_design": SimpleNamespace(
            section_id="program_design", text="Short thin prose lacking "
            "detail and numbers.", word_count=7),
        "organizational_capability": SimpleNamespace(
            section_id="organizational_capability",
            text="The coalition operates with strong financial controls and "
            "annual independent audits across its three-county service area.",
            word_count=20),
    }
    coverage = [{"covered": True, "required_evidence": ("community_condition",)},
                {"covered": False, "required_evidence": ()}]
    budget = SimpleNamespace()
    result = assess_shallow_output(plans, sections, coverage, budget)
    assert result["shallow_output"] is True
    assert "program_design" in result["under_depth_sections"]
    assert result["requirement_coverage_pct"] == 50.0
    assert any(s["signal"] == "under_depth_ratio_section"
               for s in result["signals"])


def test_populated_sections_not_shallow():
    plans = {
        "program_design": SimpleNamespace(
            section_id="program_design", target_word_range=(400, 600),
            points=50),
    }
    sections = {
        "program_design": SimpleNamespace(
            section_id="program_design",
            text=("The coalition will deliver 420 tutoring sessions across "
                  "8 member positions and 4 school sites per year. ")
            * 40,
            word_count=400),
    }
    coverage = [{"covered": True, "required_evidence": ("community_condition",)}]
    result = assess_shallow_output(plans, sections, coverage,
                                   SimpleNamespace())
    assert result["shallow_output"] is False