# G0 Book 8 — Production-Shaped Georgia Grant Vertical Slice Charter

**Charter id:** `G0_B8_CHARTER` · **Branch:** `grant-sector-r0-salvage`
**Predecessor:** Book 7 (sealed at `49b84a65`, external-review repairs
`4ca59800`, live D2 + closeout `002da233`/`28352e97`)

## 1. What the slice proves

The entire governed machine can take a realistic client intent and produce
a grounded, evaluated, recoverable grant package end-to-end:

```
CLIENT intent
  → Personal Hermes (IntentContract)
  → CEO Hermes (TaskPlan)
  → Opportunity discovery (governed source)
  → SourceSnapshot → OpportunityRevision
  → Deterministic Eligibility
  → Explainable Match (never overrides eligibility)
  → Funder/winner/community research (lineaged)
  → ApplicationProject (binds exact revision)
  → Requirements → Blueprint
  → bounded workers → real model drafting (governed Model Gateway)
  → Budget (reconciles, within ceiling)
  → Claim Ledger (every material claim supported)
  → Deterministic QA + Book 7 evaluation
  → Human review packet (NOT_PERFORMED honestly when no reviewer)
  → SUBMISSION_READY_MOCK (submission structurally impossible)
  → Client ExplanationPacket
  → Cold reconstruction from durable state
```

## 2. Out of scope (unchanged from plan §7)

External submission, legally binding certification, 50-state coverage,
generalized CRM/outreach, autonomous company operation, production
self-modification, runtime substrate adoption without Book 9 ADR.

## 3. Hard inputs from Books 1–7

The slice CONSUMES, never redesigns: IntentContract / TaskPlan /
TaskContract / WorkerResult / ContextBundle / DecisionRecord /
EvidenceClaim / CanonicalFact / ApplicationProject / OpportunityRevision /
Claim Ledger / ExplanationPacket; deny-by-default authority, tenant/project
isolation, server-side secrets, ToolGateway, ModelGateway (Book 7 phase B),
evidence authority, source precedence, historical replay, submission
disabled.

## 4. North-star test

A reviewer can answer every question in the Book 8 plan §51 (who is the
client, what did they ask, how was intent encoded, why this opportunity,
which revision, why eligible, what remains unknown, what research proved —
and did NOT prove, which requirement each section answers, which evidence
supports every claim, does the budget reconcile, what QA/eval found, what
the human reviewer approved/rejected, what amendment changed, cold-restart
survival, tenant/project isolation, submission impossibility,
reconstruction without chat memory) from durable contracts and evidence —
never "we special-cased that for the demo."

## 5. Truth rules

- BLOCKED is acceptable; FAKE PASS is not.
- Live model generation runs through the governed Model Gateway with the
  same credential/egress/authorization rules as D2-LIVE.
- Submission remains structurally impossible (`submission_enabled=false`).
- Every milestone is a staged commit; no giant final commit.
