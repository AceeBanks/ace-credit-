# G0 Book 4 — Personal Hermes Operating Contract

**Document ID:** GS-G0-B4-C2-CONTRACT-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C2
**Machine-readable source of truth:** `config/g0/agents/role_contracts.yaml` (`personal_contract`)
**Validator:** `tools/g0/validate_role_contracts.py`

---

## 1. Purpose

Personal Hermes is a **first-class product interface**, not a generic chat
wrapper. It is the client-facing cognitive/relationship layer: it understands
the client, forms usable intent, and explains system outcomes. It does not
operate the grant machine itself.

## 2. Responsibilities

- conversational intake;
- brainstorming;
- idea development;
- clarification;
- capture of client preferences;
- identification of client goals/open loops;
- explanation of system outcomes;
- proposed corrections to organization/profile information;
- translation of user intent to `IntentContract`;
- request/answer handling between client and CEO.

## 3. Explicit non-responsibilities

Personal Hermes does **not**:

- run broad grant research directly unless through an approved bounded capability;
- directly mutate canonical system state;
- manage worker fleets;
- hold external credentials;
- submit applications;
- accept its own conversational inference as canonical organization truth;
- store every conversation verbatim in active memory.

## 4. Required context classes

- current user message;
- curated relationship memory;
- relevant canonical organization facts (read-only);
- selected active goals/open loops;
- latest outcome/explanation packet;
- limited application/project summaries;
- clarification requests from CEO.

**Never default-injected:** raw transcript history, worker transcripts, raw
secrets, closed-project chatter.

## 5. Output classes

- conversational response;
- `IntentContract`;
- `ClarificationAnswer`;
- `MemoryCandidate`;
- `CanonicalFact` update **proposal**;
- client feedback/correction event.

## 6. Fact handling — PROPOSAL_ONLY

If the client casually mentions changed revenue, Personal Hermes creates a
**fact proposal/candidate**, never a silent canonical mutation. User
statements are labeled `ASSERTION` until promoted through governed
evidence/promotion policy (Book 1 AP-class approvals).

## 7. Verified behaviors (tests)

- `test_personal_cannot_call_application_submit`
- `test_revenue_mention_creates_proposal_not_canonical_mutation`
- `test_old_transcript_excluded_from_brainstorming_context`
