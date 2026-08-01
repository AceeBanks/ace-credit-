# OBB-01 Detailed Implementation Plan

> **Purpose:** Detailed implementation plan for OBB-01 Truth and Seam Lock  
> **Status:** Draft - Planning in progress  
> **Created:** 2026-08-01  
> **Alignment:** FINAL-ANCHOR-AND-BUILD-GUIDELINE.md

## Overview

OBB-01 Truth and Seam Lock consumes Phase 0 evidence to identify OpenBB integration seams without creating duplicate audit code. It can proceed in parallel with Phase 0 Books 2-4.

---

## Phase 0 Evidence Available for OBB-01 Consumption

### Book 1 - Workspace Inventory (Complete)
- **Repository Fingerprint:** repository-fingerprint.json
- **Core Components:** core-component-inventory.json
- **Trading Census:** trading-file-census.json (509 trading files)
- **Dependency Inventory:** dependency-inventory.json
- **Data Inventory:** data-inventory.json
- **Claims/Secrets:** claims-secrets-inventory.json (14,032 claims, 759 secrets)
- **Contradictions:** contradictions-register.json (170,702 raw, 1,345 material)

### Book 2 - Reproducible Baseline (Partial)
- **Environment Fingerprint:** environment-fingerprint.json
- **Test Discovery:** test-discovery.json (7 commands)
- **Bounded Execution:** bounded-test-execution.json (7/7 passing)

---

## OBB-01 Implementation Work Packages

### Work Package 1: Consume Phase 0 Evidence

**Objective:** Load and process existing Phase 0 artifacts without duplication

**Tasks:**
1. Load repository-fingerprint.json
2. Load trading-file-census.json
3. Load dependency-inventory.json
4. Load data-inventory.json
5. Load claims-secrets-inventory.json
6. Parse contradiction analysis results

**Deliverable:** `obb-evidence-digest.json` - Consolidated Phase 0 evidence for OBB use

---

### Work Package 2: Identify OBB-Relevant Components

**Objective:** From Phase 0 inventory, identify components that could interact with OpenBB

**Criteria for OBB Relevance:**
- Data ingestion paths
- Research/analysis tools
- Provider adapters
- Catalog/metadata systems
- Strategy backtest tools
- Market data access

**Tasks:**
1. Analyze 509 trading files for data access patterns
2. Identify current data providers
3. Identify research tools
4. Identify backtest engines
5. Identify data formats

**Deliverable:** `obb-seam-inventory.json` - Components with OBB relevance

---

### Work Package 3: Create Capability Matrix

**Objective:** Map identified components to OBB capabilities

**Capability Dimensions:**
- Which components currently provide what OpenBB could provide?
- Which components use data OpenBB could provide?
- Where are the integration seams?
- What are the data format differences?

**Tasks:**
1. Create current capability mapping
2. Create potential OpenBB capability mapping
3. Identify overlap and gaps
4. Document seam locations

**Deliverable:** `capability-matrix.json` - Current vs potential OpenBB capabilities

---

### Work Package 4: Generate Module Inventory

**Objective:** Use Phase 0 evidence to list relevant modules

**Tasks:**
1. List all OBB-relevant modules from inventory
2. Identify OpenBB-specific modules needed
3. Define dependency relationships
4. Document module interfaces

**Deliverable:** `module-inventory.json` - OpenBB-relevant modules

---

### Work Package 5: Create Simulation Debt Register

**Objective:** Document where simplified/simulated data exists

**Tasks:**
1. Identify standalone/simplified simulations from trading census
2. Identify pandas approximations vs genuine Nautilus
3. Identify generated fixtures vs real data
4. Document data quality debt

**Deliverable:** `simulation-debt-register.json` - Simulation debt catalog

---

## Safe Defaults Applied

### Data Provider Seam
**Default:** Current data providers are supporting until OpenBB integration is verified
**Authority:** No live data through OpenBB until Phase 1-3 completion

### Research Workspace Seam
**Default:** OpenBB Workspace as analyst cockpit only (no execution authority)
**Authority:** Research agents can use Workspace, but cannot qualify strategies

### Provider Normalization Seam
**Default:** FORGE adapter layer required (no direct OpenBB integration)
**Authority:** OCE controls adapter, not OpenBB

### Catalog/Query Seam
**Default:** Use existing catalog until OpenBB catalog is verified
**Authority:** OpenBB catalog as supplement, not replacement

### API Boundary Seam
**Default:** FORGE adapter only (no direct OpenBB API access)
**Authority:** OCE controls all adapter boundaries

---

## Deliverables Summary

| Deliverable | Purpose | Status |
|-------------|---------|--------|
| `obb-evidence-digest.json` | Consolidated Phase 0 evidence | Pending |
| `obb-seam-inventory.json` | OBB-relevant components | Pending |
| `capability-matrix.json` | Current vs potential capabilities | Pending |
| `module-inventory.json` | OpenBB-relevant modules | Pending |
| `simulation-debt-register.json` | Simulation debt catalog | Pending |

---

## Implementation Sequence

1. **Phase A: Evidence Consumption** (Current)
   - Load Phase 0 artifacts
   - Create evidence digest
   - No new inventory tools

2. **Phase B: Seam Identification** (After Phase A)
   - Analyze trading files
   - Identify OBB-relevant components
   - Create seam inventory

3. **Phase C: Capability Mapping** (After Phase B)
   - Create capability matrix
   - Identify overlaps and gaps
   - Document seam locations

4. **Phase D: Module Analysis** (After Phase C)
   - Generate module inventory
   - Define dependencies
   - Document interfaces

5. **Phase E: Debt Registration** (After Phase D)
   - Identify simulations
   - Document data quality debt
   - Create debt register

---

## Gate: Phase 0 Reality Lock

**OBB-01 planning can proceed now** (not gated by Phase 0 completion)
**OBB-01 runtime integration is gated** by Phase 0 Reality Lock
**OBB-02+ requires Phase 1-3 completion**

---

## Next Actions

1. **Immediate:** Begin evidence consumption (load Phase 0 artifacts)
2. **Parallel:** Continue Phase 0 Books 2-4 completion
3. **Coordination:** Align OBB-01 timing with Phase 0 Reality Lock
4. **Documentation:** Create detailed implementation records
5. **Approval:** Present OBB-01 plan to MAD for review

---

**Status:** OBB-01 detailed plan complete. Ready for evidence consumption.