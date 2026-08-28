#!/usr/bin/env python3
"""G1-INTEGRITY-LIVE — AmeriCorps quality/integrity benchmark.

Two live runs against the REAL FY2026 AmeriCorps Georgia NOFO with
MOCK_EVALUATION_ORGANIZATION (mission §33-§36):

  RUN 1 (G1-INTEGRITY-LIVE-01): NO client answers for critical missing
        facts. Expected: NEEDS_CLIENT_INPUT — proves fail-closed.
  RUN 2 (G1-INTEGRITY-LIVE-02): controlled MOCK_CLIENT_ASSERTION answers
        for the critical facts. READY_FOR_REVIEW only if every integrity
        gate actually passes.

Run identity (mission §26): every execution records run_id, commit sha,
source snapshot hashes, model, timestamp, artifact hashes. Metrics are
never mixed between executions.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT), str(_ROOT / "production-seed")):
    if p not in sys.path:
        sys.path.insert(0, p)

from grant_platform.factory.factpack import (  # noqa: E402
    build_mock_fact_pack, build_missing_fact_matrix)
from grant_platform.factory.integrity import (  # noqa: E402
    ApplicantStatus, ClientAnswer, RESEARCH_SOURCES)
from grant_platform.factory.orchestrator import run_factory  # noqa: E402
from grant_platform.factory.quality_drafting import (  # noqa: E402
    build_quality_model_invoke, build_section_plans)
from grant_platform.factory.solicitation import (  # noqa: E402
    AMERICORPS_GA_2026, build_blueprint_from_solicitation,
    coverage_matrix)

OUT_DIR = _ROOT / "docs" / "grant-sector" / "g1" / "quality-live"
MODEL_ID = "nvidia/nemotron-3-super-120b-a12b:free"
AS_OF = date(2026, 2, 27)   # application as-of = solicitation deadline

# Research pack — normalized official provenance (mission §18-§20).
RESEARCH_BLOCK = """- Child poverty, Walker County GA: 19.5% of under-18 residents
  (Census ACS 5-year 2020-2024, table S1701; retrieved 2026-08-28).
- Child poverty, Dade County GA: 16.4% of children
  (Census ACS via QuickFacts PEPTADR; retrieved 2026-08-28).
- Median household income, Dade County GA: $41,629
  (Census QuickFacts INC910224, 2020-2024; retrieved 2026-08-28).
- HS graduate or higher (25+), Dade County: 88.6%
  (Census QuickFacts, 2020-2024; retrieved 2026-08-28).
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _commit_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
            text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def _sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() \
        else ""


def _run_identity(tag: str) -> dict:
    profile = AMERICORPS_GA_2026
    return {
        "run_id": f"g1-integrity-{tag}-{_now()}",
        "commit_sha": _commit_sha(),
        "solicitation_sha256": profile.snapshot.compute_digest(_ROOT),
        "model": MODEL_ID,
        "as_of": AS_OF.isoformat(),
        "executed_at": _now(),
    }


def _client_answers() -> list[ClientAnswer]:
    """Controlled MOCK client answers resolving the benchmark's critical
    facts (mission §34). Labeled MOCK_CLIENT_ASSERTION — evaluation
    fixtures, never canonical external truth."""
    t = _now()
    return [
        ClientAnswer(
            "member_dosage",
            ("Each member serves a full-time 1,700-hour term: 32 hours per "
             "week delivering 3 tutoring sessions per week of 90 minutes "
             "each across a 32-week program year"),
            answered_at=t, label="MOCK_CLIENT_ASSERTION"),
        ClientAnswer(
            "activity_schedule",
            ("Tutoring runs 3 afternoons per week per site in 90-minute "
             "sessions; summer bridge runs 4 weeks at 20 hours per week; "
             "workforce workshops run monthly (12 per year)"),
            answered_at=t, label="MOCK_CLIENT_ASSERTION"),
        ClientAnswer(
            "prior_americorps",
            ("NEW — the organization has never received AmeriCorps or "
             "Georgia Serves funding"),
            answered_at=t, label="MOCK_CLIENT_ASSERTION"),
    ]


