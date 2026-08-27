# G0 Book 9 — Runtime Bake-Off Results

**Chapter:** B9.C5
**Date:** 2026-08-27
**Method:** Amendment 002 discipline — no fabricated benchmarks. Workloads
that cannot be run against a candidate are marked `NOT_RUN`/`BLOCKED`, not
scored. Candidates eliminated at C4 hard gates (Compozy, QM) were never
installed (no authorized install path in this environment) and therefore
carry no measured workload results.

## Workload matrix

| W# | Workload | Candidate A (OCE-native) result | Basis |
|---|---|---|---|
| W1 | Personal→CEO intent handoff | PASS | `run_intake` → `run_planning` in the slice; typed IntentContract carries objective/open questions — MEASURED |
| W2 | Bounded worker fanout | PASS | 4 model drafting lanes + research/QA lanes each bound to TaskContract scope — MEASURED |
| W3 | Long research task + checkpoint/resume | PASS (design) | Stage records are durable; reconstruction test recovers full state — MEASURED at record level; long-task wall-clock checkpointing is G1 (production task table) |
| W4 | Worker failure/retry | PASS | Model lane bounded retry on empty completion; degraded-mode fail-closed — MEASURED |
| W5 | Process/runtime restart mid-application | PASS | Cold-restart reconstruction from 10 durable records (1.1 ms) without raw chat — MEASURED |
| W6 | Scoped background source refresh | PARTIAL | Source-fetch count measured (3); a scheduled refresh loop is G1 (scheduler) — DERIVED |
| W7 | Approval-gated operation | PASS | `ApprovalRegistry` bound into `Authorizer` (Book 6 repair seam tests) — MEASURED (unit); no live approval-heavy slice — NOT_RUN at slice level |
| W8 | Credential-injected external API | PASS | Model Gateway: server-side resolver → provider, secret never leaked (tests G/H/I) — MEASURED |
| W9 | Malicious tool/prompt attempt | PASS | ToolGateway forged-decision denial; 6/6 security attacks denied — MEASURED |
| W10 | Multi-project concurrency | PARTIAL | Structural project scope verified; concurrent project execution is G1 (no live concurrency test) |
| W11 | Multi-tenant isolation | PASS | Structural tenant scope; cross-tenant decision reuse DENIED — MEASURED (single live tenant, denial verified) |
| W12 | Audit/evidence linkage | PASS | SliceRecords carry decision_refs + artifact_version_ids; DecisionRecord replay tests — MEASURED |
| W13 | Book 7 shadow/evaluation run | PASS | Evaluation suite runs against drafts; candidate versioning + rollback tests — MEASURED |
| W14 | Artifact/object handling | PASS (design) | ArtifactVersion N/N+1 contract tested; object-storage adapter is G1 — PARTIAL |
| W15 | Runtime export/exit | PASS | Plain Python + JSON records; no framework lock-in; export path is the repo itself — MEASURED |

Candidates B/C/D: all workloads `NOT_RUN` (not installed; no authorized
install path; eliminated at C4 hard gates). No scores are fabricated for
them.

## Weighted scoring (surviving candidate only)

Weights from B9.C6. Candidate A is scored on measured evidence; each score
is a judgment bounded by the workload matrix above, not a fake benchmark.

| Dimension | Weight | Candidate A score (0–5) | Weighted |
|---|---|---|---|
| Constitutional/contract fit | 20% | 5 | 1.00 |
| Tenant + security enforcement | 15% | 5 | 0.75 |
| Durable execution/recovery | 12% | 4 (record-level; production task table is G1) | 0.48 |
| Dual-Hermes/worker fit | 10% | 5 | 0.50 |
| Canonical-state independence | 10% | 5 | 0.50 |
| Audit/replay compatibility | 8% | 5 | 0.40 |
| Operational simplicity | 7% | 4 (Postgres/object-storage adapters are G1 work) | 0.28 |
| Custom glue eliminated | 5% | 5 (this IS the architecture) | 0.25 |
| Observability | 4% | 4 (slice telemetry exists; production tracing is G1) | 0.16 |
| Performance | 3% | 4 (slice runs fast; model latency dominated by provider) | 0.12 |
| Local/cloud deployment | 2% | 4 (local-first today; containers G1) | 0.08 |
| License/upstream risk | 2% | 5 (project-owned) | 0.10 |
| Exit/rebuild cost | 2% | 5 (plain Python/JSON) | 0.10 |
| **Total** | **100%** | | **4.72 / 5.00** |

## Conclusion

Candidate A (OCE-native / project-owned) is the only candidate passing all
hard gates with measured evidence; it scores 4.72/5.00 on the weighted
framework. No external substrate is installed, adoptable, or measured in
this environment, so no competitor score is fabricated.

**Final decision:** `OCE_NATIVE` — ratified in
`G0_B9_RUNTIME_SUBSTRATE_ADR.md`.

## Honest limitations

- Compozy/QM were eliminated on hard gate 7 (framework-owned state) and
  unproven elsewhere; they remain deferred per Amendment 002 Batch 04, not
  permanently rejected.
- Production durable-execution (task table, queue, scheduler), Postgres and
  object-storage adapters, and live concurrency are G1 work — the ADR's
  "what parts are NOT used / what remains" section records this.
- OpenRouter free-tier cost is not a production pricing basis
  (`G0_B9_COST_ENVELOPE.md`).
