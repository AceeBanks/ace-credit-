# R0 Reject / Do-Not-Port Ledger

**Document ID:** GS-R0-REJECT-001  
**Version:** 0.2  
**Status:** DEEP-DIVE PASS COMPLETE  
**Date:** 2026-08-24

This ledger prevents legacy baggage, insecure prototypes, and domain-specific assumptions from entering the Grant Sector product merely because they exist in `larger-lab`.

| Item / Pattern | Source | Disposition | Reason / Replacement |
|---|---|---|---|
| Pure CEREBUS/MVE strategy logic | trading branches | **REJECT** | Trading-domain specific |
| Capital-routing trading logic | `capital-routing` | **REJECT** | Trading-domain specific |
| Crypto strategy/data logic | crypto branches | **REJECT** | Trading-domain specific |
| Broker/MT5 live-execution logic | trading runtime | **REJECT** | Capital-bearing market domain |
| Raw credentials in agent memory | archived Hermes memory | **REJECT — CRITICAL** | Secrets must live in scoped secret storage/service identities; redact prompts/logs/sidechains |
| One Hermes memory shared across Personal + CEO roles | conceptual anti-pattern | **REJECT** | Separate identity, context, memory, authority, and retention policies |
| Infinite append-only active memory | legacy/general agent anti-pattern | **REJECT** | Archive raw history; promote validated facts/lessons; TTL and compact active context |
| Full worker transcripts injected into parent context | common multi-agent anti-pattern | **REJECT** | Sidechain trace + bounded result packet |
| Model used as authoritative database | generic LLM anti-pattern | **REJECT** | Postgres/domain stores are canonical truth |
| Model decides deterministic eligibility after rules are normalized | generic agent anti-pattern | **REJECT** | Deterministic eligibility kernel |
| Redis as sole job truth | infrastructure anti-pattern | **REJECT** | Postgres stores accepted task intent; Redis only transport/cache |
| Old SQLite research queue as production authoritative queue | `master/core/research/agents/queue.py` | **REJECT literal implementation** | Port state semantics to Postgres-backed task model |
| Old SQLite research cache as tenant product store | `master/core/research/ingestion/cache.py` | **REJECT literal implementation** | Port dedupe/gating ideas into Postgres source registry |
| Query-length-only LLM routing | `master/core/research/agents/router.py` | **REJECT** | Route on task type, quality, privacy, capability, context, provider health, cost |
| LLM self-confidence as meaningful independent evidence | old finding evaluator | **REJECT** | Evidence confidence derived from source/directness/freshness/corroboration/extraction state |
| Hard-coded academic source-ranking model for grant evidence | old finding evaluator | **REJECT** | Grant-specific evidence hierarchy |
| Generic cognition graph / Neo4j-first architecture before domain need | old graph architecture | **DEFER / REJECT as default** | Start with explicit relational Evidence Graph; add graph DB only if evidence proves need |
| TurboVec/FAISS as default product truth layer | old semantic stack | **REJECT as default** | Simplify around canonical product datastore; add specialized vector infra only if benchmarks justify |
| Old local USB / Obsidian vault as commercial product truth | master storage doctrine | **REJECT** | Durable server-side tenant-isolated storage + backups |
| Blindly merging `master` | branch archaeology | **REJECT** | Selective transplant only |
| Blindly merging `execution-runtime-foundation` | branch archaeology | **REJECT** | Selective development-skill transplant only |
| Forking archived Hermes user state wholesale | Hermes archives | **REJECT** | Rebuild clean role-specific Hermes profiles |
| Regex denylist as sole authorization control | old pre-tool hook | **REJECT as sole control** | Typed capability/policy checks; regex remains defense-in-depth only |
| `eval()` on stored agent metadata | current `coevolution_protocol.py` | **REJECT — SECURITY** | JSON/schema-safe deserialization only |
| SQLite per-module databases scattered across runtime | older OCE modules | **REJECT for production architecture** | Central migration-managed Postgres domains; local SQLite allowed only bounded dev/offline cases |
| Autonomous self-heal changing product policy/authority | OCE/self-improvement concept risk | **REJECT** | Self-heal runtime failures only; policy changes require governed review |
| Consensus on every agent decision | generic multi-agent anti-pattern | **REJECT** | Use critics/consensus only where ambiguity/consequence justify cost |
| Single monolithic 20–40 page LLM generation call | grant-writing anti-pattern | **REJECT** | Blueprint → section generation → validation → compilation |
| AI detector score as proof of human authorship/quality | client workflow risk | **REJECT as truth** | Advisory signal only; factuality/alignment/completeness remain hard gates |
| Content-farm or design tool as document source of truth | archive content stack | **REJECT** | Canonical structured document model compiles into visual formats |
| Chat as program/project source of truth | historical workflow risk | **REJECT** | Durable project/task/decision state and artifacts |
| Historical test-count claims treated as current proof | master docs/catalog | **REJECT** | Re-run isolated tests against selected commit/environment after port |

## Preserve ideas separately

Rejecting a literal implementation does **not** mean discarding its useful contract. Examples:

- old SQLite queue → preserve state machine, retry/cost fields;
- old graph → preserve typed contradiction/support relationships;
- old hooks → preserve pre/post/stop interception architecture;
- old OCE memory → preserve WORK/LEARNED/KNOWLEDGE promotion concept;
- old Hermes memory → preserve curated continuity, reject secret retention and uncontrolled growth.
