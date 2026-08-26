# G0 Book 1 — Human Approval Policy

**Chapter:** B1.C6 · **Machine-readable source:** `config/g0/policy/approval_matrix.yaml`

Approval is required exactly where consequence demands it — never as ceremony
on harmless internal automation.

| Class | Name | Semantics | Examples |
|---|---|---|---|
| AP0 | None | proceed freely | source fetch, draft generation, internal QA, match computation |
| AP1 | Review After | execute, then surface for inspection | research packs, draft versions, suggested promotions |
| AP2 | Approval Before | valid human approval ref REQUIRED pre-execution; missing/expired ⇒ DENY | canonical client-fact replacement, external comms, high-impact overrides |
| AP3 | Dual Approval | two distinct human principals | promote_change, policy amendment activation |
| APX | Prohibited in Phase | DENY unconditionally; approval cannot cure it | submission, certification, signing, binding commitments |

## The drafts special rule

Mock and real application drafts do **not** require pre-approval to generate
(AP0/AP1). This is deliberate: the product must deliver client value early
(LAW-B1-013). Approval IS required before a draft becomes represented as
client-approved/submission-ready final state.

## Approver roles

- `HUMAN_CLIENT_APPROVER` — AP1/AP2, tenant-scoped.
- `HUMAN_ADMIN_APPROVER` — AP1/AP2/AP3, platform-wide, A4-audited.
- `DUAL_OWNER_PLUS_ADMIN` — AP3 requires both as distinct principals.

## Constraints (enforced)

- No approver may approve their own self-authority expansion (LAW-B1-018).
- Approval refs carry approver id, timestamp, scope; expired ⇒ fail closed.
- APX cannot be satisfied by any approval — only constitutional amendment opens it.

Plan-mandated checks: generating a draft = AP0/AP1 ✔ · marking a package
approved = human approval required ✔ · submitting a package = APX ✔ ·
changing verified EIN from chat alone = AP2 or conflict workflow ✔
