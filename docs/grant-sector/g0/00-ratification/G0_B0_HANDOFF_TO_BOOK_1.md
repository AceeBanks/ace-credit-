# G0 Book 0 — Handoff to Book 1

**From:** Book 0 ratification substrate (this package)
**To:** Book 1 — Constitutional control plane (`G0_BOOK_01_MASTER_IMPLEMENTATION_PLAN_v1.0.md`)
**Precondition met:** `ready_for_book1_ratification: true` (computed, see `G0_B0_REALITY_LOCK.json`)

## Binding constraints Book 1 must implement

1. **Typed capability/policy engine** (DEC-GOV-001, CD-010): authorization evaluates
   actor + tenant + project + capability + resource + authority + risk. Missing
   information ⇒ DENY. Regex denylists are defense-in-depth only.
2. **Authority levels preserve consequence separation** (DEC-DRAFT-002, DEC-SUB-001):
   CAN_GENERATE / CAN_RECOMMEND / CAN_PREPARE ≠ CAN_EXECUTE ≠ CAN_SUBMIT ≠
   CAN_MODIFY_SYSTEM_POLICY. `application.draft*` allowed at L2;
   submission/certify/sign unregistered in Phase 1.
3. **Submission prohibition is structural** (CD-003): the capability layer dominates
   tool availability; no browser/HTTP/connector path may confer submission. Book 1's
   Reality Lock must derive `submission_disabled` from registry/policy evidence.
4. **Memory isolation by identity** (CD-008, DEC-MEM-001): namespaces keyed per actor;
   no cross-role promotion; no secrets in memory/prompts/sidechains/logs (DEC-SEC-001).
5. **Policy mutation is protected** (DEC-GOV-002): agents cannot change their own
   authority; policy changes require governed approval above agent authority.
6. **Audit is durable and structured** (DEC-GOV-001, seed Package F): every consequential
   action emits actor/capability/request-ID-bearing audit evidence; raw logs are not
   the audit system.
7. **Framework sovereignty ban**: framework config alone can never authorize an action.

## Provisional downstream artifacts

Book 0 treats the Book 1 constitution draft (GS-G0-B1-CONST-001,
`provisional_downstream_draft`) as input context — it is referenced but NOT ratified
by Book 0. Ratification of Book 1 happens in Book 1's own gate.

## Deferred obligations inherited by Books 2+

- Semantica vs relational-baseline bake-off (CAND-SEMANTICA/CAND-RELATIONAL-BASELINE, Book 5).
- Parser bake-off incl. Unstructured; PixelRAG fallback benchmark (Book 3).
- Crawl4AI / GPT Researcher bounded-pattern evidence (Book 3); Eval Lab + Guardrails (Book 4);
  Univer licensing boundary (Book 5); Activepieces bounded fabric (Book 6).
- Fresh license/security due diligence before production use of every reused asset (DEC-LIC-003).

## Known limitations / open items (non-blocking)

- Stale "California-first" wording remains inside GS-R0-SEED-001 as historical lineage
  (deliberately not edited; superseded by Amendment 001 via CD-001).
- Historical test-count claims remain rejected until re-run post-port (CD-011 doctrine).
