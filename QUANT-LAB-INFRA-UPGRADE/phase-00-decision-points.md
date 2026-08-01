# Phase 0 Books 2-4 Human Decision Points

> **Purpose:** Identify all human decision points required for Phase 0 Books 2-4 completion  
> **Status:** Draft - Decision point identification in progress  
> **Created:** 2026-07-31

## Overview

Phase 0 Books 2-4 require substantial strategic decisions that cannot be automated. This document catalogs all human decision points, their impact, required evidence, and approval authority.

---

## Book 2 (Reproducible Baseline) Decision Points

### Decision 2.1: Canonical Branch Strategy
**Question:** Which branch is the canonical source of truth?  
**Impact:** Affects all future development, CI/CD, and deployment  
**Evidence Required:**
- Current branch usage patterns
- GitHub default vs root README discrepancy
- Historical commit patterns
- Team collaboration workflow

**Options:**
- A) Keep `main` as canonical (GitHub default)
- B) Switch to `master` as canonical (README preference)
- C) Use `develop` for active development, `main` for releases

**Decision Maker:** MAD (Human Strategic Authority)  
**Approval Required:** Yes  
**Blocker for:** Book 2 completion, all downstream work

---

### Decision 2.2: Genuine Nautilus Backtest Fixture Selection
**Question:** Which backtest fixture will serve as the canonical reproducible baseline?  
**Impact:** Determines whether Nautilus is the canonical trading model per anchor A6  
**Evidence Required:**
- Available backtest fixtures in repository
- Data source for each fixture
- Determinism verification for each candidate
- Resource requirements

**Options:**
- A) Select existing fixture that meets criteria
- B) Generate new deterministic fixture
- C) Record critical gap if no suitable fixture exists

**Decision Maker:** Trading Systems Reviewer  
**Approval Required:** Yes  
**Blocker for:** Book 2 completion, Phase 0 Reality Lock

---

### Decision 2.3: Service Readiness Criteria
**Question:** Which services are considered "ready" and require full readiness verification?  
**Impact:** Determines scope of service readiness testing effort  
**Evidence Required:**
- Current service inventory from Book 1
- Service claims in documentation
- Runtime evidence of service activity

**Options:**
- A) Verify all services in inventory
- B) Verify only services with recent activity
- C) Verify only services with production claims

**Decision Maker:** OCE Operations Director  
**Approval Required:** No (operational decision)  
**Blocker for:** Book 2 completion

---

## Book 3 (Component Classification) Decision Points

### Decision 3.1: Vendored NautilusTrader Strategy
**Question:** What is the intended role of `projects/trading/nautilus_trader/`?  
**Impact:** Determines dependency management, update strategy, and FORGE integration approach  
**Evidence Required:**
- Upstream origin and commit/tag
- Local modifications present
- Current dependency usage
- Update requirements

**Options:**
- A) Maintain as editable local dependency
- B) Switch to packaged dependency (PyPI)
- C) Use as maintained fork with upstream sync
- D) Remove and use only upstream packages
- E) Record as accidental vendor and quarantine

**Decision Maker:** MAD (Strategic Dependency Decision)  
**Approval Required:** Yes  
**Blocker for:** Book 3 completion, Phase 1 planning

---

### Decision 3.2: MT5 MCP Classification
**Question:** What is the operational class of `projects/trading/mt5-mcp/`?  
**Impact:** Determines whether this can be used in Phase 1 integration  
**Evidence Required:**
- Current usage patterns
- Test coverage
- Broker connection status
- Alternative FX execution paths

**Options:**
- A) Canonical FX execution path
- B) Supporting utility (reusable logic only)
- C) Experimental tool surface
- D) Legacy interface (deprecated)
- E) Quarantined (unsafe/unknown)

**Decision Maker:** Trading Systems Reviewer  
**Approval Required:** Yes  
**Blocker for:** Book 3 completion, FX execution path

---

### Decision 3.3: Actual FX Execution Script Location
**Question:** Where is the operator's actual production FX execution script?  
**Impact:** Determines whether canonical FX path exists or is a critical external blocker  
**Evidence Required:**
- Search across repository
- External repository investigation
- Broker/platform investigation
- Manual documentation

**Options:**
- A) Found in repository (identify path)
- B) Found in external repository (document location)
- C) Only MT5 MCP exists (classify as 3.2)
- D) No known script (record critical external blocker)

**Decision Maker:** MAD (Operational Authority)  
**Approval Required:** Yes  
**Blocker for:** Book 3 completion, Phase 0 Reality Lock

---

### Decision 3.4: Agent Authority Boundaries
**Question:** What are the current authority boundaries for each agent/autopilot?  
**Impact:** Determines which agents can change production state  
**Evidence Required:**
- Runtime evidence of agent operations
- Tool access logs
- Current config files
- Historical progress notes

**Options:**
- A) Classify based on runtime evidence (current authority)
- B) Classify based on documented authority (claimed authority)
- C) Revoke authority from agents without explicit approval
- D) Grant authority to agents with demonstrated need

**Decision Maker:** OCE Operations Director  
**Approval Required:** Yes  
**Blocker for:** Book 3 completion, Phase 1 agent governance

---

### Decision 3.5: Canonical vs Supporting Component Classification
**Question:** Which components qualify as "canonical" vs "supporting"?  
**Impact:** Determines Phase 1 dependency graph and authority boundaries  
**Evidence Required:**
- Book 1 inventory
- Book 2 baseline results
- FORGE anchor compliance
- Independent validation readiness

**Options:**
- A) Strict canonical definition (must meet all criteria)
- B) Permissive canonical definition (partial credit)
- C) Default to supporting until verified canonical

**Decision Maker:** Independent Validator + MAD  
**Approval Required:** Yes  
**Blocker for:** Book 3 completion, Phase 1 handoff

