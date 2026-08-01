# Phase 0 Books 2-4 Decision Classification

> **Purpose:** Classify Phase 0 Books 2-4 items by resolution approach  
> **Status:** Draft - Decision classification in progress  
> **Created:** 2026-07-31  
> **Updated:** 2026-08-01 - Applied safe defaults per architecture guidance

## Overview

Phase 0 Books 2-4 items are classified into five categories:
1. **Verified Fact** - Determinable from existing evidence
2. **Safe Default** - Apply established default without MAD decision
3. **Requires MAD Decision** - Strategic choice requiring human approval
4. **External Blocker** - Scoped to later phase, not current blocker
5. **Duplicate/Noise Contradiction** - Deduplicated, grouped, severity-ranked

**Principle:** Do not treat every unknown as a MAD decision or total Phase 0 blocker.

---

## Applied Safe Defaults

### Default 1: Canonical Branch
**Classification:** Safe Default  
**Decision:** `main` is canonical  
**Rationale:** GitHub default; master references are legacy/stale  
**MAD Decision Required:** No

### Default 2: NautilusTrader Dependency
**Classification:** Safe Default  
**Decision:** Pinned upstream dependency behind FORGE adapter  
**Action:** Quarantine vendored source until origin/modifications are documented  
**MAD Decision Required:** No

### Default 3: Nautilus Baseline Fixture
**Classification:** Safe Default  
**Decision:** Identify or create smallest deterministic local fixture with pinned data  
**Requirement:** Two identical reruns to prove determinism  
**MAD Decision Required:** No

### Default 4: MT5 MCP Classification
**Classification:** Safe Default  
**Decision:** Experimental/quarantined; not the canonical FX path  
**MAD Decision Required:** No

### Default 5: FX Execution Script
**Classification:** External Blocker  
**Decision:** External adapter currently unregistered  
**Scope:** FX execution blocked until location/interface recorded  
**Non-Blocker:** Research and data phases are not blocked  
**MAD Decision Required:** No (external blocker scoped to later phase)

### Default 6: Agent Authority
**Classification:** Safe Default  
**Decision:** Deny by default  
**Authority:** No production, capital, broker-writing, paper, shadow, sandbox, or live authority exists  
**MAD Decision Required:** No

### Default 7: Component Classification
**Classification:** Safe Default  
**Decision:** Strict classification  
**Default:** Supporting or quarantined until verified canonical  
**MAD Decision Required:** No

### Default 8: Quarantine Policy
**Classification:** Safe Default  
**Decision:** Targeted and enforceable  
**MAD Decision Required:** No

### Default 9: Canonical Path Map
**Classification:** Safe Default  
**Decision:** One canonical path per function, named supporting paths  
**MAD Decision Required:** No

### Default 10: Service Readiness
**Classification:** Safe Default  
**Decision:** Verify only services claimed canonical/current  
**MAD Decision Required:** No

---

## Contradiction Resolution Strategy

### Raw Detection: 170,702 Contradictions
**Classification:** Duplicate/Noise Contradiction  
**Action Required:** Deduplicate, group, severity-rank, escalate only material contradictions  
**MAD Decision Required:** Only for material contradictions after analysis

**Process:**
1. Group contradictions by category and source
2. Deduplicate identical or near-identical contradictions
3. Severity-rank: Critical (blocks Phase 0) vs Non-Critical (can defer)
4. Escalate only Critical contradictions to MAD
5. Document Non-Critical contradictions for later review

---

## Items Requiring MAD Decision

### Decision 1: Critical Contradiction Resolution
**Question:** How to resolve Critical contradictions after deduplication/severity-ranking?  
**Impact:** Phase 0 completion  
**Approver:** MAD  
**Status:** Pending (requires contradiction analysis first)

---

## Summary

| Category | Count | MAD Decisions Required |
|----------|-------|------------------------|
| Verified Fact | 0 | 0 |
| Safe Default | 10 | 0 |
| Requires MAD Decision | 1 | 1 |
| External Blocker | 1 | 0 |
| Duplicate/Noise Contradiction | 170,702 (raw) | After analysis |

**Total MAD Decisions Required:** 1 (after contradiction analysis)

---

## Next Actions

1. **Immediate:** Apply safe defaults to all applicable items
2. **Automatable:** Begin contradiction deduplication and severity-ranking
3. **After Analysis:** Present only Critical contradictions to MAD
4. **Continue:** Book 2-4 implementation with safe defaults applied
5. **OBB Planning:** Can proceed (planning not gated by Phase 0 completion)

---

**Status:** Decision classification corrected. Safe defaults applied. MAD decisions minimized to 1 pending contradiction analysis.