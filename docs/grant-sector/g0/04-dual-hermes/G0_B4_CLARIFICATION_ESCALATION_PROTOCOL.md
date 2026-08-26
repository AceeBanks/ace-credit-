# G0 Book 4 — Clarification & Escalation Protocol

**Document ID:** GS-G0-B4-C5-PROTOCOL-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C5
**Schema:** `schemas/g0/agents/clarification_request.schema.json`
**Policy:** `config/g0/agents/clarification_policy.yaml`
**Validator:** `tools/g0/validate_intent_clarification.py`

---

## 1. Purpose

Allow CEO Hermes to obtain missing information **without becoming a second
independent client relationship**.

## 2. Flow

```text
CEO identifies missing critical input
        ↓
ClarificationRequest
        ↓
Personal Hermes
        ↓
asks user naturally
        ↓
ClarificationAnswer
        ↓
Intent amendment / fact proposal
        ↓
CEO resumes
```

## 3. ClarificationRequest

```yaml
clarification_id:
intent_id:
requesting_actor:
question_type:
question:
why_needed:
blocking:
expected_answer_type:
allowed_context_refs:
created_at:
```

## 4. Policy rules

| Rule | Content |
|---|---|
| CLARIFY-001 | No avoidable questions — the requester verifies the answer is not already in canonical state or Personal memory (`answerable_from_canonical_state`). |
| CLARIFY-002 | Personal never answers on behalf of the client by inference; eligibility-critical/factual questions go to the user or carry an explicit inference label. |
| CLARIFY-003 | Blocking is explicit; blocking eligibility-critical questions gate eligible status and draft readiness. |
| CLARIFY-004 | `why_needed` may be translated into user-friendly language without distortion. |
| CLARIFY-005 | Answers amend the IntentContract as a new version — never by silently mutating prior history. |
| CLARIFY-006 | Repeated blockers escalate to human review (max 2 repeats) rather than guessing. |

## 5. Verified behaviors

- `test_no_duplicate_clarification_when_answer_already_canonical`
- `test_unresolved_eligibility_critical_blocks_draft_readiness`
- `test_clarification_answer_amends_intent_version`