def _run(tag: str, answers, status, out_tag: str) -> dict:
    ident = _run_identity(tag)
    profile = AMERICORPS_GA_2026
    fact_pack = build_mock_fact_pack()
    matrix = build_missing_fact_matrix(fact_pack)
    bp = build_blueprint_from_solicitation(profile)
    plans = build_section_plans(bp, fact_pack, profile,
                                client_answers=answers,
                                applicant_status=status)

    model_invoke, _gateway, counter = build_quality_model_invoke(MODEL_ID)
    print(f"[{tag}] LIVE run: {len(bp.sections)} sections, "
          f"budget {bp.word_limit_total()}w, answers="
          f"{len(answers)}, model={MODEL_ID}")

    factory = run_factory(
        project_id="proj-g1q",
        blueprint=bp,
        model_invoke=model_invoke,
        model_id=MODEL_ID,
        fact_pack=fact_pack,
        profile=profile,
        missing_matrix=matrix,
        client_answers=answers,
        applicant_status=status,
        as_of=AS_OF,
        ceiling="182400.00",
        client_budget_lines=[
            ("Member living allowances (8 full-time MSY)", "personnel",
             "112000.00"),
            ("Member FICA (7.65% of allowances)", "personnel", "8568.00"),
            ("Member healthcare assistance", "personnel", "4800.00"),
            ("Program director (0.25 FTE) — supervision & compliance",
             "personnel", "15600.00"),
            ("Member recruitment — advertising, campus visits, screening",
             "recruitment", "4800.00"),
            ("Member retention — certifications, coaching, recognition",
             "retention", "6000.00"),
            ("Data collection & evaluation systems", "evaluation",
             "7200.00"),
            ("Member training plan & tutoring curriculum", "training",
             "4800.00"),
            ("Indirect costs (10% de minimis)", "indirect", "16377.00"),
        ])

    run_dir = OUT_DIR / out_tag
    run_dir.mkdir(parents=True, exist_ok=True)
    docx_path = run_dir / "PROPOSAL.docx"
    pdf_path = run_dir / "PROPOSAL.pdf"
    factory.docx.write(str(docx_path))
    factory.pdf.write(str(pdf_path))

    pdf_pages = -1
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        pdf_pages = len(doc)
        doc.close()
    except Exception:
        pass

    md = ["# G1 Integrity Benchmark — FY2026 AmeriCorps Georgia", "",
          f"_Run: {ident['run_id']}_",
          f"_Applicant: {fact_pack.legal_name} "
          f"({fact_pack.organization_label})_",
          f"_Artifact label: {factory.artifact_label}_", ""]
    for sid, sec in factory.draft.sections.items():
        md.append(f"## {sec.title}")
        md.append("")
        md.append(sec.text)
        md.append("")
    (run_dir / "PROPOSAL.md").write_text("\n".join(md), encoding="utf-8")

    cov = coverage_matrix(factory.draft.sections, profile)
    s = factory.summary()
    integ = factory.integrity
    report = {
        "run_identity": ident,
        "artifact_hashes": {
            "docx": _sha_file(docx_path), "pdf": _sha_file(pdf_path)},
        "artifact_label": factory.artifact_label,
        "solicitation": {
            "funder": profile.snapshot.funder,
            "title": profile.snapshot.title,
            "source_url": profile.snapshot.source_url,
            "sha256": profile.snapshot.sha256,
            "deadline": profile.deadline,
            "narrative_page_limit": profile.narrative_page_limit},
        "requirements_count": len(profile.requirements),
        "scoring_criteria_count": len(profile.criteria),
        "research_sources": [
            {"source_id": r.source_id, "publisher": r.publisher,
             "dataset": r.dataset, "official_url": r.official_url,
             "retrieval_date": r.retrieval_date,
             "observation_period": r.observation_period,
             "geography": r.geography, "locator": r.locator,
             "authority_tier": r.authority_tier}
            for r in RESEARCH_SOURCES],
        "organization": {
            "label": fact_pack.organization_label,
            "fact_count": len(fact_pack.facts),
            "applicant_status": status.status if status else "UNKNOWN"},
        "sections": {sid: {"title": sec.title, "words": sec.word_count,
                           "target_range": list(plans[sid].target_word_range)}
                     for sid, sec in factory.draft.sections.items()},
        "requirement_coverage_pct": round(
            100 * sum(1 for c in cov if c["covered"]) / max(1, len(cov)), 1),
        "words_total": sum(x.word_count
                           for x in factory.draft.sections.values()),
        "pdf_pages_actual": pdf_pages,
        "model_calls": counter["n"],
        "revisions": sum(r.get("revisions", 0)
                         for r in factory.draft.model_runs
                         if isinstance(r, dict)),
        "fact_critic": [
            {"section": r.get("section"),
             "verdict": r.get("fact_critic"),
             "violations": r.get("fact_violations", [])}
            for r in factory.draft.model_runs if isinstance(r, dict)],
        "qa_gates": [r.to_dict() for r in factory.qa.results],
        "integrity": integ.to_dict() if integ else None,
        "readiness_state": factory.readiness_state,
        "status": s.get("status"),
    }
    (run_dir / "RUN_REPORT.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8")

    print(f"[{tag}] words={report['words_total']} pdf_pages={pdf_pages} "
          f"coverage={report['requirement_coverage_pct']}% "
          f"claims={integ.ledger_summary if integ else '?'} "
          f"readiness={factory.readiness_state}")
    return report


