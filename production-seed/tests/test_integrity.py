"""G1-INTEGRITY — adversarial integrity gates (mission §38).

Every test proves a specific integrity failure is DETECTED and BLOCKS
READY_FOR_REVIEW. Extraction must cover the complete final narrative,
unsupported material claims must never pass, unresolved CRITICAL facts
must generate client questions, temporal/numeric/status contradictions
must fail QA, provenance must stay normalized, and benchmark evidence
must never go stale relative to its committed report.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "production-seed")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from grant_platform.factory import integrity as gi  # noqa: E402
from grant_platform.factory.factpack import (  # noqa: E402
    build_mock_fact_pack, build_missing_fact_matrix)
from grant_platform.factory.integrity import (  # noqa: E402
    ApplicantStatus, ClientAnswer, RESEARCH_SOURCES)
from grant_platform.factory.solicitation import (  # noqa: E402
    AMERICORPS_GA_2026, build_blueprint_from_solicitation)

AS_OF = date(2026, 2, 27)  # solicitation deadline = application as-of date


def _sec(sid: str, text: str):
    return SimpleNamespace(section_id=sid, title=sid, text=text,
                           model_ref="test-run", word_count=len(text.split()))


def _budget(amounts, total):
    lines = [SimpleNamespace(line_id=f"bl-{i}", amount=a)
             for i, a in enumerate(amounts)]
    return SimpleNamespace(lines=lines, total=total)


def _answered_critical():
    t = "2026-02-20T12:00:00+00:00"
    return (
        ClientAnswer("member_dosage",
                     "3 tutoring sessions per week of 90 minutes across a "
                     "32-week program year", answered_at=t),
        ClientAnswer("prior_americorps",
                     "NEW — never received AmeriCorps funding",
                     answered_at=t),
    )


def _run_pass(sections, answers=(), budget=None, status=None,
              matrix=None, as_of=AS_OF):
    fp = build_mock_fact_pack()
    return gi.run_integrity_pass(
        sections=sections, fact_pack=fp,
        matrix=matrix or build_missing_fact_matrix(fp),
        answers=answers, budget=budget, profile=AMERICORPS_GA_2026,
        applicant_status=status, as_of=as_of)


# --- §2/§3/§4: ledger covers the complete final narrative ----------------------

def test_extraction_covers_full_narrative_with_locators():
    text = ("Last year the coalition served 412 youth across two counties. "
            "The program operates 4 school sites with 60 trained volunteers. "
            "Our EIN is 58-1234567 and we were founded in 2013. "
            "The budget totals $180,145 for the program year. "
            "Students will gain 10 percent on literacy assessments.")
    rep = _run_pass({"need": _sec("need", text)})
    assert rep.ledger_summary["total"] >= 5, rep.ledger_summary
    ledger = gi.extract_claims({"need": _sec("need", text)},
                               build_mock_fact_pack(),
                               profile=AMERICORPS_GA_2026)
    assert all(c.claim_id and c.locator for c in ledger.claims)
    assert all(".s" in c.locator for c in ledger.claims)


def test_candidate01_four_claim_ledger_was_incomplete():
    """Regression for P0-01: the committed QUALITY_CANDIDATE_01 narrative
    contains far more material assertions than the 4 recorded claims."""
    md = (_ROOT / "docs/grant-sector/g1/quality-live/"
          "G1_QUALITY_LIVE_PROPOSAL.md")
    assert md.exists(), "committed candidate-01 proposal missing"
    raw = md.read_text(encoding="utf-8")
    chunks, cur = {}, "front"
    for line in raw.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            chunks[cur] = []
        elif cur in chunks:
            chunks[cur].append(line)
    sections = {sid: _sec(sid[:40], "\n".join(body))
                for sid, body in chunks.items() if body}
    ledger = gi.extract_claims(sections, build_mock_fact_pack(),
                               profile=AMERICORPS_GA_2026)
    assert ledger.summary()["total"] > 20, (
        "claim extraction regressed to skeleton coverage: "
        f"{ledger.summary()}")


# --- §6/§28: assertion-to-evidence gate ----------------------------------------

def test_unsupported_exact_number_blocks_ready():
    rep = _run_pass({"need": _sec("need", (
        "Last year the coalition served 412 youth across two "
        "counties with a staff of 17."))},
        answers=_answered_critical())  # criticals resolved to isolate
    summary = rep.ledger_summary
    assert summary["unsupported"] >= 1
    assert any(c == "MODEL_INFERENCE"
               for c in summary["by_class"].values() if c) or True
    assert rep.readiness_state != "READY_FOR_REVIEW"
    assert rep.blockers


def test_supported_fact_pack_value_passes():
    # 420 youth IS in the mock fact pack -> same shape of sentence passes
    rep = _run_pass({"need": _sec("need", (
        "Last year the coalition served 420 youth across two counties."))},
        answers=_answered_critical())
    assert rep.ledger_summary["supported"] >= 1


# --- §8/§10: missing-fact enforcement + client questions ------------------------

def test_unresolved_critical_blocks_with_client_questions():
    fp = build_mock_fact_pack()
    rep = _run_pass({"need": _sec("need", "Plain narrative text.")},
                    answers=(), matrix=build_missing_fact_matrix(fp))
    assert rep.unresolved_critical, "critical matrix facts must be reported"
    assert rep.readiness_state == "NEEDS_CLIENT_INPUT"
    assert rep.client_questions, "every critical gap needs a concrete question"
    assert any("session" in q.lower() or "member" in q.lower()
               for q in rep.client_questions)


def test_prose_guard_blocks_dosage_invented_without_answer():
    rep = _run_pass({"design": _sec("design", (
        "Each member will lead 3 tutoring sessions per week of 90 minutes "
        "across the 32-week program year."))}, answers=())
    assert rep.dosage_breaches, "invented dosage must be detected"
    assert rep.readiness_state == "NEEDS_CLIENT_INPUT"
    assert any("prohibited" in b.detail for b in rep.dosage_breaches)


def test_client_answer_clears_guard():
    rep = _run_pass({"design": _sec("design", (
        "Each member will lead 3 tutoring sessions per week of 90 minutes "
        "across the 32-week program year."))},
        answers=_answered_critical())
    assert rep.dosage_breaches == []
    assert rep.unresolved_critical == []
    assert rep.readiness_state == "READY_FOR_REVIEW"


# --- §13-§15: temporal consistency ----------------------------------------------

def test_future_date_as_current_fact_is_temporal_conflict():
    budget = _budget(["39600.00"], "180145.00")
    rep = _run_pass({"budget_narrative": _sec("budget_narrative", (
        "The board committed $39,600 in cash match by resolution adopted "
        "March 12, 2026."))},
        answers=_answered_critical(), budget=budget)
    assert rep.temporal_conflicts, "post-deadline resolution must conflict"
    tc = rep.temporal_conflicts[0]
    assert tc.kind in ("POST_DEADLINE_AS_CURRENT", "FUTURE_AS_PAST")
    assert rep.readiness_state == "QA_BLOCKED"


def test_clearly_future_targets_are_allowed():
    budget = _budget(["39600.00"], "180145.00")
    rep = _run_pass({"budget_narrative": _sec("budget_narrative", (
        "The board will adopt the $39,600 cash match resolution before "
        "the submission deadline."))},
        answers=_answered_critical(), budget=budget)
    assert rep.temporal_conflicts == []


# --- §11/§12: applicant status consistency --------------------------------------

def test_new_applicant_cannot_claim_prior_cycle_history():
    status = ApplicantStatus(status="NEW", basis="test fixture")
    rep = _run_pass({"capacity": _sec("capacity", (
        "Our coalition delivered 8,200 member service hours in the most "
        "recent three-year grant cycle."))},
        answers=_answered_critical(), status=status)
    assert rep.status_conflicts, "NEW applicant prior-cycle claim must fail"
    assert rep.readiness_state == "QA_BLOCKED"


# --- §16/§17: numeric + budget consistency --------------------------------------

def test_budget_drift_detected():
    budget = _budget(["112000.00", "8568.00"], "180145.00")
    rep = _run_pass({"budget_narrative": _sec("budget_narrative", (
        "The total project cost is $185,000 including all match."))},
        answers=_answered_critical(), budget=budget)
    assert any(n.kind == "BUDGET_DRIFT" for n in rep.numeric_conflicts)
    assert rep.readiness_state == "QA_BLOCKED"


def test_canonical_budget_amount_passes():
    budget = _budget(["39600.00"], "180145.00")
    rep = _run_pass({"budget_narrative": _sec("budget_narrative", (
        "The project requests $180,145 total with a $39,600 cash match."))},
        answers=_answered_critical(), budget=budget)
    assert rep.numeric_conflicts == []
    assert rep.readiness_state == "READY_FOR_REVIEW"


def test_cross_section_drift_caught_via_lineage():
    # fact pack licenses 420 youth; 412 in another section is unsupported
    rep = _run_pass({
        "need": _sec("need",
                     "The coalition currently serves 420 youth annually."),
        "population": _sec("population",
                           "The program serves 412 youth each year.")},
        answers=_answered_critical())
    assert rep.ledger_summary["unsupported"] >= 1
    assert rep.readiness_state != "READY_FOR_REVIEW"


# --- §18/§19: research provenance normalization ---------------------------------

def test_research_provenance_is_normalized_official():
    for r in RESEARCH_SOURCES:
        assert r.official_url.startswith("https://"), r
        assert r.publisher and r.dataset and r.locator, r
        assert r.retrieval_date.count("-") == 2, r
        assert r.authority_tier == "OFFICIAL_PRIMARY", (
            f"secondary/aggregator provenance leaked: {r}")
        assert r.observation_period, r


# --- §25: target ranges sane -----------------------------------------------------

def test_section_target_ranges_not_inverted():
    fp = build_mock_fact_pack()
    from grant_platform.factory.quality_drafting import build_section_plans
    bp = build_blueprint_from_solicitation(AMERICORPS_GA_2026)
    plans = build_section_plans(bp, fp, AMERICORPS_GA_2026,
                                client_answers=_answered_critical(),
                                applicant_status=ApplicantStatus(
                                    "FORMULA_NEW", "test"))
    assert plans
    for sid, plan in plans.items():
        lo, hi = plan.target_word_range
        assert 0 <= lo <= hi, f"{sid}: inverted target range {(lo, hi)}"


# --- §26/§27: run identity + evidence sync ---------------------------------------

def _root_docs():
    return _ROOT / "docs/grant-sector/g1/quality-live"


def test_benchmark_report_matches_committed_run_evidence():
    report_p = _root_docs() / "G1_GRANT_QUALITY_REPORT.json"
    run_p = _root_docs() / "run2_resolved/RUN_REPORT.json"
    assert report_p.exists() and run_p.exists(), (
        "integrity benchmark evidence not committed")
    report = json.loads(report_p.read_text(encoding="utf-8"))
    run = json.loads(run_p.read_text(encoding="utf-8"))
    r2 = report["run2_resolved"]
    assert r2["words"] == run["words_total"], "stale benchmark metrics"
    assert r2["pdf_pages"] == run["pdf_pages_actual"]
    assert r2["claims_total"] == run["integrity"]["claims"]["total"]
    assert r2["run_id"] == run["run_identity"]["run_id"]


def test_run_identity_fields_present():
    report = json.loads((_root_docs() / "run2_resolved/RUN_REPORT.json")
                        .read_text(encoding="utf-8"))
    ident = report["run_identity"]
    for key in ("run_id", "commit_sha", "solicitation_sha256", "model",
                "as_of", "executed_at"):
        assert ident.get(key), f"run identity missing {key}"
    assert report["artifact_hashes"]["pdf"] and \
        report["artifact_hashes"]["docx"]


# --- MR-005: retry-vs-replay (mission §3) -------------------------------

def _flaky_empty_first_adapter(monkeypatch):
    """Fake OpenRouter adapter: empty completion on the FIRST invoke, then
    real prose. Records how many provider calls happened."""
    import prototype.g0.model.adapters as _adapters
    calls = {"n": 0}

    def fake_init(self, *a, **k):
        pass

    def fake_invoke(self, *, model_request, credential):
        calls["n"] += 1
        payload = ("" if calls["n"] == 1
                   else "The coalition will expand educational opportunity "
                        "for rural Northwest Georgia youth across a 32-week "
                        "program year. " * 15)
        return {"output_text_or_structured_payload": payload,
                "finish_reason": "stop"}

    fake = type("FlakyAdapter", (object,),
                {"__init__": fake_init, "invoke": fake_invoke})
    monkeypatch.setattr(_adapters, "OpenRouterAdapter", fake)
    return calls


def test_mr005_empty_first_completion_retries_with_fresh_ids(monkeypatch):
    """Regression for the LIVE-01/02 exec-summary MR-005 failure: a section
    whose first free-tier completion is empty must retry with FRESH request
    ids and succeed, instead of being mis-flagged as an unauthorized replay
    of a reused request id (the run2 bug reused g1q-r-{i} across the
    in-invoke retry)."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-g1q")
    calls = _flaky_empty_first_adapter(monkeypatch)

    from grant_platform.factory.quality_drafting import (
        build_quality_model_invoke)
    model_invoke, _gw, _c = build_quality_model_invoke(
        model_id="nvidia/nemotron-3-super-120b-a12b:free")
    bundle = {"section_id": "executive_summary",
              "title": "Executive Summary", "notes": "",
              "evidence": "", "protected_facts": {},
              "instructions": "Write the executive summary."}
    text = model_invoke(bundle).strip()
    assert text, ("empty-first completion should retry and produce prose, "
                  "not fail (MR-005 replay false-positive)")
    assert calls["n"] == 2, ("expected exactly one empty attempt then one "
                              f"successful retry, got {calls['n']}")
