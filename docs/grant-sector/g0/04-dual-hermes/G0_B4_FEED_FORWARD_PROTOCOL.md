# G0 Book 4 — Feed-Forward Protocol

**Document ID:** GS-G0-B4-FEEDFORWARD-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4 (overview of C4-C11 contracts)

---

## 1. Purpose

Freeze the typed feed-forward chain end-to-end. Interaction between roles is
governed by **typed contracts**, never by prompt convention or a shared
mega-prompt.

## 2. The canonical flow

```text
CLIENT
  ↓
PERSONAL HERMES
  ↓
IntentContract
  ↓
CONTROL / POLICY
  ↓
CEO HERMES
  ↓
TaskPlan
  ↓
TaskContracts
  ↓
SPECIALIST WORKERS / DETERMINISTIC SERVICES
  ↓
WorkerResults + sidechains
  ↓
CEO Synthesis → OutcomeArtifact
  ↓
PERSONAL HERMES
  ↓
ClientExplanationPacket
  ↓
CLIENT
```

## 3. Contract boundaries

| Boundary | Contract | Schema |
|---|---|---|
| Client → Personal | conversation + refs | — |
| Personal → CEO | `IntentContract` | `intent_contract.schema.json` |
| CEO → Personal | `ClarificationRequest` | `clarification_request.schema.json` |
| CEO → Workers | `TaskPlan` + `TaskContract` | `task_plan.schema.json`, `task_contract.schema.json` |
| Worker → CEO | `WorkerResult` + `SidechainManifest` | `worker_result.schema.json`, `sidechain_manifest.schema.json` |
| CEO → Personal | `OutcomeArtifact` | `outcome_artifact.schema.json` |
| Personal → Client | `ClientExplanationPacket` | `client_explanation_packet.schema.json` |
| Any operation | `ContextBundle` | `context_bundle.schema.json` |

## 4. Rules (frozen)

1. Raw conversation is linked, never embedded wholesale.
2. CEO work begins from a complete IntentContract.
3. Missing critical input → ClarificationRequest, never a guess.
4. Workers receive minimum-information TaskContracts and bounded refs.
5. Parent Hermes receives bounded WorkerResults; depth lives in sidechains.
6. CEO synthesizes against evidence/state; conflict is surfaced, not averaged.
7. Personal explains outcomes without altering facts or hiding uncertainty.
8. Memory is not a second hidden pathway around this protocol.

## 5. Verified by

The band tests for C4-C11 (`test_intent_contract.py`,
`test_clarification_flow.py`, `test_task_delegation.py`,
`test_worker_sidechains.py`, `test_context_boundaries.py`).
