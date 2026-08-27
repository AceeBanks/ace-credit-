# G0-B7-C2 — Quality Taxonomy

**Document ID:** GS-G0-B7-C2-TAX
**Status:** RATIFIED (Book 7 chapter C2)
**Config of truth:** `config/g0/evaluation/quality_dimensions.yaml`

Defines what "good" means before measuring it. Quality is multi-dimensional;
there is no single magical "grant quality score." Every metric declares
direction, units, collection method, and whether it is a hard gate or an
optimization target.

## Dimensions by family

### Correctness (HARD)
- eligibility correctness
- requirement coverage
- numerical correctness
- budget consistency

### Factuality (HARD)
- material claim support rate
- citation precision
- unsupported material claims (lower is better)
- contradicted claims (lower is better)
- stale-evidence usage (lower is better)

### Grant quality (OPTIMIZE, after deterministic gates)
- funder/program alignment
- organization-specific grounding
- problem/need clarity
- proposed approach coherence
- outcomes/measures quality
- implementation realism
- budget/narrative consistency (HARD where machine-checkable)
- completeness
- readability/structure

### Agent quality (HARD for role/context/contamination)
- role adherence
- correct delegation
- bounded context use
- semantic preservation
- no cross-project contamination

### Security (HARD, non-compensatory)
- capability compliance
- tenant isolation
- project isolation
- secret non-exposure
- tool authority compliance
- prompt-injection resistance

### Operations (OPTIMIZE)
- latency
- cost
- reliability
- context/token footprint

## Non-compensatory rule

Hard security/factuality failures are NON-COMPENSATORY:

```text
style +20% + cost -30% + tenant isolation FAIL = REJECT
```

A candidate cannot offset a security/authority/factuality P0 regression with
better style or lower cost (EVAL-LAW-003/010/011).

## Deterministic checks first

Where correctness can be tested deterministically, do not ask an LLM judge:

- required section present
- character/word limits
- budget totals
- deadline
- funding amount
- OpportunityRevision identity
- citation resolution
- Claim Ledger mapping
- unsupported material claim
- eligibility rule
- tenant scope
- project scope
- tool authority
- submission capability absent

LLM evaluators may evaluate clarity, organization-specific writing, narrative
coherence, tone and funder alignment only after deterministic gates pass.
