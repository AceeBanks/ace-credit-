# G0 Book 4 — D1 Hermes Mock-Draft Contract

**Document ID:** GS-G0-B4-C22-D1-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C22
**Config:** `config/g0/agents/d1_mock_draft_contract.yaml`
**Prototype:** `prototype/g0/agents/d1_flow.py`
**Validator:** `tools/g0/validate_d1_contract.py`

---

## 1. Purpose

Unlock the **first true Dual-Hermes-generated mock application** after Book 4
ratification. D0 (Book 3) proved governed data can feed a Shadow Draft
Harness; D1 proves the actual cognitive architecture:

```text
CLIENT IDEA
    ↓
Personal Hermes → IntentContract
    ↓
CEO Hermes → TaskPlan
    ↓
research / eligibility / requirements / evidence
    ↓
bounded drafting worker(s) → WorkerResults
    ↓
CEO synthesis → mock proposal artifact → QA → OutcomeArtifact
    ↓
Personal Hermes → ClientExplanationPacket
```

## 2. Georgia-first fixture

- approved client organization fixture;
- real/archived Georgia opportunity snapshot governed by Book 3;
- exact OpportunityRevision;
- D0 DraftContextBundle;
- client intent created through Personal Hermes;
- CEO TaskPlan/TaskContracts;
- mock proposal Artifact.

## 3. D1 outputs

- visible opportunity/match rationale;
- visible grant/funder/winner/community research as available;
- application blueprint;
- one full mock proposal or a defined significant section set;
- distinct business-plan strategy stub if relevant;
- QA report;
- client explanation.

## 4. Restrictions (frozen)

- **MOCK / NON-SUBMISSION label required**;
- no L4/L5 action;
- unsupported facts stay placeholders/questions;
- **no fabricated testimonial/partnership**;
- exact source/evidence refs retained;
- sidechains available for review without entering Personal context.

## 5. Success metrics (frozen)

1. client intent survives Personal→CEO translation;
2. CEO can execute without raw client transcript;
3. worker outputs remain bounded;
4. factual claims trace to Book 3 evidence;
5. reset/reconstruct after generation succeeds;
6. mock proposal remains consistent with the exact opportunity revision.

## 6. Verified behaviors

- `test_d1_intent_survives_translation`
- `test_ceo_executes_without_raw_transcript`
- `test_claims_trace_to_book3_evidence`
- `test_no_fabricated_testimonial_or_partnership`
- `test_mock_proposal_consistent_with_exact_revision`
- `test_reset_reconstruct_after_generation`
