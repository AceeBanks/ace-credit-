# G0-B7-C5 — Golden Set Protocol

**Document ID:** GS-G0-B7-C5-GOLDEN
**Status:** RATIFIED (Book 7 chapter C5)

Build a small high-quality corpus before a giant noisy corpus.

## Golden set hierarchy

### Tier G1 — deterministic gold
Exact facts/rules where the expected answer is machine-verifiable (eligibility
outcomes, deadline/revision identity, budget totals, citation resolution).

### Tier G2 — expert-reviewed gold
Grant outputs/rubrics reviewed by knowledgeable humans; label_origin =
HUMAN_REVIEWER with reviewer refs recorded.

### Tier G3 — adjudicated preference
Multiple acceptable outputs ranked/adjudicated with documented criteria
(pairwise preference + human adjudication; disagreement is data, not noise).

### Tier G4 — adversarial gold
Known traps: prompt injections, stale evidence, malformed opportunities,
future-target vs historical-achievement confusions, malicious source fixtures.

## Rule

**Golden quality > corpus size.** A 40-case human-reviewed golden set beats a
4,000-case model-generated pile for promotion decisions.

## Label integrity

- G1/G4 labels derive from deterministic truth or known traps.
- G2 labels require reviewer identity + timestamp.
- G3 requires documented adjudication criteria.
- Model-generated labels are always marked MODEL_GENERATED and never
  presented as human gold (C29-19, EVAL-002).
