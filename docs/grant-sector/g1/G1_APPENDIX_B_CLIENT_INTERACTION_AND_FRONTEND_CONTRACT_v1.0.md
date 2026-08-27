# G1 Appendix B — Client Interaction & Frontend Contract

**Version:** 1.0
**Status:** FROZEN (G1 implementation contract)
**Scope:** client-facing product (G1.9) — chat-first interaction and web
frontend. Does not reopen Book 9 architecture or Appendix A.

## 1. Frontend product principle

The Grant product is primarily **CHAT + WORK PROGRESS + DELIVERABLES** —
not a complex Grant-management dashboard.

```
USER SAYS WHAT THEY NEED
        ↓
SYSTEM WORKS
        ↓
USER SEES HIGH-LEVEL PROGRESS
        ↓
SYSTEM ASKS ONLY NECESSARY QUESTIONS
        ↓
FINAL DELIVERABLE APPEARS IN CHAT
```

## 2. Primary client UX

Main views:
- **CHAT**
- **CHAT HISTORY**
- **DELIVERABLES**
- **SETTINGS**

Optional secondary views (only where they materially help): Grant
shortlist, Application overview, Sources/evidence.

Do not overload navigation.

## 3. Chat UX

Support:
- streaming assistant responses;
- message history;
- file attachments;
- conversation titles;
- thread persistence (return and continue later);
- model selector;
- clarification requests;
- approval cards;
- source/context cards;
- deliverable cards.

A normal user types: *"We need funding for an after-school STEM program
in Atlanta."* — the platform handles the rest.

## 4. Manus/Genspark-style work preview

While work executes, expose operational state (NOT hidden chain-of-thought):

```
✓ Opportunity
✓ Eligibility
✓ Funder research
✓ Community evidence
Proposal:
✓ Executive Summary
✓ Organization Background
✓ Statement of Need
● Program Narrative
○ Evaluation
○ Sustainability
○ Budget Narrative
○ Final QA
○ Packaging
```

Expose: task state, artifact state, high-level progress, source count,
blocking questions, quality results.

Do NOT expose: private model reasoning, internal chain-of-thought, raw
worker scratchpads.

Work preview is driven by **durable task state**, never faked by timers.

## 5. Deliverable UX

Final output appears directly in chat:

```
Your proposal is ready.
Community Impact Grant — Full Proposal — 34 pages
Requirement Coverage: 100% | Evidence-backed claims: 47 | Critical issues: 0
[ Preview ] [ DOCX ] [ PDF ] [ Sources ]
```

Users do not need a separate document-management dashboard to find what
the agent created.

## 6. Hermes advanced consoles

Normal users do NOT choose Personal vs CEO Hermes — the system handles it
automatically. Under **Advanced → Agent Consoles**, provide optional access
to Personal Hermes and CEO Hermes native/local UI (open/embed/proxy).
Do NOT rebuild all Hermes UI functionality. Do NOT expose individual
workers as user-facing chats.

## 7. Frontend component decisions

| Component | Decision |
|---|---|
| shadcn/ui | **ADOPT FOUNDATION** |
| Beautiful UI | ADOPT AI-interaction primitives / reference |
| Transitions.dev | ADOPT selective motion |
| beUI | OPTIONAL POLISH |
| RareUI | OPTIONAL POLISH |
| Hermes native UI | REUSE for advanced agent consoles |
| design-extract | DEVELOPMENT TOOLING / PROTOTYPE ONLY |

No hard runtime dependency on inspiration/component websites.

## 8. Frontend technical direction

Preferred stack: **Next.js, React, TypeScript, Tailwind, shadcn/ui**.
Accessible primitives. Responsive desktop-first, mobile usable.
Do not spend excessive time on visual polish before the workflow works.

## 9. Main screen layout

```
left sidebar:  New Chat | History | Deliverables
center:        conversation
optional right: work preview panel
input:         text | attachments | model selector | send
```

## 10. Model picker (Appendix A integration)

Frontend reads the governed Model Registry. Default: **Auto — Recommended**.
Show only approved models with useful fields (context, task compatibility,
cost tier, quality/eval status, availability). If a selected model cannot
handle the job, block or fall back safely — backend retains final
eligibility authority.

## 11. Clarification / approval cards

Missing critical info → explicit card:

```
Need your input
"How many youth do you expect to serve annually?"
[ Answer ]
```

Never invent the value. Approval cards for governed actions where
required (ApprovalRegistry).

## 12. Contract enforcement

- Frontend talks only to `apps/api` endpoints (Book 9 contract map);
  never to canonical Postgres directly.
- Progress streams come from durable task state.
- Deliverables are object-storage-backed artifacts with version + quality
  status.
- Cross-tenant access, forged project IDs, unauthorized model selection,
  artifact URL access, and session expiry are tested (Wave 5).
- **Submission invariant:** the UI may show "Ready for review" or
  "Submission-ready package" but exposes NO automatic submit control;
  submission remains structurally disabled (Book 6/7/8 law). A future
  submission capability requires an explicitly governed phase.
- The UI never exposes individual workers as user-facing chats, and never
  displays hidden chain-of-thought or raw scratchpads.

## Commit: `G1-APPENDIX-B`
