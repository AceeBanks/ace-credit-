# Heuristic Triage Candidates: Contradiction Analysis

> **Purpose:** Heuristic triage of potential contradictions from Phase 0 Book 1 Part 3 analysis  
> **Status:** Heuristic triage candidates (NOT MAD decisions)  
> **Created:** 2026-08-01  
> **P0-REPAIR-01:** Reclassified from "ready for MAD review" to heuristic triage candidates  
> **Analysis:** 170,702 raw patterns → 92,647 deduplicated patterns → 1,345 heuristic candidates

---

## Heuristic Triage Analysis Summary

### Processing Results
- **Raw Pattern Matches:** 170,702
- **Deduplicated Patterns:** 92,647 (45.7% deduplication rate)
- **Noise (deferred):** 91,166 (general category, generic patterns)
- **Heuristic Candidates:** 1,345 (labeled as critical + high severity by heuristics)

### Severity Distribution (Heuristic Labels)
- **Critical (heuristic):** 1,331 (authority, security, capital categories)
- **High (heuristic):** 14 (architecture category only)
- **Medium (heuristic):** 53 (performance, integration) - deferred
- **Low (heuristic):** 83 (status, dependency) - deferred
- **Noise (heuristic):** 91,166 (general category, generic patterns) - deferred

**Important:** These are heuristic labels based on pattern matching, not evidence-backed contradictions. The actual opposing claims, source locations, and semantic resolution have not been validated.

---

## Limitation: Heuristic Pattern Matching

This analysis uses pattern matching and keyword heuristics to identify potential contradictions. It does NOT provide:

- **Exact opposing claims:** What specifically contradicts what
- **Source locations:** Precise file paths and line numbers for each claim
- **Semantic resolution:** Whether the apparent contradiction is real or contextual
- **Safe defaults:** What the safe operational default should be

The 1,345 "candidates" are patterns that *might* indicate contradictions, not confirmed material contradictions requiring MAD decisions.

---

## Evidence-Backed Contradiction Sample (Required Format)

To escalate actual contradictions to MAD, each must include:

| Field | Description | Example |
|-------|-------------|---------|
| Cluster ID | Unique identifier for the contradiction cluster | CONTRADICT-001 |
| Claim A | Exact text of first claim | "Agents have full execution authority" |
| Claim B | Exact text of opposing claim | "Agents require explicit approval for execution" |
| Source A | File path and line number for Claim A | `AGENTS.md:42` |
| Source B | File path and line number for Claim B | `OPERATOR_RULES.md:15` |
| Category | Type of contradiction (authority/security/architecture) | Authority |
| Why They Conflict | Explanation of the semantic conflict | Mutually exclusive permission models |
| Safe Default | Operational default until resolved | Deny by default, explicit approval required |
| MAD Input Needed | Whether MAD must decide or safe default suffices | No - safe default available |

**Current Status:** The 1,345 heuristic candidates have NOT been converted to this evidence-backed format. MAD review is NOT appropriate until this conversion is complete.

---

## Heuristic Category Patterns (Not Validated Contradictions)

### Category: Authority (1,252 heuristic matches)

**Heuristic Pattern:** Matches keywords related to agent authority, execution permissions, capital access, or operational control.

**Actual Status:** NOT validated as contradictions. These are pattern matches that *might* indicate authority-related conflicts.

**Required Evidence:** For each match, need exact opposing claims, source locations, and semantic conflict analysis.

### Category: Security (79 heuristic matches)

**Heuristic Pattern:** Matches keywords related to security controls, secret management, access controls, or credential handling.

**Actual Status:** NOT validated as contradictions. These are pattern matches that *might* indicate security-related conflicts.

**Required Evidence:** For each match, need exact opposing claims, source locations, and semantic conflict analysis.

### Category: Capital (0 heuristic matches)

**Heuristic Pattern:** No matches found for capital-related keywords.

**Actual Status:** No heuristic candidates in capital category (good baseline).

---

## High Severity Heuristic Patterns (14)

### Category: Architecture (14 heuristic matches)

**Heuristic Pattern:** Matches keywords related to system architecture, component relationships, or structural design decisions.

**Actual Status:** NOT validated as contradictions. These are pattern matches that *might* indicate architecture-related conflicts.

**Required Evidence:** For each match, need exact opposing claims, source locations, and semantic conflict analysis.

---

## Deferred Contradictions (Non-Material)

### Medium Severity (53) - Deferred
- **Category:** Performance, Integration
- **Reason:** Material for Phase 1-3, not Phase 0 completion
- **Action:** Defer to relevant phase

### Low Severity (83) - Deferred
- **Category:** Status, Dependency
- **Reason:** Informational, not blocking
- **Action:** Defer to later review

### Noise (91,166) - Deferred
- **Category:** General, generic patterns
- **Reason:** Documentation noise, not material contradictions
- **Action:** Archive, no action required

---

## Required Next Steps (Before MAD Review)

### Step 1: Evidence-Backed Cluster Analysis
Convert heuristic candidates to evidence-backed contradiction clusters using the required format:
- Extract exact opposing claims for each cluster
- Record precise source locations (file:line)
- Analyze semantic conflict (why they actually conflict)
- Determine safe default operational behavior
- Assess whether MAD input is truly needed

### Step 2: Top Cluster Sample Creation
Create a small evidence-backed sample (5-10 clusters) to validate the approach:
- Select highest-impact heuristic candidates
- Perform full evidence extraction
- Present to MAD for methodology validation
- Iterate on clustering approach if needed

### Step 3: Full Cluster Generation (After Sample Approval)
Process remaining heuristic candidates only after MAD approves the methodology:
- Apply evidence extraction process at scale
- Generate evidence-backed contradiction clusters
- Separate actual contradictions from false positives
- Identify clusters requiring MAD decisions vs. safe-default resolution

---

## Phase 0 Impact

### Blocking Phase 0 Completion?
**No** - Heuristic pattern matching does not block Phase 0 Reality Lock. These are candidates for investigation, not validated contradictions.

### Requiring MAD Approval?
**Not yet** - The 1,345 heuristic candidates require evidence-backed analysis before MAD review is appropriate. MAD should review the clustering methodology and sample clusters first.

### Safe Defaults Available?
**Unknown** - Safe defaults cannot be determined until actual contradictions are validated with exact claims and semantic analysis. Current labels are heuristic pattern matches, not evidence-backed conflicts.

---

## Next Actions

1. **Create Evidence-Backed Sample:** Select 5-10 high-impact heuristic candidates and perform full evidence extraction
2. **Validate Methodology:** Present sample clusters to MAD for clustering approach validation
3. **Full Analysis (After Approval):** Process remaining candidates using approved methodology
4. **Separate Real Contradictions:** Distinguish actual contradictions from false positives
5. **Apply Safe Defaults:** Only after evidence-backed contradictions are validated
6. **MAD Review:** Only for actual contradictions that cannot be resolved with safe defaults

---

**Status:** Heuristic triage candidates identified. Evidence-backed analysis required before MAD review. NOT ready for MAD decisions.