---

## Book 4 (Reality Lock) Decision Points

### Decision 4.1: Critical Contradiction Resolution
**Question:** How to resolve the 170,702 contradictions identified in Book 1 Part 3?  
**Impact:** Determines whether Phase 0 can complete  
**Evidence Required:**
- Contradiction register from Part 3
- Source document review
- Historical evidence
- Runtime verification

**Options:**
- A) Manual resolution of critical contradictions
- B) Automated classification by severity
- C) Batch resolution by category
- D) Phase 0 completion blocked until all resolved

**Decision Maker:** MAD + Independent Validator  
**Approval Required:** Yes  
**Blocker for:** Book 4 completion, Phase 0 Reality Lock

---

### Decision 4.2: Quarantine Scope and Policy
**Question:** Which components require quarantine and what are the release conditions?  
**Impact:** Determines forbidden dependencies and Phase 1 boundaries  
**Evidence Required:**
- Book 3 classification results
- Security assessment
- Operational risk analysis
- Recovery feasibility

**Options:**
- A) Aggressive quarantine (safety-first)
- B) Targeted quarantine (known risks only)
- C) Monitoring quarantine (allow with warnings)
- D) No quarantine (accept all risks)

**Decision Maker:** Security Reviewer + MAD  
**Approval Required:** Yes  
**Blocker for:** Book 4 completion, Phase 1 handoff

---

### Decision 4.3: Canonical Path Map Finalization
**Question:** What is the final canonical path map for all functions?  
**Impact:** Phase 1 dependency structure and FORGE integration architecture  
**Evidence Required:**
- Book 3 classification
- Book 4 decision records
- FORGE anchor requirements
- Operational capability evidence

**Options:**
- A) Single canonical path per function
- B) Multiple canonical paths with primary designation
- C) Canonical path + supporting paths
- D) External blocker for functions without path

**Decision Maker:** MAD (Final Strategic Authority)  
**Approval Required:** Yes  
**Blocker for:** Book 4 completion, Phase 1 handoff

---

### Decision 4.4: Phase 0 Reality Lock Approval
**Question:** Does the Reality Lock Manifest accurately represent the system?  
**Impact:** Authorizes Phase 1 to begin; final Phase 0 gate  
**Evidence Required:**
- Complete Books 1-3 evidence
- All decision records approved
- Independent validation report
- No critical blockers

**Options:**
- A) Approve (Phase 1 can begin)
- B) Approve with noncritical findings (Phase 1 with conditions)
- C) Reject (return to Books 1-3)
- D) Block (critical issues prevent Phase 0 completion)

**Decision Maker:** MAD (Human Strategic Authority)  
**Approval Required:** Yes  
**Blocker for:** Phase 0 completion, Phase 1 start

---

## Decision Priority Matrix

| Decision | Priority | Automatable | Human Approval | Blocker |
|----------|----------|-------------|----------------|---------|
| 2.1 Canonical Branch | HIGH | No | Yes | Book 2 |
| 2.2 Nautilus Fixture | HIGH | Partial | Yes | Book 2 |
| 2.3 Service Readiness | MEDIUM | Yes | No | Book 2 |
| 3.1 Nautilus Strategy | CRITICAL | No | Yes | Book 3 |
| 3.2 MT5 MCP | HIGH | No | Yes | Book 3 |
| 3.3 FX Script | CRITICAL | No | Yes | Book 3 |
| 3.4 Agent Authority | HIGH | Partial | Yes | Book 3 |
| 3.5 Canonical Classification | HIGH | Partial | Yes | Book 3 |
| 4.1 Contradiction Resolution | CRITICAL | Partial | Yes | Book 4 |
| 4.2 Quarantine Policy | HIGH | No | Yes | Book 4 |
| 4.3 Canonical Path Map | CRITICAL | No | Yes | Book 4 |
| 4.4 Reality Lock Approval | CRITICAL | No | Yes | Phase 0 |

---

## Automatable vs Human-Required Tasks

### Fully Automatable (No Human Decision)
- Environment fingerprinting
- Test command discovery
- Test collection without execution
- Service startup verification
- Dependency graph construction
- Contradiction detection (already done)

### Partially Automatable (Human Decision Required)
- Test execution group selection
- Service readiness criteria application
- Component classification evidence gathering
- Contradiction severity classification
- Quarantine recommendation

### Fully Human-Required (Strategic Decisions)
- Canonical branch selection
- Nautilus dependency strategy
- FX execution path determination
- Agent authority boundaries
- Canonical vs supporting classification
- Quarantine policy
- Final Reality Lock approval

---

## Recommended Decision Sequence

1. **Immediate (Blocker Resolution):**
   - Decision 2.1: Canonical Branch Strategy
   - Decision 3.3: FX Script Location

2. **Book 2 Completion:**
   - Decision 2.2: Nautilus Fixture Selection
   - Decision 2.3: Service Readiness Criteria

3. **Book 3 Completion:**
   - Decision 3.1: Nautilus Strategy
   - Decision 3.2: MT5 MCP Classification
   - Decision 3.4: Agent Authority
   - Decision 3.5: Canonical Classification

4. **Book 4 Completion:**
   - Decision 4.1: Contradiction Resolution
   - Decision 4.2: Quarantine Policy
   - Decision 4.3: Canonical Path Map
   - Decision 4.4: Reality Lock Approval

---

## Next Steps

1. **Begin automatable work:** Book 2 environment fingerprinting
2. **Present decision points to MAD for initial guidance**
3. **Create decision record templates for each human decision**
4. **Document evidence requirements for each decision**
5. **Establish decision-making process and approval workflow**

---

**Status:** Decision points identified. Ready for human review and decision-making process definition.