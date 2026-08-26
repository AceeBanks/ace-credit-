# G0-B3 — Source Health, D0 Data Packet & Shadow Draft Harness (C22-C24)

## Scope

Treats sources as operational dependencies with measurable health (B3.C22), defines the source-governed evidence packet that unlocks the first grounded mock grant (B3.C23), and specifies — without productionizing — the first visible writing demonstration (B3.C24).

## C22 — Source Health, Observability & Degradation

Config of truth: `config/g0/source/source_health_policy.yaml` · Prototype: `prototype/g0/source/health.py`

Eight health states (`HEALTHY`, `DEGRADED`, `FAILING`, `AUTH_ERROR`, `RATE_LIMITED`, `SCHEMA_CHANGED`, `DISABLED`, `UNKNOWN`) and eleven health metrics (last successful fetch, failure rate, latency, schema-validation rate, extraction-quality trend, HTTP status distribution, rate-limit events, content-change frequency, duplicate rate, stale-source count, downstream invalidations).

**Schema drift is fail-closed:** a schema validation failure drives the source to `SCHEMA_CHANGED`, disables fresh promotion, requires a captured fixture and repair/eval — critical facts are never silently mapped to null. A source can remain **queryable historically** while disabled for fresh promotion, and an outage never erases cached history. A **hard-stale critical opportunity forces uncertainty/block**, never silent readiness.

## C23 — D0 Source-Governed Data Packet

Config of truth: `config/g0/source/d0_data_packet.yaml` · Prototype: `prototype/g0/source/d0_packet.py`

The D0 packet is the **source-governed evidence packet** required to construct a Book 2 `DraftContextBundle` without agent memory. It requires all nine sections: client-profile fixture (manually approved), Georgia opportunity (registered source + immutable snapshot + exact revision), opportunity requirements (extracted/normalized), eligibility (validated + deterministic), funder/program research (source-backed), historical winner/award research (no unsupported causal inference), community-impact statistics (typed, geography/time explicit), budget assumptions (client-provided/verified labels), and proposal profile (18-section skeleton).

Fact discipline is fail-closed: **no missing factual input may be silently invented** — every fact carries a source ref or an explicit `NEEDS_CLIENT_INPUT` / `NEEDS_SOURCE` / `PROVISIONAL` / `UNSUPPORTED_DO_NOT_USE` state. Every output carries `MOCK`, `NON_SUBMISSION`, `NOT_CLIENT_APPROVED_FINAL`. Success criteria are executable: exact source revision visible, material claims traceable, requirement coverage measurable, no agent memory required for reconstruction, and the draft regenerates from the packet (deterministic serialization).

## C24 — D0 Shadow Draft Harness Specification

Specified, not productionized. The harness flow is fixed: D0 Data Packet → Application Blueprint Generator → Requirement-to-Section Map → Evidence Retrieval → Draft Section Generator → Factuality/Citation Check → Requirement Coverage Check → Cross-Section Consistency → Mock Proposal Artifact → D0 QA Report.

Model permissions are **L2 internal only**; no email/send/submission tools exist anywhere in the flow. The hard stop is constitutional: **D0 is an evaluation artifact and can never be represented as submission-ready production output.** D0 is judged on requirement coverage, unsupported-claim rate, evidence-lineage completeness, factual consistency, organization/opportunity correctness, usefulness and reproducibility — not award rate.

## Tests

- `tests/g0/book3/test_source_health.py` — schema drift → SCHEMA_CHANGED + promotion disabled + repair required; outage preserves history; hard-stale blocks;
- `tests/g0/book3/test_d0_packet.py` — nine sections required, unsupported facts rejected, explicit fact states allowed, exact revision required, MOCK/NON_SUBMISSION labels enforced, deterministic regeneration, measurable coverage;
- `tests/g0/book3/test_d0_harness.py` — flow is the exact ten-stage spec, L2-only permissions with no submission stages, hard stop declared, Book 2 Georgia fixture feeds a packet that reconstructs without agent memory.

## Validation

- `python tools/g0/validate_health_d0.py` → **PASS**

## Commits

- `G0-B3-C22-C24` chapter band.

## Status

PASS — sources degrade safely, and the D0 packet/harness spec makes the first grounded mock grant reconstructable, measurable and clearly non-submission.
