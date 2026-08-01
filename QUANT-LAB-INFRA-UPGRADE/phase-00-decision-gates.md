# Phase 0 Decision Gates (Corrected)

> **Purpose:** Define decision gates for Phase 0 Books 2-4 with safe defaults applied  
> **Status:** Corrected - Safe defaults applied, MAD decisions minimized  
> **Created:** 2026-07-31  
> **Updated:** 2026-08-01

## Overview

Phase 0 decision gates with safe defaults applied. Most items are now verified facts or safe defaults requiring no MAD decision. Only 1 gate requires MAD approval after analysis.

---

## Safe Default Gates (No MAD Decision Required)

### Gate 1: Canonical Branch
**Status:** RESOLVED (Safe Default)  
**Decision:** `main` is canonical  
**Rationale:** GitHub default; master references are legacy/stale  
**Action:** Update any remaining master references in documentation

### Gate 2: NautilusTrader Dependency
**Status:** RESOLVED (Safe Default)  
**Decision:** Pinned upstream dependency behind FORGE adapter  
**Action:** Quarantine vendored source until origin/modifications are documented

### Gate 3: Nautilus Baseline Fixture
**Status:** OPEN (Safe Default)  
**Decision:** Identify or create smallest deterministic local fixture  
**Requirement:** Two identical reruns to prove determinism  
**Action:** Implement fixture selection/creation

### Gate 4: MT5 MCP Classification
**Status:** RESOLVED (Safe Default)  
**Decision:** Experimental/quarantined; not canonical FX path  
**Action:** Classify as experimental in Book 3

### Gate 5: FX Execution Script
**Status:** RESOLVED (External Blocker)  
**Decision:** External adapter currently unregistered  
**Scope:** FX execution blocked until location/interface recorded  
**Non-Blocker:** Research and data phases are not blocked  
**Action:** Document as external blocker for Phase 9

### Gate 6: Agent Authority
**Status:** RESOLVED (Safe Default)  
**Decision:** Deny by default  
**Authority:** No production, capital, broker-writing, paper, shadow, sandbox, or live authority  
**Action:** Apply default in Book 3 classification

### Gate 7: Component Classification
**Status:** OPEN (Safe Default)  
**Decision:** Strict classification  
**Default:** Supporting or quarantined until verified canonical  
**Action:** Implement classification logic with safe defaults

### Gate 8: Quarantine Policy
**Status:** RESOLVED (Safe Default)  
**Decision:** Targeted and enforceable  
**Action:** Implement targeted quarantine in Book 4

### Gate 9: Canonical Path Map
**Status:** OPEN (Safe Default)  
**Decision:** One canonical path per function, named supporting paths  
**Action:** Implement path mapping with safe defaults

### Gate 10: Service Readiness
**Status:** OPEN (Safe Default)  
**Decision:** Verify only services claimed canonical/current  
**Action:** Implement service readiness verification

---

## MAD Decision Gate (After Analysis)

### Gate 11: Critical Contradiction Resolution
**Status:** OPEN (Requires Analysis First)  
**Blocker:** Phase 0 completion  
**Approval Authority:** MAD

### Pre-Gate Analysis Required
- [ ] Deduplicate 170,702 raw contradictions
- [ ] Group contradictions by category and source
- [ ] Severity-rank: Critical vs Non-Critical
- [ ] Identify Critical contradictions (block Phase 0)
- [ ] Document Non-Critical contradictions (defer to later)

### Decision Options
- **Option A:** Resolve Critical contradictions
- **Option B:** Record as Phase 0 blocker
- **Option C:** Defer Non-Critical contradictions

### MAD Approval Required
- Only for Critical contradictions after analysis
- Non-Critical contradictions can be deferred

---

## Gate Status Dashboard

| Gate | Status | Type | MAD Approval | Action |
|------|--------|------|--------------|--------|
| 1: Canonical Branch | RESOLVED | Safe Default | No | Update docs |
| 2: Nautilus Strategy | RESOLVED | Safe Default | No | Quarantine vendor |
| 3: Nautilus Fixture | OPEN | Safe Default | No | Implement |
| 4: MT5 MCP | RESOLVED | Safe Default | No | Classify experimental |
| 5: FX Path | RESOLVED | External Blocker | No | Document blocker |
| 6: Agent Authority | RESOLVED | Safe Default | No | Apply default |
| 7: Classification | OPEN | Safe Default | No | Implement |
| 8: Quarantine | RESOLVED | Safe Default | No | Implement |
| 9: Path Map | OPEN | Safe Default | No | Implement |
| 10: Service Readiness | OPEN | Safe Default | No | Implement |
| 11: Contradictions | OPEN | MAD Decision | Yes (after analysis) | Analyze first |

---

## Next Actions

1. **Immediate:** Begin contradiction deduplication and severity-ranking
2. **Parallel:** Implement safe default gates (3, 7, 9, 10)
3. **After Analysis:** Present only Critical contradictions to MAD
4. **Continue:** Book 2-4 implementation with safe defaults
5. **OBB Planning:** Can proceed (planning not gated by Phase 0)

---

**Status:** Safe defaults applied. MAD decisions minimized to 1 pending contradiction analysis.