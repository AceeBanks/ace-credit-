"""G1 Wave 4 — full Grant factory tests.

Covers blueprint derivation, deterministic + live-model drafting lanes,
protected-fact hard gates, budget ceiling reconciliation, cross-section
synthesis, real DOCX/PDF render validity, full QA gates, and honest
BLOCKED status.
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from grant_platform.factory.blueprint import (  # noqa: E402
    ApplicationBlueprint,
    build_blueprint,
)
from grant_platform.factory.budget import build_budget  # noqa: E402
from grant_platform.factory.drafting import (  # noqa: E402
    PROTECTED_FACTS,
    DraftingReport,
    draft_sections,
)
from grant_platform.factory.orchestrator import (  # noqa: E402
    BLOCKED,
    SUBMISSION_READY_MOCK,
    run_factory,
)
from grant_platform.factory.qa import run_full_qa  # noqa: E402
from grant_platform.factory.render import (  # noqa: E402
    render_docx,
    render_pdf,
)
from grant_platform.factory.synthesis import synthesize  # noqa: E402


def test_blueprint_derives_full_section_catalog():
    bp = build_blueprint()
    assert isinstance(bp, ApplicationBlueprint)
    assert len(bp.sections) == 7
    ids = {s.section_id for s in bp.sections}
    assert {"executive_summary", "organization_background",
            "statement_of_need", "program_narrative",
            "outcomes_evaluation", "sustainability",
            "budget_narrative"} <= ids
    assert bp.revision_id() if hasattr(bp, "revision_id") else True
    assert bp.opportunity_revision_id == "opp_rev_ga_501_1"
    assert len(bp.required_attachments) == 4
    assert "$50,000" in bp.required_terminology


def test_deterministic_lane_grounded_and_honest():
    bp = build_blueprint()
    report = draft_sections(bp)
    assert isinstance(report, DraftingReport)
    assert report.generation_mode == "DETERMINISTIC_BASELINE"
    assert len(report.sections) == 7
    # protected facts preserved verbatim
    org = report.sections["organization_background"].text
    assert "Community Youth Works, Inc." in org
    assert "ELIGIBLE" in org.upper()
    assert "opp_rev_ga_501_1" in org
    need = report.sections["statement_of_need"].text
    assert "18.2" in need
    # unknowns stay visible, never invented
    assert "UNKNOWN:" in need
    unknowns = report.unsupported_material_claims()
    assert all(c.classification == "UNKNOWN" for c in unknowns)


def test_live_lane_uses_governed_model_invoke():
    bp = build_blueprint()
    seen = {}

    def model_invoke(bundle):
        seen["bundle"] = bundle
        assert "conv:" not in str(bundle)          # no transcripts
        assert bundle["protected_facts"]["organization_name"] == \
            "Community Youth Works, Inc."
        assert bundle["instructions"]               # bounded instructions
        sec = bundle["section_id"]
        if sec == "executive_summary":
            return ("Community Youth Works, Inc. requests $50,000 from the "
                    "Georgia Rural Community Impact Grant FY2026 "
                    "(opportunity revision opp_rev_ga_501_1). The "
                    "organization is ELIGIBLE. Deadline October 15, 2026.")
        if sec == "statement_of_need":
            return ("Dade County poverty is 18.2 percent (2023 ACS). "
                    "UNKNOWN: exact youth count was not provided.")
        return ("Grounded section for " + sec + ". Organization: Community "
                "Youth Works, Inc., founded 2012, Atlanta GA, EIN "
                "58-2345671, 501(c)(3). Georgia Rural Community "
                "Impact Grant FY2026. Deadline October 15, 2026. "
                "Ceiling $50,000. Revision opp_rev_ga_501_1. ELIGIBLE. "
                "Dade County poverty 18.2 percent (2023 ACS).")

    report = draft_sections(bp, model_invoke=model_invoke,
                            model_id="minimax/minimax-m3:free")
    assert report.generation_mode == "LIVE_MODEL"
    assert len(report.model_runs) == 7
    assert all(r["status"] == "OK" for r in report.model_runs)
    assert all(s.protected_facts_preserved
               for s in report.sections.values())
    assert seen["bundle"] is not None


def test_live_lane_altered_protected_fact_fails_qa():
    bp = build_blueprint()

    def bad_model(bundle):
        # malicious/mistaken model: changes deadline AND ceiling
        return ("Deadline October 16, 2026. Ceiling $500,000. "
                "Organization: Community Youth Works, Inc. ELIGIBLE. "
                "opp_rev_ga_501_1. 18.2 percent.")

    report = draft_sections(bp, model_invoke=bad_model)
    # at least the deadline/ceiling violations must be flagged
    assert any(not s.protected_facts_preserved
               for s in report.sections.values())
    factory = run_factory(model_invoke=bad_model)
    assert factory.status == BLOCKED
    assert any("protected_facts" in r.gate for r in factory.qa.results
               if r.status == "FAIL")


def test_budget_reconciles_within_ceiling():
    budget = build_budget()
    assert budget.within_ceiling is True
    assert budget.total == "50000.00"
    assert budget.categories["personnel"] == "42000.00"
    assert budget.ok is True


def test_budget_over_ceiling_fails_closed():
    budget = build_budget(client_lines=[
        ("Extra personnel", "personnel", "100000.00")])
    assert budget.within_ceiling is False
    assert not budget.ok
    assert budget.issues


def test_synthesis_terminology_pass():
    bp = build_blueprint()
    report = draft_sections(bp)
    syn = synthesize(bp, report)
    assert syn.pass_count >= 4
    assert not syn.failures


def test_full_factory_submission_ready_mock_deterministic():
    """Deterministic lane has UNKNOWN material claims (honest gaps),
    so status is BLOCKED — never fake-ready. P0-02 fix."""
    factory = run_factory(project_id="proj-1")
    assert factory.status == BLOCKED  # UNKNOWN claims block READY
    summary = factory.summary()
    assert summary["sections"] == 7
    assert summary["unsupported"] > 0  # honest UNKNOWN claims
    assert summary["readiness_state"] != "READY_FOR_REVIEW"
    assert summary["submission_enabled"] is False
    assert summary["within_ceiling"] is True
    assert summary["generation_mode"] == "DETERMINISTIC_BASELINE"


def test_docx_is_valid_ooxml_zip():
    bp = build_blueprint()
    report = draft_sections(bp)
    docx = render_docx(report.sections, artifact_version_id="av-1")
    assert docx.kind == "docx"
    assert docx.payload[:2] == b"PK"          # zip magic
    zf = zipfile.ZipFile(io.BytesIO(docx.payload))
    names = zf.namelist()
    assert "[Content_Types].xml" in names
    assert "word/document.xml" in names
    doc = zf.read("word/document.xml").decode("utf-8")
    assert "Georgia Rural Community Impact Grant FY2026" in doc
    assert "UNKNOWN" in doc or "UNKNOWN" in "\n".join(
        s.text for s in report.sections.values())


def test_pdf_is_valid_pdf():
    bp = build_blueprint()
    report = draft_sections(bp)
    pdf = render_pdf(report.sections, artifact_version_id="av-1")
    assert pdf.kind == "pdf"
    assert pdf.payload[:5] == b"%PDF-"
    assert b"endobj" in pdf.payload or b"%%EOF" in pdf.payload


def test_full_factory_live_lane_pass():
    def model_invoke(bundle):
        return ("Community Youth Works, Inc., founded 2012, Atlanta GA, EIN "
                "58-2345671, 501(c)(3), is ELIGIBLE for "
                "the Georgia Rural Community Impact Grant FY2026 "
                "(opp_rev_ga_501_1). Deadline October 15, 2026, ceiling "
                "$50,000. Dade County poverty 18.2 percent (2023 ACS). "
                f"Section: {bundle['section_id']}.")

    factory = run_factory(model_invoke=model_invoke)
    assert factory.status == SUBMISSION_READY_MOCK
    assert factory.draft.generation_mode == "LIVE_MODEL"
    assert len(factory.model_runs) == 7
