# G0 Amendment 003 — Humanizer Bounded Style-Transform Evaluation

**Document ID:** GS-G0-AMD-003
**Version:** 1.0
**Status:** ACTIVE PLANNING AMENDMENT — DOES NOT ALTER BOOK 1 CONSTITUTIONAL LAW
**Branch:** `grant-sector-r0-salvage`
**Date:** 2026-08-26
**Applies to:** Books 7 and 8
**Does not reopen:** Books 1–6 ratified contracts

---

# 0. Purpose

The external repository `blader/humanizer` is approved as a **BOUNDED
STYLE_TRANSFORM CANDIDATE** for the Book 7/8 quality pipeline (recorded as
RESERVE in the R0/G0 External Component Decision Ledger, Batch 05). This
amendment gives that reservation a narrow formal contract so integration
into the evaluation pipeline is governed rather than ad hoc.

The governing principle is unchanged from Amendment 002:

> **Books define what must be true. External components compete only to
> implement bounded parts of those contracts. No component may redefine the
> product, evidence authority, canonical state, or constitutional control
> model.**

---

# 1. Classification

- **Repository:** `blader/humanizer`
- **Classification:** BOUNDED STYLE_TRANSFORM CANDIDATE
- **Explicitly NOT:** writer authority, evidence authority, canonical state,
  fact source, QA authority, production self-modification system.

Humanizer transforms **prose presentation only**. It never changes what the
grant machine knows to be true.

---

# 2. Bounded Scope Rules (HZR-001..015)

1. **HZR-001 — Prose only.** Humanizer may transform prose (wording, voice,
   tone, structure of sentences/paragraphs). It may not transform structured
   data, budget numbers, deadlines, citations, or canonical facts.
2. **HZR-002 — No canonical fact modification.** Humanizer cannot modify
   canonical facts or evidence authority in any form.
3. **HZR-003 — No evidence authority.** Humanizer cannot create, retract, or
   re-grade evidence; it cannot change provenance or source lineage.
4. **HZR-004 — No independent introduction of protected content.** Humanizer
   cannot independently introduce names, dates, numbers, statistics, funding
   amounts, budget values, citations, organizations, partnerships,
   testimonials, or historical outcomes.
5. **HZR-005 — Every output is a new ArtifactVersion.** Each Humanizer pass
   produces ArtifactVersion N+1 from ArtifactVersion N; versions are
   append-only and the input artifact ref is recorded.
6. **HZR-006 — Pre/post semantic comparison is mandatory.** A semantic
   comparison between input and output artifact is required before the output
   may be used for any downstream purpose.
7. **HZR-007 — Protected claims must be diffed.** Claims in the Claim Ledger
   marked protected (organization names, funder names, program names, dates,
   deadlines, funding ranges, budget numbers, statistics, citations,
   historical outcomes, measurable targets, eligibility statements,
   partnership statements, testimonial statements, required terminology) are
   extracted and diffed; any protected-fact change is a FAIL.
8. **HZR-008 — Factuality revalidation after transform.** Factuality and
   claim-ledger validation MUST run again AFTER Humanizer; an artifact is not
   usable until the post-transform run passes.
9. **HZR-009 — No direct canonical write.** Humanizer cannot write directly
   into canonical application state; it returns a candidate ArtifactVersion
   through the governed promotion path.
10. **HZR-010 — Evaluated against grounded baseline.** Humanizer is evaluated
    as BASELINE GROUNDED DRAFT vs HUMANIZED GROUNDED DRAFT on the SAME
    input/evidence set.
11. **HZR-011 — No AI-detector evasion objective.** Humanizer must not be
    optimized for "AI detector evasion"; that is explicitly out of scope and
    not a success metric.
12. **HZR-012 — Success objective.** The success objective is more natural
    writing while preserving semantic/factual integrity.
13. **HZR-013 — Replaceable.** The component remains replaceable; project-owned
    contracts (ArtifactVersion, ClaimLedger, EvalSuite) are authoritative.
14. **HZR-014 — No measurable improvement => REJECT/DEFER.** If no measurable
    quality improvement exists over baseline, the disposition must be
    REJECT or DEFER — never silent adoption.
15. **HZR-015 — Provenance recorded.** License, version, and provenance of the
    Humanizer component are recorded in the external-component decision
    ledger and in every eval run that uses it.

---

# 3. Integration Path

```text
ArtifactVersion N (BASELINE GROUNDED DRAFT)
        ↓
STYLE_TRANSFORM (Humanizer candidate, bounded scope)
        ↓
semantic comparison + protected-claim diff (HZR-006/007)
        ↓
ArtifactVersion N+1 (HUMANIZED GROUNDED DRAFT)
        ↓
factuality/claim-ledger revalidation (HZR-008)
        ↓
Book 7 eval suite (grant quality, factuality, security regression)
        ↓
PromotionDecision: PROMOTE | REVISE | REJECT | QUARANTINE | DEFER
```

The Humanizer output never bypasses the Book 7 promotion path.

---

# 4. Hard Gates

- Any protected-fact change (HZR-007) => FAIL, regardless of style gains.
- Any increase in unsupported material claims => FAIL (EVAL-LAW-003/C8 hard gate).
- Submission capability must never appear in Humanizer output or any pipeline
  stage; submission stays structurally disabled.

---

# 5. Disposition after Book 7 D2 experiment

The D2 experiment (first grounded grant-writing quality experiment) will
record baseline vs humanized metrics and the resulting disposition for the
Humanizer candidate. D2 does NOT automatically promote Humanizer; the
disposition derives from the Book 7 promotion rules.

---

# 6. Relation to Prior Records

- Decision Ledger Batch 05: `blader/humanizer` RESERVE for Book 7/8.
- Book 6 handoff: Humanizer reserved as BOUNDED STYLE_TRANSFORM CANDIDATE;
  a ratified amendment is required before integration — this document is that
  amendment.
- Amendment 002 anti-pollution tests remain binding: this amendment adds a
  bounded candidate without weakening any constitutional invariant.
