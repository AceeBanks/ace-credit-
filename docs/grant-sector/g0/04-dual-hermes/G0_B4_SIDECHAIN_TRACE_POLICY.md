# G0 Book 4 — Sidechain Trace Policy

**Document ID:** GS-G0-B4-C8-SIDECHAIN-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C8
**Schema:** `schemas/g0/agents/sidechain_manifest.schema.json`
**Prototype:** `prototype/g0/agents/result_reducer.py`

---

## 1. Purpose

Preserve full forensic depth of worker execution **without contaminating CEO
or Personal active context**.

## 2. Policy

| Topic | Rule |
|---|---|
| Default visibility | CEO/Personal receive the bounded WorkerResult; the transcript is retrieved only through explicit review/debugging paths. |
| Retention class | Every manifest carries a retention class (e.g. `D4_WORKER_TRACE`); scratch expires per `worker_context_policy`. |
| Redaction | `redaction_status` ∈ {CLEAN, REDACTED, POLICY_FAILURE}; raw secrets are never persisted — a match is a policy failure. |
| Evidence promotion | High-value evidence found in a trace is promoted to Book 3 evidence objects, never left only in transcript. |
| Audit | Failed attempts remain in the manifest (`errors`, `retries`) and stay part of the decision/audit lineage. |

## 3. Secret scan

Patterns scanned before persistence:

- API keys (`sk-…`, `AKIA…`)
- bearer tokens
- private key blocks

A matched pattern raises `SidechainPolicyError`; the trace is refused rather
than stored.

## 4. Verified behaviors

- `test_secret_fixture_fails_closed`
- `test_secret_scan_catches_private_key_and_bearer`
- `test_retries_keep_lineage_unique_attempts`
