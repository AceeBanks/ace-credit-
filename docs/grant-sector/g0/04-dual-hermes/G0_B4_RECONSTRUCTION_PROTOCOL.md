# G0 Book 4 — Reconstruction & Cold-Restart Protocol

**Document ID:** GS-G0-B4-C19-RECON-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C19
**Schema:** `schemas/g0/agents/reconstruction_manifest.schema.json`
**Prototype:** `prototype/g0/agents/reconstruction.py`
**Validator:** `tools/g0/validate_compaction_reconstruction.py`

---

## 1. Purpose

Prove the system is **not secretly dependent on hidden conversational
state**. If losing an agent context means losing the business workflow,
Book 4 has failed.

## 2. Reconstruction sequences

### Personal Hermes

```text
identity/user scope
→ selected preferences/goals/open loops
→ active organization/project summaries
→ recent relevant episodic summary
→ ready
```

### CEO Hermes

```text
ratified policy/capability refs
→ active application/project state
→ current intent/plan/task states
→ active blockers
→ promoted operational lessons
→ ready
```

## 3. ReconstructionManifest

Records the exact durable objects used to rebuild context, the excluded
objects (archived raw chat), and `raw_chat_required=false`.

## 4. Required test

Delete/reset both Hermes runtime contexts and rebuild from durable state. The
system must still know:

- client organization;
- active intent/project;
- current opportunity revision;
- task status;
- unresolved questions;
- relevant preferences;
- authority state.

It must **not** require archived raw chat to reconstruct basic operation.

## 5. Recovery quality metric

Compare pre-reset vs post-reset answers to a standardized operational state
query. Material differences = fail/review; exact match = full recovery.

## 6. Verified behaviors

- `test_personal_cold_restart_reconstructs`
- `test_ceo_cold_restart_reconstructs`
- `test_reconstruction_does_not_require_raw_chat`
- `test_recovery_quality_exact_match`
- `test_recovery_quality_detects_material_difference`
