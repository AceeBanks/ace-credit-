# G0 Book 4 — Worker Contract

**Document ID:** GS-G0-B4-C8-CONTRACT-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C8
**Schema:** `schemas/g0/agents/worker_result.schema.json`
**Prototype:** `prototype/g0/agents/result_reducer.py`

---

## 1. Purpose

Workers are **bounded executors**, not sovereign agents. Each worker receives
one TaskContract, produces one WorkerResult plus sidechain, and disappears.

## 2. Sidechain model

Each worker attempt produces a `SidechainManifest`:

```text
task_id / attempt_id / worker identity / model/provider
start/end time / tool+capability calls / source/artifact refs
errors/retries / full transcript URI / token+cost metrics
redaction status / retention class / secret scan
```

## 3. WorkerResult — the bounded parent-facing payload

```yaml
task_id:
attempt_id:
status:              # SUCCEEDED | PARTIAL | FAILED
summary:             # bounded (<= 4000 chars); full trace stays in sidechain
structured_output_ref:
key_findings:
uncertainties:
source_refs:
artifact_refs:
quality_state:
recommended_followups:
sidechain_ref:
```

## 4. Rules (frozen)

1. **CEO receives WorkerResult by default, not transcript.** A 50k-token trace
   returns a bounded payload; the full trace is retrievable only via
   `sidechain_ref`.
2. **Sidechains cannot contain raw secrets.** A secret scan runs before
   persistence; any match is a `POLICY_FAILURE` (raised), never silently
   redacted into a plausible-looking trace.
3. **High-value evidence is promoted to Book 3 objects**, never trapped in
   transcripts.
4. **Failed attempts remain part of audit lineage.** Retries keep the same
   `task_id` lineage with unique `attempt_id`s.

## 5. Verified behaviors

- `test_50k_trace_returns_bounded_parent_payload`
- `test_ceo_retrieves_exact_refs_without_transcript_injection`
- `test_secret_fixture_fails_closed`
- `test_retries_keep_lineage_unique_attempts`
