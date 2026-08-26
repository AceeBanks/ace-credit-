# G0 Book 2 — Chapter C13: Artifact & Document Family Model

## Decision

Represent the client's complete Phase 1 document suite coherently. Artifacts
are logical documents with immutable `ArtifactVersion`s.

Machine-readable source of truth: `config/g0/domain/artifact_families.yaml`.
Executable form: `prototype/g0/domain/artifacts.py` (+ B2.C8 `version_chain`).

## Required Phase 1 families (10)

GrantProposal, BusinessPlan, PitchDeck, FinancialPackage, PartnershipMaterial,
TestimonialMaterial, GoalSheet, ResearchReport, QAReport, SubmissionPackage.

- **PartnershipMaterial**: letters/partnership evidence or placeholders ONLY
  when supported.
- **TestimonialMaterial**: verified testimonial/support content only; never
  synthetic testimonial presented as real.
- **SubmissionPackage**: bundle/manifest of submission-ready artifacts; Phase 1
  may prepare but not submit.

## Version & mock rules

- Versions are immutable (frozen), numbered monotonically without gaps
  (`version_chain`), each with a content hash.
- Supersession lives on the Artifact: once SUPERSEDED, none of its versions may
  enter a package (`validate_package`); packages referencing unknown versions
  fail closed.
- Mock artifacts are visibly distinguishable (`status = MOCK`) and can never
  enter a real submission package (`for_real_submission` flag).

## Tests (8 in `test_artifacts.py`)

- artifact family coverage equals client Phase 1 scope (missing family visible)
- version history immutable (frozen; mutation raises)
- package cannot include superseded artifact version; unknown version fails
- package uses latest versions per artifact
- mock visibly distinct from approved/submission-ready
- mock version cannot enter real submission
- validator: missing family, missing version rule fail closed

Run: `python -m pytest tests/g0/book2/test_artifacts.py -q` — **8 passed**.
