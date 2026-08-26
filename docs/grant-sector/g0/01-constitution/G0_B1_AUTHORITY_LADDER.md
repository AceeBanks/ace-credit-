# G0 Book 1 — Authority Ladder & Matrix

**Chapters:** B1.C4 · **Machine-readable source:** `config/g0/policy/authority_matrix.yaml`

Authority is defined **independently of tools**: a level describes what KIND of
effect an action has on the world, not which library performs it.

| Level | Name | Essence | Hard limits |
|---|---|---|---|
| L0 | Observe | read-only inspection | no mutation, no external comms |
| L1 | Propose | questions, shortlists, plans, corrections | nothing canonical except labeled non-canonical drafts |
| L2 | Safe Execute | research, ingestion, eligibility, ranking, drafting, QA, internal artifacts | NO send/sign/certify/submit; no silent overwrite of protected facts |
| L3 | Managed Execute | governed internal state mutation | always audited + policy-controlled |
| L4 | External Action | outreach, CRM, approved non-binding transmission | requires approval policy |
| L5 | Submission / Legally Material | submit/certify/sign/bind/attest | **DISABLED for Phase 1** |

## Initial ceilings

| Actor | Ceiling |
|---|---|
| Human Client / Admin | Human sovereign within product role |
| Personal Hermes | L1 |
| CEO Hermes | L2 |
| Worker | task-scoped L2 |
| Deterministic Service | narrow L3 transitions where predefined |
| Source Adapter | L2 source operations only |
| Outreach Agent | disabled (future) |
| Submission Agent | disabled (future) |

## Plan-mandated scenario resolutions

| Scenario | Resolution |
|---|---|
| `application.draft_full_proposal` @ CEO L2 | ALLOW (AP1 review-after) — LAW-B1-013 |
| `application.submit` @ CEO L2 | DENY (L5 > ceiling AND phase DISABLED AND APX) |
| `email.send` (`communication.send`) @ CEO L2 | DENY (capability DISABLED; CEO not in allowed actors) |
| worker researches assigned grant but changes tenant/profile | DENY (task scope + tenant scope checks) |
| Personal Hermes proposes profile change | ALLOW as proposal (non-canonical) |
| Personal Hermes accepts/promotes profile change itself | DENY (ceiling L1 < L3; not in allowed actors) |
