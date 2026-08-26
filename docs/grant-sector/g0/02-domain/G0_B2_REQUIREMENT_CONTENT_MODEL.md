# G0 Book 2 — Chapter C11: Requirement & Application Content Model

## Decision

Represent the real grant-writing workload, not merely application metadata.
Requirements carry content semantics (prompt, constraints, word/page/character
limits, formatting rules, required evidence, required attachments, due
semantics, normalized state); responses link the evidence that satisfies them.

Machine-readable source of truth: `config/g0/domain/requirement_types.yaml`.
Executable form: `prototype/g0/domain/requirements.py` + models.

## Requirement → Response → Artifact

- One requirement may require multiple artifacts (`required_attachments`).
- One artifact may satisfy multiple requirements ONLY through explicit
  per-requirement `RequirementResponse` links.
- A response claiming COMPLETED/SATISFIED/VERIFIED for an evidence-bearing type
  MUST link the artifact version that satisfies it — unsupported partnership or
  testimonial content can never be invented as completed evidence.

## ProposalSection vs BusinessPlanSection

- **ProposalSection** supports DYNAMIC section sets: the client's 18-section
  model is a proposal template/profile (`profile_section_key`), while actual
  solicitation requirements may add/remove/reorder sections
  (`requirement_id`-driven).
- **BusinessPlanSection** is a separate type/schema: business plan serves
  business viability/operations, not funder-response semantics.

## Content alignment links

Sections may link to requirements, canonical facts, evidence claims,
statistics, project goals, budget lines, research findings. Unresolvable links
are reported (fail closed). Cross-document consistency: shared canonical facts
drive proposal/business plan/pitch deck/financials while each artifact retains
its own purpose and narrative structure.

## Tests (8 in `test_requirements.py`)

- one requirement may require multiple artifacts
- one artifact may satisfy multiple requirements only when explicitly linked
- proposal/business plan remain distinct types
- dynamic solicitation section coexists with client 18-section profile
- section content links resolve or fail closed
- unsupported partnership cannot be invented as completed evidence
- validator: missing requirement type, missing section family fail closed

Run: `python -m pytest tests/g0/book2/test_requirements.py -q` — **8 passed**.