def main() -> int:
    import os
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("STOP: OPENROUTER_API_KEY not configured — fail-closed.")
        return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status_new = ApplicantStatus(
        status="FORMULA_NEW",
        basis="MOCK_CLIENT_ASSERTION: never received AmeriCorps/Georgia "
              "Serves funding; new applicants apply via formula funding "
              "(NOFO C.1/B.1)")

    # RUN 1 — no client answers: critical facts unresolved -> fail-closed
    print("=" * 70)
    run1 = _run("LIVE-01", (), status_new, "run1_blocked")

    # RUN 2 — controlled MOCK client answers resolve critical facts
    print("=" * 70)
    run2 = _run("LIVE-02", _client_answers(), status_new, "run2_resolved")

    comparison = {
        "generated_at": _now(),
        "note": ("QUALITY_CANDIDATE_01 (7c668daa) remains the pre-integrity "
                 "adversarial artifact; runs below are the "
                 "integrity-hardened candidates (mission §1, §36)."),
        "candidate_01_reference": {
            "commit": "7c668daa", "words": 3023, "pdf_pages": 7,
            "claims_ledger": 4, "coverage_pct": 100.0,
            "readiness": "READY_FOR_REVIEW (invalid — see P0-01..P0-05)"},
        "run1_blocked": {
            "run_id": run1["run_identity"]["run_id"],
            "words": run1["words_total"],
            "pdf_pages": run1["pdf_pages_actual"],
            "coverage_pct": run1["requirement_coverage_pct"],
            "claims_total": run1["integrity"]["claims"]["total"],
            "claims_supported": run1["integrity"]["claims"]["supported"],
            "claims_unsupported": run1["integrity"]["claims"]["unsupported"],
            "critical_gaps": run1["integrity"]["unresolved_critical_facts"],
            "temporal_conflicts": len(run1["integrity"]["temporal_conflicts"]),
            "numeric_conflicts": len(run1["integrity"]["numeric_conflicts"]),
            "readiness": run1["readiness_state"],
            "model_calls": run1["model_calls"],
            "revisions": run1["revisions"]},
        "run2_resolved": {
            "run_id": run2["run_identity"]["run_id"],
            "words": run2["words_total"],
            "pdf_pages": run2["pdf_pages_actual"],
            "coverage_pct": run2["requirement_coverage_pct"],
            "claims_total": run2["integrity"]["claims"]["total"],
            "claims_supported": run2["integrity"]["claims"]["supported"],
            "claims_unsupported": run2["integrity"]["claims"]["unsupported"],
            "critical_gaps": run2["integrity"]["unresolved_critical_facts"],
            "temporal_conflicts": len(run2["integrity"]["temporal_conflicts"]),
            "numeric_conflicts": len(run2["integrity"]["numeric_conflicts"]),
            "readiness": run2["readiness_state"],
            "model_calls": run2["model_calls"],
            "revisions": run2["revisions"]},
    }
    (OUT_DIR / "G1_GRANT_QUALITY_REPORT.json").write_text(
        json.dumps(comparison, indent=2, default=str), encoding="utf-8")
    print("=" * 70)
    print("RUN1:", comparison["run1_blocked"]["readiness"],
          "| RUN2:", comparison["run2_resolved"]["readiness"])
    print(f"Report: {OUT_DIR / 'G1_GRANT_QUALITY_REPORT.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
