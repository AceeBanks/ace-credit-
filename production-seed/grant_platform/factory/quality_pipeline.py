"""G1-QUALITY-PROD — canonical quality application pipeline.

ONE authoritative production proposal path. Every client AUTO/MANUAL
generation runs THROUGH this orchestrator (never the shallow baseline
writer). The pipeline is:

    solicitation decomposition (SolicitationProfile)
    -> ApplicationBlueprint (solicitation-derived sections + scoring weights)
    -> Requirement Matrix (coverage_matrix)
    -> OrganizationFactPack
    -> MissingFactMatrix
    -> client-question gate   (NEEDS_CLIENT_INPUT before generation)
    -> SectionPlans (objective, criterion, facts, sub-questions, depth)
    -> bounded per-section workers:
         draft -> quality critic -> factual critic -> bounded revision
    -> global synthesis (voice/terminology/numbers)
    -> final Claim Ledger extraction (complete final narrative)
    -> integrity QA (temporal / numeric / budget / cross-section / status)
    -> budget reconciliation
    -> render DOCX/PDF
    -> readiness state

Reuses the existing G1 factory modules (run_factory, quality_drafting,
solicitation, factpack, integrity). It does NOT build new architecture —
it is the composition and gating boundary that the API was missing.

Provenance (§24): every package records pipeline_version, pipeline_label
(QUALITY_PRODUCTION vs DEVELOPER_DIAGNOSTIC), solicitation_id, run_id,
model provenance, quality/integrity passes, claim-ledger hash and
fact-freeze hash so any artifact can be traced to either the canonical
quality engine or the diagnostic baseline.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.factory.budget import build_budget
from grant_platform.factory.factpack import build_missing_fact_matrix
from grant_platform.factory.orchestrator import run_factory
from grant_platform.factory.quality_drafting import build_section_plans
from grant_platform.factory.solicitation import (
    build_blueprint_from_solicitation, coverage_matrix)

PIPELINE_VERSION = "G1-QUALITY-PROD-01"
QUALITY_LABEL = "QUALITY_PRODUCTION"
DIAGNOSTIC_LABEL = "DEVELOPER_DIAGNOSTIC"

# Normal client states (§20).
NEEDS_OPPORTUNITY = "NEEDS_OPPORTUNITY"
NEEDS_CLIENT_INPUT = "NEEDS_CLIENT_INPUT"
NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
GENERATION_UNAVAILABLE = "GENERATION_UNAVAILABLE"
QA_BLOCKED = "QA_BLOCKED"
READY_FOR_REVIEW = "READY_FOR_REVIEW"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


@dataclass
class QualityPipelinePackage:
    """Result of the canonical quality pipeline (or a pre-generation gate).

    gate is one of OK / NEEDS_OPPORTUNITY / NEEDS_CLIENT_INPUT /
    GENERATION_UNAVAILABLE. When gate == OK, factory is populated with a
    real FactoryPackage (DRAFT_* / READY_FOR_REVIEW) — never a fake.
    """
    factory: object | None
    gate: str = "OK"
    provenance: dict = field(default_factory=dict)
    coverage: list = field(default_factory=list)
    shallow: dict = field(default_factory=dict)
    quality_score: dict = field(default_factory=dict)
    client_questions: list = field(default_factory=list)
    pipeline_label: str = QUALITY_LABEL

    @property
    def readiness_state(self) -> str:
        if self.gate in (NEEDS_OPPORTUNITY, NEEDS_CLIENT_INPUT,
                         NEEDS_EVIDENCE, GENERATION_UNAVAILABLE):
            return self.gate
        if self.factory is None:
            return GENERATION_UNAVAILABLE
        return self.factory.readiness_state

    @property
    def submission_enabled(self) -> bool:
        return False

    def summary(self) -> dict:
        """Flatten a client-facing summary (factory metrics + provenance +
        quality signals). Never exposes secrets."""
        base: dict = {}
        if self.factory is not None:
            base = self.factory.summary()
        base["readiness_state"] = self.readiness_state
        base["gate"] = self.gate
        base["status"] = self.factory.status if self.factory else "BLOCKED"
        base["submission_enabled"] = False
        base["generation_mode"] = (
            self.factory.draft.generation_mode if self.factory else None)
        base["pipeline_label"] = self.pipeline_label
        base["pipeline_version"] = self.provenance.get("pipeline_version",
                                                       PIPELINE_VERSION)
        base["solicitation_id"] = self.provenance.get("solicitation_id")
        base["run_id"] = self.provenance.get("run_id")
        base["quality_passes"] = self.provenance.get("quality_passes", {})
        base["integrity_passes"] = self.provenance.get("integrity", {})
        base["claim_ledger_hash"] = self.provenance.get("claim_ledger_hash")
        base["fact_freeze_hash"] = self.provenance.get("fact_freeze_hash")
        base["model_provenance"] = self.provenance.get("model_provenance", [])
        base["client_questions"] = self.client_questions
        base["requirement_coverage_pct"] = (
            self.provenance.get("requirement_coverage_pct"))
        base["quality_score"] = self.quality_score
        base["shallow_output"] = self.shallow
        return base


# --- Pre-generation gates -----------------------------------------------------


def _gate(pkg: QualityPipelinePackage, gate: str, questions=()) \
        -> QualityPipelinePackage:
    pkg.gate = gate
    if questions:
        pkg.client_questions = list(questions)
    return pkg


def _needs_opportunity(*, project_id: str, run_id: str) -> QualityPipelinePackage:
    pkg = QualityPipelinePackage(
        factory=None,
        provenance={"pipeline_version": PIPELINE_VERSION,
                    "pipeline_label": QUALITY_LABEL,
                    "project_id": project_id, "run_id": run_id,
                    "generated_at": _now()})
    return _gate(pkg, NEEDS_OPPORTUNITY, ())


def _needs_client_input(pkg: QualityPipelinePackage, questions) \
        -> QualityPipelinePackage:
    return _gate(pkg, NEEDS_CLIENT_INPUT, questions)


# --- Shallow-output signal (§22) ---------------------------------------------

SHALLOW_SIGNALS = (
    "under_depth_ratio_section", "low_rubric_coverage",
    "missing_program_specificity", "low_evidence_usage",
)


def _section_depth_ratio(words: int, target: tuple[int, int]) -> float:
    lo, hi = target
    mid = ((lo + hi) / 2.0) or 1.0
    return words / mid


def assess_shallow_output(plans: dict, sections: dict, coverage: list,
                          budget) -> dict:
    """Detect shallow output from rubric coverage + planned depth +
    evidence/program specificity. NOT a raw page-count heuristic."""
    signals: list[dict] = []
    under_depth: list[str] = []
    for sid, plan in plans.items():
        sec = sections.get(sid)
        if sec is None:
            under_depth.append(sid)
            continue
        ratio = _section_depth_ratio(sec.word_count, plan.target_word_range)
        if ratio < 0.5 and plan.points > 0:
            under_depth.append(sid)
            signals.append({"signal": "under_depth_ratio_section",
                            "section": sid, "detail": (
                                f"ratio {ratio:.2f} vs planned "
                                f"target {plan.target_word_range}")})
    if coverage:
        covered = sum(1 for c in coverage if c.get("covered"))
        cov_pct = round(100 * covered / len(coverage), 1)
        if cov_pct < 90:
            signals.append({"signal": "low_rubric_coverage",
                            "detail": f"requirement coverage {cov_pct}%"})
    else:
        cov_pct = None
    # program specificity: a substantive proposal names concrete quantities
    full = " ".join(s.text for s in sections.values()) if sections else ""
    import re as _re
    digits = len(_re.findall(r"\d{2,}", full))
    if digits < 3:
        signals.append({"signal": "missing_program_specificity",
                        "detail": "few or no concrete quantities in narrative"})
    shallow = bool(under_depth) or bool(signals)
    return {
        "shallow_output": shallow,
        "signals": signals,
        "under_depth_sections": under_depth,
        "requirement_coverage_pct": cov_pct,
        "signal_labels": [s["signal"] for s in signals],
    }


# --- Quality scoring (§15) ---------------------------------------------------

QUALITY_DIMENSIONS = (
    "Executive Summary", "Need / Problem", "Program Design",
    "Goals / Objectives", "Implementation", "Evaluation",
    "Organizational Capacity", "Budget Narrative", "Sustainability",
    "Funder Alignment", "Evidence Discipline", "Persuasiveness",
    "Professional Readiness",
)


def score_proposal(*, sections: dict, plans: dict, coverage: list,
                   readiness: str, integrity_clean: bool,
                   unsupported: int) -> dict:
    """Heuristic 0-5 score per dimension (blueprint depth + coverage
    signals). Honest: dimensions are scored by how the specific
    solicitation section performed, not global averages."""
    sec_points = {p.section_id: p.points for p in plans.values()}
    ratios = {sid: _section_depth_ratio(sections[sid].word_count,
                                        plans[sid].target_word_range)
              for sid in sections if sid in plans}
    has_need = "statement_of_need" in sections or "program_design" in sections
    has_eval_reqs = any("evaluation" in sid for sid in sections)
    n_evidence = sum(1 for c in coverage if c.get("required_evidence")
                     and c.get("covered"))

    def _s(lo, hi):
        return min(5, max(0, round(sum([lo, hi]) / 2)))

    scores = {
        "Executive Summary": _s(
            3 if "executive_summary" in sections else 1,
            2),
        "Need / Problem": _s(
            2 if has_need else 0,
            4 if ratios.get("program_design",
                            ratios.get("statement_of_need", 0)) >= 1 else 1),
        "Program Design": _s(
            4 if ratios.get("program_design", 0) >= 1 else 1,
            1),
        "Goals / Objectives": _s(
            3 if ratios.get("program_design", 0) >= 0.8 else 1, 0),
        "Implementation": _s(
            3 if ratios.get("organizational_capability",
                            ratios.get("cost_effectiveness", 0)) >= 0.8
            else 1, 0),
        "Evaluation": _s(
            4 if has_eval_reqs and ratios.get("evaluation_summary", 0) >= 1
            else 1, 2),
        "Organizational Capacity": _s(
            4 if ratios.get("organizational_capability", 0) >= 0.9 else 1, 0),
        "Budget Narrative": _s(
            4 if ratios.get("budget_narrative",
                            ratios.get("cost_effectiveness", 0)) >= 0.8
            else 1, 1),
        "Sustainability": _s(
            3 if ratios.get("sustainability", 0) >= 0.8 else 1, 0),
        "Funder Alignment": _s(
            4 if coverage and any("priority" in (c.get("title", "")).lower()
                                  and c.get("covered") for c in coverage)
            else 2, 0),
        "Evidence Discipline": _s(
            4 if n_evidence >= 1 and integrity_clean else
            (2 if n_evidence >= 1 else 0),
            2 if unsupported == 0 else 0),
        "Persuasiveness": _s(
            3 if len(sections) >= 4 and
            sum(sections[s].word_count for s in sections) >= 1000 else 1, 0),
        "Professional Readiness": _s(
            5 if readiness == READY_FOR_REVIEW else
            (3 if readiness == QA_BLOCKED else
             (1 if readiness == NEEDS_CLIENT_INPUT else 0)), 0),
    }
    raw = sum(scores.values())
    overall = round(raw / len(scores), 2)
    return {"dimensions": scores, "overall_out_of_5": overall,
            "max": 5.0}


# --- Provenance (§24) --------------------------------------------------------


def build_provenance(*, project_id: str, solicitation_id: str,
                     fact_pack, draft_sections: dict,
                     plan_shallow: dict, factory, coverage: list,
                     model_provenance: list,
                     run_id: str | None = None) -> dict:
    """Traceable run provenance. Claim-ledger and fact-freeze hashes let us
    tell QUALITY_PRODUCTION output from any other lane by fingerprint."""
    integrity = getattr(factory, "integrity", None)
    ledger_summary = integrity.ledger_summary if integrity else {}
    fact_freeze = sorted(
        f"{f.fact_id}={f.value}" for f in fact_pack.facts.values())
    return {
        "pipeline_version": PIPELINE_VERSION,
        "pipeline_label": QUALITY_LABEL,
        "project_id": project_id,
        "run_id": run_id or f"g1qp-{uuid.uuid4().hex[:10]}",
        "solicitation_id": solicitation_id,
        "generated_at": _now(),
        "model_provenance": model_provenance,
        "quality_passes": {
            "sections_planned": len(plan_shallow.get("plans", {})),
            "redundant": False,
            "shallow_output_detected": plan_shallow.get("shallow_output", False),
        },
        "integrity": (integrity.ledger_summary if integrity else {}),
        "requirement_coverage_pct": (
            round(100 * sum(1 for c in coverage if c.get("covered"))
                  / max(1, len(coverage)), 1) if coverage else None),
        "claim_ledger_hash": _sha256(ledger_summary),
        "fact_freeze_hash": _sha256(fact_freeze),
    }


# --- Canonical entrypoint ----------------------------------------------------


def produce_application_quality(
    *,
    project_id: str,
    profile,
    fact_pack,
    client_answers=(),
    applicant_status=None,
    as_of=None,
    ceiling: str | None = None,
    client_budget_lines=None,
    research_block: str = "",
    model_invoke,
    model_id: str | None = None,
    missing_matrix=None,
    run_id: str | None = None,
    deadline: str | None = None,
) -> QualityPipelinePackage:
    """Run the FULL canonical quality pipeline.

    Gates:
      - no solicitation profile  -> NEEDS_OPPORTUNITY (never a generic fake)
      - no organization fact pack-> NEEDS_OPPORTUNITY
      - unresolved CRITICAL missing facts and no answers
                                 -> NEEDS_CLIENT_INPUT (questions BEFORE
                                    spending a live generation call)
      - no live model invoke     -> GENERATION_UNAVAILABLE (fail closed;
                                    the deterministic skeleton is never a
                                    client deliverable)

    Requires a governed live model invoke. There is NO deterministic path —
    the developer baseline is exposed only through the explicit
    DETERMINISTIC diagnostic lane, labeled DEVELOPER_DIAGNOSTIC.
    """
    run_id = run_id or f"g1qp-{uuid.uuid4().hex[:10]}"
    if profile is None:
        return _needs_opportunity(project_id=project_id, run_id=run_id)
    if fact_pack is None:
        return _needs_opportunity(project_id=project_id, run_id=run_id)
    if model_invoke is None:
        pkg = QualityPipelinePackage(
            factory=None,
            provenance={"pipeline_version": PIPELINE_VERSION,
                        "pipeline_label": QUALITY_LABEL,
                        "project_id": project_id, "run_id": run_id,
                        "solicitation_id": profile.snapshot.source_id,
                        "generated_at": _now()})
        return _gate(pkg, GENERATION_UNAVAILABLE, ())

    blueprint = build_blueprint_from_solicitation(profile)
    # Requirement matrix (solicitation provenance)
    matrix = missing_matrix or build_missing_fact_matrix(fact_pack)
    # client-question gate before any live generation (§21)
    answered_ids = {a.fact_id for a in client_answers}
    critical = [m for m in matrix.critical()
                if m.fact_id not in answered_ids]
    if critical:
        pkg = QualityPipelinePackage(
            factory=None,
            provenance={"pipeline_version": PIPELINE_VERSION,
                        "pipeline_label": QUALITY_LABEL,
                        "project_id": project_id, "run_id": run_id,
                        "solicitation_id": profile.snapshot.source_id,
                        "generated_at": _now(),
                        "client_questions": [m.client_question
                                             for m in critical]})
        return _gate(pkg, NEEDS_CLIENT_INPUT,
                     [m.client_question for m in critical])

    # Build SectionPlans once so the canonical package can report planned
    # depth; draft_sections_quality reuses them via run_factory.
    plans = build_section_plans(blueprint, fact_pack, profile,
                                client_answers=client_answers,
                                applicant_status=applicant_status)
    eff_ceiling = ceiling
    if eff_ceiling is None:
        eff_ceiling = profile.funding_ceiling
    if eff_ceiling is None and client_budget_lines:
        from decimal import Decimal as _D
        eff_ceiling = str(sum((_D(line[2]) for line in
                               client_budget_lines), _D("0.00")))
    eff_ceiling = eff_ceiling or "50000.00"
    budget = build_budget(ceiling=eff_ceiling,
                          client_lines=client_budget_lines)

    factory = run_factory(
        project_id=project_id,
        blueprint=blueprint,
        model_invoke=model_invoke,
        model_id=model_id,
        fact_pack=fact_pack,
        profile=profile,
        missing_matrix=matrix,
        client_answers=client_answers,
        applicant_status=applicant_status,
        as_of=as_of,
        ceiling=eff_ceiling,
        client_budget_lines=client_budget_lines,
        deadline=deadline or profile.deadline,
    )

    coverage = coverage_matrix(factory.draft.sections, profile)
    shallow = assess_shallow_output(
        plans, factory.draft.sections, coverage, budget)

    integrity = factory.integrity
    integrity_clean = (integrity is not None
                       and integrity.readiness_state == READY_FOR_REVIEW)
    score = score_proposal(
        sections=factory.draft.sections, plans=plans, coverage=coverage,
        readiness=factory.readiness_state, integrity_clean=integrity_clean,
        unsupported=len(factory.draft.unsupported_material_claims()))

    model_provenance: list = []
    for r in factory.draft.model_runs:
        if isinstance(r, dict):
            model_provenance.append({
                "section": r.get("section"), "status": r.get("status"),
                "model_id": r.get("model_id"),
                "passes": r.get("passes"),
                "revisions": r.get("revisions"),
                "critic_overall": r.get("critic_overall"),
                "fact_critic": r.get("fact_critic"),
                # Surface the exact failure so a QA_BLOCKED live run can be
                # audited (provider rate-limit/auth vs a real drafting bug).
                "error": r.get("error"),
                "reason": r.get("reason"),
                "fallbacks": r.get("fallbacks"),
            })

    provenance = build_provenance(
        project_id=project_id,
        solicitation_id=profile.snapshot.source_id,
        fact_pack=fact_pack,
        draft_sections=factory.draft.sections,
        plan_shallow={"plans": plans, "shallow_output":
                      shallow.get("shallow_output")},
        factory=factory,
        coverage=coverage,
        model_provenance=model_provenance,
        run_id=run_id)

    return QualityPipelinePackage(
        factory=factory, gate="OK", provenance=provenance,
        coverage=coverage, shallow=shallow, quality_score=score,
        pipeline_label=QUALITY_LABEL)