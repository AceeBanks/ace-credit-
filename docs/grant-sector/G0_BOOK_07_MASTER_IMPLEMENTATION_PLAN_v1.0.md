# G0 Book 7 — Evaluation, Promotion & Quality Doctrine Master Implementation Plan

**Document ID:** GS-G0-B7-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 6 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Receives from:** Books 0–6 + Amendment 002  
**Hands off to:** Book 8 Production-Shaped Grant Vertical Slice; Book 9 Runtime Substrate ADR / clean production seed

---

# 0. Book Mission

Book 7 creates the quality-control laboratory that decides whether any model, prompt, skill, parser, retrieval strategy, workflow, routing rule, agent behavior, or proposed system improvement is actually better before it may influence production behavior.

The governing question is:

> **How does the platform prove a candidate change is safer, more correct, more useful, and operationally acceptable than the current baseline—without allowing the system to grade or promote itself by assertion?**

Book 7 is not a “self-improving super-agent” book. It is the opposite: it creates the controlled scientific boundary around improvement.

The required lifecycle is:

```text
OBSERVATION / FAILURE / IDEA
        ↓
CANDIDATE CHANGE
        ↓
VERSIONED EVALUATION CORPUS
        ↓
BASELINE vs CANDIDATE
        ↓
DETERMINISTIC ASSERTIONS
DOMAIN EVALUATION
SECURITY / AUTHORITY TESTS
EVIDENCE / FACTUALITY TESTS
COST / LATENCY / RELIABILITY
HUMAN REVIEW WHERE REQUIRED
        ↓
PROMOTE | REVISE | REJECT | QUARANTINE
        ↓
BOUNDED ROLLOUT / SHADOW / CANARY
        ↓
MONITOR
        ↓
KEEP | ROLLBACK
```

No candidate generator owns promotion authority.

---

# 1. Why Book 7 Exists

Books 1–6 establish what the machine is allowed to be:

- Book 1: constitutional authority and product boundaries;
- Book 2: canonical grant-sector meaning;
- Book 3: trusted external reality and source ingestion;
- Book 4: Dual-Hermes cognition, delegation and memory boundaries;
- Book 5: evidence, provenance, decisions and replay;
- Book 6: identity, security, tools, credentials and execution control.

Without Book 7, later optimization creates a dangerous gap:

```text
"this prompt seems better"
"this model feels smarter"
"this skill worked once"
"this plugin says it improved itself"
"this parser has a better demo"
"this route is cheaper"
        ↓
production change
```

Book 7 replaces that with evidence.

---

# 2. Constitutional Non-Dilution

Book 7 inherits and may not weaken:

1. Personal Hermes and CEO Hermes are distinct optimization targets.
2. Workers remain bounded and non-sovereign.
3. Agent memory is not canonical truth.
4. Book 1 authority dominates every evaluation and rollout action.
5. Book 2 domain semantics remain sovereign.
6. Book 3/5 evidence authority cannot be replaced by evaluator opinion.
7. Book 6 security gates cannot be traded away for quality or speed.
8. External grant submission remains disabled in G0.
9. A model may participate in evaluation but may not be the sole judge of its own promotion.
10. Generated output is not evidence merely because another model scores it highly.
11. Tenant-private data cannot silently become global training/evaluation material.
12. No external skill/evolution framework may write directly into production behavior.
13. Improvement must be reversible.
14. Promotion decisions are first-class auditable DecisionRecords.
15. Quality claims require versioned evidence.

---

# 3. Book Theme

## Observe → Measure → Compare → Challenge → Decide → Roll Out → Monitor → Roll Back

```text
PRODUCTION / SHADOW EXPERIENCE
        ↓
ObservationEvent
FailureCase
HumanFeedback
        ↓
CandidateChange
        ↓
EvalSuite + EvalCorpusVersion
        ↓
BaselineRun / CandidateRun
        ↓
MetricBundle
        ↓
PromotionDecision
        ↓
ReleaseCandidate
        ↓
Shadow / Canary / Bounded Rollout
        ↓
OperationalMonitoring
        ↓
KEEP or ROLLBACK
```

---

# 4. Required Artifact Set

```text
docs/grant-sector/g0/07-evaluation/
├── G0_B7_EVALUATION_CONSTITUTION.md
├── G0_B7_QUALITY_TAXONOMY.md
├── G0_B7_EVAL_CASE_CONTRACT.md
├── G0_B7_EVAL_CORPUS_GOVERNANCE.md
├── G0_B7_GOLDEN_SET_PROTOCOL.md
├── G0_B7_GEORGIA_FIXTURE_PACK.md
├── G0_B7_GRANT_DRAFT_QUALITY_RUBRIC.md
├── G0_B7_FACTUALITY_EVIDENCE_RUBRIC.md
├── G0_B7_ELIGIBILITY_MATCH_EVAL.md
├── G0_B7_RESEARCH_QUALITY_EVAL.md
├── G0_B7_PERSONAL_HERMES_EVAL.md
├── G0_B7_CEO_HERMES_EVAL.md
├── G0_B7_WORKER_EVAL.md
├── G0_B7_MEMORY_CONTEXT_EVAL.md
├── G0_B7_SECURITY_AUTHORITY_REGRESSION.md
├── G0_B7_MODEL_ROUTING_EVAL.md
├── G0_B7_PARSER_RETRIEVAL_EVAL.md
├── G0_B7_SKILL_PROMOTION_PROTOCOL.md
├── G0_B7_CHANGE_PROMOTION_PROTOCOL.md
├── G0_B7_SHADOW_CANARY_ROLLBACK.md
├── G0_B7_HUMAN_REVIEW_PROTOCOL.md
├── G0_B7_EVALUATOR_GOVERNANCE.md
├── G0_B7_COST_LATENCY_RELIABILITY.md
├── G0_B7_DATA_PRIVACY_LEAKAGE.md
├── G0_B7_EXTERNAL_TOOL_BAKEOFF.md
├── G0_B7_ADVERSARIAL_EVAL_REPORT.md
├── G0_B7_REALITY_LOCK_REPORT.md
└── G0_B7_HANDOFF_TO_BOOK_8.md

schemas/g0/evaluation/
├── eval_case.schema.json
├── eval_corpus_version.schema.json
├── eval_suite.schema.json
├── eval_run.schema.json
├── metric_bundle.schema.json
├── candidate_change.schema.json
├── promotion_decision.schema.json
├── release_candidate.schema.json
├── rollout_event.schema.json
├── rollback_event.schema.json
├── human_review.schema.json
├── failure_case.schema.json
└── feedback_event.schema.json

config/g0/evaluation/
├── quality_dimensions.yaml
├── promotion_thresholds.yaml
├── regression_gates.yaml
├── evaluator_policies.yaml
├── rollout_policies.yaml
└── privacy_policies.yaml

prototype/g0/evaluation/
├── models.py
├── runner.py
├── assertions.py
├── metrics.py
├── compare.py
├── promotion.py
├── rollout.py
├── rollback.py
├── evaluators.py
├── corpus.py
└── adapters/

tests/g0/book7/
├── test_eval_case.py
├── test_corpus_lineage.py
├── test_golden_sets.py
├── test_grant_quality.py
├── test_factuality.py
├── test_eligibility.py
├── test_research.py
├── test_personal_hermes.py
├── test_ceo_hermes.py
├── test_workers.py
├── test_memory_context.py
├── test_security_regression.py
├── test_model_routing.py
├── test_parser_retrieval.py
├── test_skill_promotion.py
├── test_change_promotion.py
├── test_rollout_rollback.py
├── test_evaluator_governance.py
├── test_privacy_leakage.py
└── test_adversarial_eval.py
```

---

# 5. Chapter B7.C1 — Evaluation Constitution

Freeze the laws governing quality claims and promotion.

## EVAL-LAW-001 — Baseline required

No candidate is “better” without an explicit baseline/version.

## EVAL-LAW-002 — Corpus/version required

Quality claims identify the exact evaluation corpus and suite version.

## EVAL-LAW-003 — Critical regressions veto aggregate improvement

A candidate cannot offset a security/authority/factuality P0 regression with better style or lower cost.

## EVAL-LAW-004 — Deterministic assertions dominate subjective graders

Where correctness can be checked deterministically, use deterministic evaluation.

## EVAL-LAW-005 — LLM judges are advisory unless independently anchored

Model graders may assess dimensions such as clarity/alignment, but cannot alone authorize production promotion.

## EVAL-LAW-006 — Evaluator independence

A candidate should not be sole evaluator of itself. Use deterministic checks, independent models, human review or combinations appropriate to risk.

## EVAL-LAW-007 — Evidence lineage required

Eval cases inherit Book 5 lineage.

## EVAL-LAW-008 — Promotion is explicit

No auto-writing candidate becomes production behavior without PromotionDecision.

## EVAL-LAW-009 — Promotion is reversible

Every promoted behavioral change has rollback identity/path.

## EVAL-LAW-010 — Security is non-compensatory

Book 1/6 violations are hard vetoes.

## EVAL-LAW-011 — Tenant privacy is non-compensatory

Cross-tenant leakage is P0 regardless of other scores.

## EVAL-LAW-012 — Production feedback is not automatically ground truth

User acceptance, win/loss, or downstream outcome may be informative but requires interpretation and lineage.

## EVAL-LAW-013 — Quality dimensions remain visible

Do not collapse everything into one opaque score.

## EVAL-LAW-014 — Evaluation infrastructure is replaceable

Promptfoo, Hermes Eval Lab, Dojo, SkillClaw or any other tool sits behind project-owned contracts.

## EVAL-LAW-015 — No silent online self-modification

G0 prohibits a production agent from observing itself and silently rewriting/promoting its own skills/prompts/routes.

Commit: `G0-B7-C1: freeze evaluation and promotion constitution`

---

# 6. Chapter B7.C2 — Quality Taxonomy

Define what “good” means before measuring it.

## Product-level dimensions

### Correctness

- eligibility correctness;
- requirement coverage;
- numerical correctness;
- factual accuracy;
- citation/evidence consistency.

### Grant usefulness

- funder alignment;
- organization/program alignment;
- specificity;
- completeness;
- actionability;
- coherent narrative;
- measurable outcome framing;
- budget/narrative consistency.

### Evidence quality

- support coverage;
- source authority;
- freshness;
- contradiction visibility;
- locator/provenance correctness.

### Agent behavior

- role adherence;
- correct delegation;
- bounded context use;
- no cross-project contamination;
- no unnecessary questions when canonical state answers them;
- no authority escalation.

### Operational quality

- latency;
- cost;
- reliability;
- retry behavior;
- recovery;
- token/context efficiency.

### Safety/security

- tenant isolation;
- secret non-exposure;
- tool policy compliance;
- prompt-injection resistance;
- approval compliance.

### Human experience

- clarity;
- appropriate confidence/uncertainty;
- useful explanation;
- edit burden;
- relationship continuity for Personal Hermes.

Each metric declares direction, units, collection method, confidence/variance where relevant, and whether it is a hard gate or optimization target.

---

# 7. Chapter B7.C3 — EvalCase Contract

## EvalCase

```yaml
eval_case_id:
case_type:
corpus_version_id:
source_lineage_refs:
input_fixture_refs:
expected_assertions:
rubric_refs:
privacy_class:
tenant_scope:
label_origin:
reviewer_refs:
created_at:
valid_for_versions:
```

Case types include:

- deterministic rule;
- structured extraction;
- grant opportunity;
- organization profile;
- eligibility;
- matching;
- research;
- drafting;
- budget;
- QA;
- Personal Hermes interaction;
- CEO orchestration;
- worker execution;
- security/adversarial;
- memory/reconstruction;
- tool execution.

No case without lineage/fixture identity.

---

# 8. Chapter B7.C4 — Eval Corpus Governance

## Corpus classes

- GOLDEN_PUBLIC;
- GOLDEN_SYNTHETIC;
- GOLDEN_HUMAN_REVIEWED;
- TENANT_PRIVATE_APPROVED;
- ADVERSARIAL;
- REGRESSION;
- SHADOW_PRODUCTION;
- HOLDOUT.

## Rules

1. corpus versions immutable;
2. additions create new version;
3. train/dev/eval/holdout separation explicit where learning occurs;
4. model-generated labels marked as such;
5. tenant-private examples never become global corpus by default;
6. duplicates and near-duplicates tracked;
7. contamination/leakage analysis required for important benchmarks;
8. historical cases retain source/effective-date context;
9. benchmark composition report required.

---

# 9. Chapter B7.C5 — Golden Set Protocol

Build a small high-quality corpus before a giant noisy corpus.

## Golden set hierarchy

### Tier G1 — deterministic gold

Exact facts/rules where expected answer is machine-verifiable.

### Tier G2 — expert-reviewed gold

Grant outputs/rubrics reviewed by knowledgeable humans.

### Tier G3 — adjudicated preference

Multiple acceptable outputs ranked/adjudicated with documented criteria.

### Tier G4 — adversarial gold

Known traps, conflicts, prompt injections, stale evidence, malformed opportunities.

## Rule

Golden quality > corpus size.

---

# 10. Chapter B7.C6 — Georgia-First Fixture Pack

Book 7 uses Georgia as the first state proof lane inherited from prior books.

Fixture pack should include, as source availability permits:

- federal opportunity applicable to Georgia;
- Georgia state opportunity;
- nonprofit organization profile;
- organization with incomplete eligibility facts;
- organization that is clearly ineligible;
- opportunity amendment/revision case;
- requirement-heavy solicitation;
- budget-heavy solicitation;
- scanned/complex PDF;
- historical award/winner evidence;
- community statistic evidence;
- contradictory/stale source case;
- prompt-injected/malicious source fixture;
- mock proposal with planted factual errors;
- mock proposal with unsupported historical claims;
- future-target vs historical-achievement distinction.

The fixture pack is for evaluation and shadow/mock work, not external submission.

Commit: `G0-B7-C2-C6: define quality taxonomy and governed Georgia eval corpus`

---

# 11. Chapter B7.C7 — Grant Draft Quality Rubric

Define a multi-dimensional grant rubric; do not use “sounds professional” as quality.

Dimensions:

1. requirement coverage;
2. funder/program alignment;
3. organization-specific grounding;
4. problem/need clarity;
5. proposed approach coherence;
6. outcomes/measures quality;
7. implementation realism;
8. budget/narrative consistency;
9. evidence/citation support;
10. factuality;
11. internal consistency;
12. specificity vs generic filler;
13. uncertainty honesty;
14. readability/structure;
15. forbidden fabrication absence.

## Deterministic checks first

Examples:

- required sections present;
- character/word limits;
- dates/amounts consistent;
- citations resolve;
- claims map to ledger;
- budget totals reconcile;
- prohibited unsupported claims absent;
- opportunity revision exact.

Subjective rubric grading comes after deterministic gates.

## Human edit burden

Track meaningful edits required after draft generation. Do not equate stylistic preference with factual failure.

---

# 12. Chapter B7.C8 — Factuality & Evidence Evaluation

Metrics:

- material claim support rate;
- citation precision;
- citation recall for citation-required claims;
- locator correctness;
- unsupported claim count;
- contradicted claim count;
- stale-evidence usage;
- source-authority compliance;
- assumption labeling accuracy;
- future-target/historical-fact classification accuracy.

## Hard gate

A candidate that increases prose quality while increasing unsupported material claims cannot promote.

---

# 13. Chapter B7.C9 — Eligibility & Match Evaluation

## Eligibility

Treat deterministic eligibility as classification/rule execution, not prose grading.

Measure:

- rule extraction accuracy;
- hard-rule evaluation accuracy;
- unknown handling;
- false eligible rate;
- false ineligible rate;
- revision sensitivity;
- explanation correctness.

False eligible on a hard requirement is higher severity than a conservative unknown.

## Matching

Separate:

- hard eligibility;
- relevance/alignment ranking;
- strategic attractiveness;
- evidence sufficiency.

Measure ranking quality against reviewed fixtures without allowing match score to override hard eligibility.

---

# 14. Chapter B7.C10 — Research Quality Evaluation

Research output must be evaluated for:

- source coverage;
- authority mix;
- historical award identity correctness;
- funder-priority grounding;
- community statistic correctness;
- geography/time fit;
- duplicate-source detection;
- unsupported inference;
- limitation disclosure;
- usefulness to proposal strategy;
- provenance completeness.

Social/Agent-Reach evidence, if used, is evaluated separately from official opportunity truth.

Commit: `G0-B7-C7-C10: implement grant drafting factuality eligibility and research evaluation`

---

# 15. Chapter B7.C11 — Personal Hermes Evaluation

Personal Hermes is evaluated for relationship/intake quality, not CEO execution depth.

## Core behaviors

- captures user intent accurately;
- asks only necessary questions;
- uses existing canonical profile before re-asking;
- preserves user preferences/decisions appropriately;
- distinguishes idea exploration from authorized work request;
- produces valid IntentContract;
- does not perform CEO-only operations;
- communicates uncertainty clearly;
- explains outcomes using governed ExplanationPacket;
- avoids cross-project/client contamination.

## Longitudinal tests

Evaluate multi-session continuity with cold reconstruction and preference updates.

A “warmer personality” cannot compensate for wrong intent translation.

---

# 16. Chapter B7.C12 — CEO Hermes Evaluation

CEO Hermes is evaluated for operational discipline.

Metrics/tests:

- IntentContract interpretation;
- plan decomposition quality;
- correct worker selection;
- task bounding;
- evidence/context selection;
- authority compliance;
- unnecessary tool-call rate;
- worker-result conflict handling;
- blocker detection;
- synthesis correctness;
- completion-state correctness;
- no client-relationship memory pollution;
- no hidden dependence on giant raw chat history.

## Feed-forward quality test

Evaluate:

```text
client idea
→ Personal interpretation
→ IntentContract
→ CEO plan
→ worker outputs
→ CEO synthesis
→ Personal explanation
```

Measure semantic preservation and drift at each boundary.

---

# 17. Chapter B7.C13 — Worker Evaluation

Workers are evaluated per task type.

Required properties:

- obey TaskContract;
- use only allowed context/tools;
- return structured WorkerResult;
- identify unresolved gaps;
- preserve evidence refs;
- do not promote scratch memory;
- do not expand scope;
- do not contact client directly unless explicitly designed;
- do not alter policy/canonical state without capability.

Worker intelligence is subordinate to task correctness.

---

# 18. Chapter B7.C14 — Memory & Context Evaluation

Test the Book 4 doctrine empirically.

## Scenarios

- cold restart;
- long-running client relationship;
- multiple simultaneous grants;
- conflicting updated preference;
- inactive project reactivation;
- huge worker trace;
- irrelevant old conversation;
- context compaction;
- source amendment;
- model/provider swap.

Metrics:

- mandatory anchor retention;
- relevant-memory recall;
- irrelevant-context rate;
- cross-project bleed;
- token footprint;
- reconstruction correctness;
- stale-memory usage;
- question repetition.

Compare bounded assembled context against raw-history baselines where useful.

Commit: `G0-B7-C11-C14: establish Dual-Hermes worker and context evaluation suites`

---

# 19. Chapter B7.C15 — Security & Authority Regression Suite

Every candidate behavioral/runtime change must run relevant Book 1/6 regressions.

Non-compensatory gates include:

- unknown capability denied;
- wrong tenant denied;
- wrong project denied;
- Personal→CEO authority escalation denied;
- worker scope escalation denied;
- expired approval denied;
- secret exposure absent;
- egress policy enforced;
- prompt injection cannot create authority;
- submission remains disabled;
- audit/provenance write required;
- cross-tenant retrieval absent.

No model/skill/runtime improvement can promote if these regress.

---

# 20. Chapter B7.C16 — Model & Routing Evaluation

Models are interchangeable implementation resources, not personalities embedded in architecture.

Evaluate per capability/task class:

- correctness;
- factuality;
- instruction adherence;
- structured-output validity;
- latency;
- cost;
- context-window behavior;
- tool-use reliability;
- variance/retry rate;
- safety regression;
- provider availability/fallback behavior.

## Routing

A routing candidate must prove value against a simpler baseline.

Possible route decisions:

```text
cheap deterministic/small model
→ routine classification/extraction

stronger model
→ complex research synthesis/drafting

fallback
→ provider failure or schema failure
```

Do not route merely because a plugin claims intelligent routing.

---

# 21. Chapter B7.C17 — Parser & Retrieval Evaluation

Book 3 parser candidates and Book 5 retrieval strategies get empirical comparison.

## Parser lanes

Include Marker per Amendment 002 plus existing candidates.

Metrics:

- text fidelity;
- headings;
- tables/forms;
- OCR;
- page/locator lineage;
- extraction errors;
- latency/cost;
- hardware needs;
- failure detection.

## Retrieval

Compare exact/relational/full-text/vector/graph strategies for appropriate tasks.

Do not reward semantic retrieval for tasks where exact lookup is the correct mechanism.

---

# 22. Chapter B7.C18 — Evaluator Governance

Evaluation itself can fail.

## Evaluator types

- deterministic assertion;
- schema validator;
- domain rule evaluator;
- statistical metric;
- independent LLM judge;
- pairwise preference judge;
- human reviewer;
- production outcome metric.

## Requirements

Each evaluator declares:

- what it measures;
- what it cannot measure;
- version;
- known bias/failure modes;
- required independence;
- calibration evidence where relevant.

## LLM judge calibration

Use reviewed cases to measure agreement, positional bias, verbosity bias and self-preference where practical.

Never let one opaque “quality judge” decide production promotion.

---

# 23. Chapter B7.C19 — CandidateChange Contract

Any proposed improvement becomes a typed candidate.

```yaml
candidate_change_id:
change_type:
baseline_version:
candidate_version:
source_or_generator:
reason:
expected_benefit:
risk_class:
affected_capabilities:
required_eval_suites:
rollback_ref:
status:
```

Change types:

- PROMPT;
- SKILL;
- MODEL;
- ROUTE;
- PARSER;
- RETRIEVAL;
- WORKFLOW;
- CONFIG;
- MEMORY_POLICY;
- CONTEXT_ASSEMBLY;
- TOOL_ADAPTER;
- RUNTIME_COMPONENT;
- RUBRIC/EVALUATOR.

Constitution/policy changes follow stricter governance and cannot masquerade as ordinary candidate changes.

---

# 24. Chapter B7.C20 — Skill Promotion Protocol

This chapter implements Amendment 002's single promotion path.

Candidate generators may include:

- archived Hermes Skill Eval Lab;
- Hermes Skill Factory pattern;
- SkillClaw;
- Hermes Dojo;
- 42-evey bounded plugins;
- Compozy skill resources if runtime candidate remains relevant;
- human-authored skills;
- failure-derived candidate lessons.

They may generate candidates only.

## Skill lifecycle

```text
OBSERVED NEED
→ candidate skill
→ static/security validation
→ sandbox execution
→ task-specific eval suite
→ regression suite
→ baseline comparison
→ human review if risk requires
→ PROMOTE / REVISE / REJECT / QUARANTINE
→ versioned release
→ monitor
→ rollback if needed
```

## Direct-write prohibition

No candidate framework may directly overwrite production Hermes skill directories.

## Skill identity

Every promoted skill has stable ID/version, provenance, author/generator, eval result, authority requirements and rollback version.

---

# 25. Chapter B7.C21 — Prompt / Workflow / Route Promotion

Apply the same discipline beyond skills.

## PromotionDecision

Must include:

- baseline/candidate refs;
- eval corpus/suite versions;
- metric comparison;
- hard-gate results;
- reviewer/approval where required;
- reason codes;
- rollout policy;
- rollback ref.

## Pareto behavior

Do not require every metric to improve. Allow explicit trade-offs only if no hard gate regresses and the trade-off is documented.

Example:

- 20% lower cost;
- equal factuality;
- +5% latency;
- no security regression;

may be acceptable.

But:

- prettier prose;
- +3 unsupported claims;

is not.

Commit: `G0-B7-C15-C21: implement regression model routing evaluator and promotion governance`

---

# 26. Chapter B7.C22 — Shadow, Canary & Rollback

G0 does not need unsafe autonomous production experimentation.

## Rollout classes

### OFFLINE_ONLY

No live influence.

### SHADOW

Candidate observes same inputs or replays traces but cannot affect client outcome.

### INTERNAL_CANARY

Limited internal/test users.

### BOUNDED_CLIENT_CANARY

Only after future authorization and only for low-risk reversible behavior.

### FULL

Promoted default.

During current G0 grant work, consequential external submission remains disabled regardless of rollout class.

## Rollback

Rollback must restore known baseline configuration/version without depending on agent memory.

Triggers may include:

- hard-gate failure;
- factuality degradation;
- security alert;
- latency/cost runaway;
- structured-output failure;
- human quality regression.

---

# 27. Chapter B7.C23 — Human Review Protocol

Human review is targeted, not ceremonial.

Required when:

- rubric dimension is materially subjective and high-impact;
- candidate changes client-facing grant strategy significantly;
- evaluation disagreement remains unresolved;
- security/policy boundary changes;
- production skill promotion risk exceeds threshold;
- gold-label creation/adjudication requires expertise.

## Reviewer record

```text
reviewer identity/role
case/candidate
rubric
scores/decision
comments/reason codes
conflicts of interest if relevant
timestamp
```

Inter-reviewer disagreement is data, not something to hide.

---

# 28. Chapter B7.C24 — Cost, Latency & Reliability

Quality must be operationally viable.

Track per capability:

- token/input/output use;
- model cost;
- external API cost;
- parser/OCR compute;
- p50/p95 latency;
- timeout rate;
- retry rate;
- schema failure rate;
- tool failure rate;
- recovery success;
- context size.

## Cost guard

Cost optimization cannot bypass correctness/evidence/security floors.

42-evey cost/delegation plugins may be evaluated as telemetry/helpers, not adopted as authority.

---

# 29. Chapter B7.C25 — Privacy, Leakage & Benchmark Integrity

## Threats

- tenant-private examples leaking into global eval;
- evaluation corpus copied into prompts visible to unrelated tenants;
- holdout contamination;
- model memorization mistaken for capability;
- duplicate examples inflating scores;
- production logs containing secrets;
- evaluator receiving unnecessary PII;
- candidate skill generated from another tenant's private workflow.

## Required controls

- privacy class on every case;
- tenant scope;
- redaction/minimization;
- explicit approval for generalized reuse;
- holdout separation;
- duplicate/near-duplicate analysis;
- audit of corpus exports;
- deletion/retention linkage.

Cross-tenant leakage = P0.

---

# 30. Chapter B7.C26 — Production Feedback & Failure Harvesting

Book 7 creates the safe input side of future improvement.

## FailureCase

Capture:

- capability/task;
- input/evidence refs;
- observed output;
- expected behavior if known;
- failure taxonomy;
- severity;
- reviewer/user feedback;
- reproducibility;
- candidate lesson refs.

## Feedback is not direct training truth

Examples:

- client dislikes tone → preference signal;
- grant loses → not proof draft was bad;
- reviewer corrects deadline → factual error candidate;
- worker repeatedly misses requirement → strong regression candidate.

Book 7 harvests evidence for improvement without letting anecdotes rewrite production behavior.

---

# 31. Chapter B7.C27 — External Evaluation Tool Bake-Off

Evaluate external tools only where they reduce implementation burden.

## Candidate roles

### Promptfoo

Potential test/eval orchestration, red-team and model/prompt comparison helper.

### Guardrails

Potential structured validation helper where its contracts fit.

### Hermes archived Skill Eval Lab

Reference/possible adapter for Hermes skill-specific evaluation.

### SkillClaw

Candidate skill evolution/generation mechanisms.

### Hermes Dojo

Performance/weakness detection candidate.

### Hermes Skill Factory

Workflow→candidate skill generation pattern; licensing must be resolved before code reuse.

### 42-evey plugins

Selective telemetry/cost/delegation/session helpers.

### Compozy skill lifecycle

Only if Compozy remains runtime candidate.

## Bake-off rule

The project owns:

```text
EvalCase
EvalCorpusVersion
EvalSuite
EvalRun
MetricBundle
CandidateChange
PromotionDecision
ReleaseCandidate
RollbackEvent
```

External tools adapt to those objects.

## Decision outcomes

- ADOPT_BOUNDED;
- WRAP;
- REFERENCE;
- DEFER;
- REJECT.

No wholesale “self-evolution stack.”

---

# 32. Chapter B7.C28 — Statistical Discipline

Avoid fake precision from tiny eval sets.

For quantitative comparisons, report where appropriate:

- sample size;
- mean/rate;
- distribution/variance;
- confidence interval or bootstrap interval;
- paired comparison where same cases used;
- failure counts by severity;
- uncertainty.

Do not claim a 2% improvement is meaningful from 20 noisy subjective cases.

For binary deterministic tasks such as eligibility, emphasize confusion matrices and high-severity error classes.

For ranking, use appropriate ranking metrics plus human/domain review.

For subjective drafting, combine rubric distributions, pairwise preference and edit burden rather than one mean score.

---

# 33. Chapter B7.C29 — Adversarial Evaluation Suite

Required attacks include at least:

1. candidate scores itself;
2. evaluator model is same candidate with self-preference;
3. prettier prose hides unsupported claims;
4. cheaper model drops requirement coverage;
5. faster parser loses table cells;
6. semantic retrieval improves recall but returns stale authority;
7. skill expands worker scope;
8. skill adds unauthorized tool call;
9. routing plugin chooses model lacking structured-output reliability;
10. memory optimization drops deadline anchor;
11. context optimization leaks another project;
12. Personal Hermes starts doing CEO work;
13. CEO starts accumulating relationship memory;
14. worker contacts client directly;
15. candidate bypasses Book 6 approval;
16. candidate enables submission capability;
17. prompt injection causes false evaluator PASS;
18. eval case has no provenance;
19. eval label was model-generated but presented as human gold;
20. tenant-private example enters global corpus;
21. holdout duplicated in development corpus;
22. duplicate cases inflate success rate;
23. source revision changes expected answer but corpus silently mutates;
24. LLM judge rewards verbosity;
25. LLM judge penalizes concise correct answer;
26. evaluator disagrees with deterministic truth;
27. human reviewers disagree materially;
28. candidate wins aggregate but fails P0 security case;
29. candidate wins average factuality but hallucinates one critical deadline;
30. rollback artifact missing;
31. rollout version cannot be identified;
32. SkillClaw/Dojo writes directly to production skill path;
33. Skill Factory derives candidate from private tenant workflow without approval;
34. cost plugin suppresses required research to save money;
35. model router changes behavior during benchmark unpredictably;
36. external eval tool unavailable;
37. evaluation database/index lost and corpus rebuild attempted;
38. historical benchmark cannot be reconstructed;
39. outcome feedback from a lost grant is treated as direct negative label;
40. system marks itself “improved” without baseline comparison.

All P0 cases must pass.

---

# 34. Chapter B7.C30 — Integration & Property Tests

Mandatory invariants:

```text
1. Every quality claim names baseline + corpus + suite + run.
2. Hard security/authority gates cannot be compensated by soft metrics.
3. Deterministic truth overrides subjective evaluator disagreement.
4. Eval corpus versions are immutable.
5. Tenant-private cases stay scoped.
6. Candidate generators cannot self-promote.
7. Production behavior changes only through PromotionDecision.
8. Promotion has rollback identity.
9. Personal and CEO Hermes have separate eval suites.
10. Worker evals enforce TaskContract boundaries.
11. Memory/context eval checks cold reconstruction and contamination.
12. Grant factuality measures material claim support.
13. Eligibility evaluation separates hard rules from ranking.
14. Research evaluation preserves evidence/limitations.
15. Model routing is measured against simple baseline.
16. Parser/retrieval evaluation uses task-appropriate truth.
17. External eval tools are replaceable.
18. Failure feedback becomes candidate evidence, not automatic production truth.
19. Historical eval runs are replayable from Book 5 lineage.
20. Submission remains disabled.
```

Property tests where practical:

- same immutable corpus/version hashes identically;
- promotion evaluation is idempotent for fixed deterministic inputs;
- hard-gate failure always vetoes promotion;
- rollback returns exact previous configuration identity;
- corpus export never includes unauthorized tenant cases;
- candidate serialization round-trip preserves affected capability/risk/eval requirements.

---

# 35. Chapter B7.C31 — Book 7 Reality Lock

Machine-readable output:

```json
{
  "book": "G0-B7",
  "status": "PASS|FAIL",
  "evaluation_constitution_pass": true,
  "quality_taxonomy_pass": true,
  "eval_case_contract_pass": true,
  "corpus_governance_pass": true,
  "golden_set_protocol_pass": true,
  "georgia_fixture_pack_ready": true,
  "grant_quality_eval_pass": true,
  "factuality_eval_pass": true,
  "eligibility_match_eval_pass": true,
  "research_eval_pass": true,
  "personal_hermes_eval_pass": true,
  "ceo_hermes_eval_pass": true,
  "worker_eval_pass": true,
  "memory_context_eval_pass": true,
  "security_regression_pass": true,
  "model_routing_eval_pass": true,
  "parser_retrieval_eval_pass": true,
  "skill_promotion_pass": true,
  "change_promotion_pass": true,
  "rollback_pass": true,
  "privacy_leakage_pass": true,
  "external_tool_bakeoff_complete": true,
  "adversarial_p0_pass": true,
  "submission_enabled": false,
  "p0_open": 0,
  "ready_for_book8": true
}
```

No `ready_for_book8=true` if the system lacks a reproducible baseline-vs-candidate promotion path or if any external evolution tool can modify production behavior outside it.

---

# 36. Chapter B7.C32 — Book 8 Handoff

Book 8 receives a real evaluation harness rather than a promise to “QA the vertical slice.”

Handoff includes:

```text
versioned Georgia/federal fixtures
golden sets
Grant draft rubric
factuality/evidence metrics
eligibility/match metrics
research metrics
Personal Hermes suite
CEO Hermes suite
worker suite
memory/context suite
security regression suite
cost/latency metrics
PromotionDecision contract
shadow/rollback contract
failure harvesting contract
external-tool dispositions
```

Book 8 must use these to evaluate the production-shaped vertical slice end-to-end.

Book 8 is not allowed to invent a new quality definition merely because the demo looks impressive.

---

# 37. Parallel-Agent Work Allocation

## Lane A — Constitution / Corpus

C1–C6.

Lands first because every later lane needs stable eval/corpus contracts.

## Lane B — Grant Domain Quality

C7–C10.

Drafting, factuality, eligibility/match, research.

## Lane C — Agent Quality

C11–C14.

Personal, CEO, workers, memory/context.

## Lane D — Regression / Models / Retrieval

C15–C18.

Security, routing, parsers/retrieval, evaluator governance.

## Lane E — Promotion System

C19–C23.

CandidateChange, skill/change promotion, rollout/rollback, human review.

## Lane F — Operations / Privacy / Tool Bake-Off

C24–C28.

Cost, leakage, failure harvesting, external eval tools, statistics.

## Lane G — Attack / Reality Lock

C29–C32.

Adversarial, integration/property, Reality Lock, handoff.

### Merge law

No lane may create its own independent promotion path or quality score that bypasses C1/C19–C23.

---

# 38. Commit Plan

```text
1. G0-B7-C1
   evaluation constitution

2. G0-B7-C2-C6
   quality taxonomy + corpus + Georgia fixtures

3. G0-B7-C7-C10
   grant quality/factuality/eligibility/research

4. G0-B7-C11-C14
   Personal/CEO/worker/context evaluation

5. G0-B7-C15-C18
   security/model/parser/evaluator governance

6. G0-B7-C19-C21
   candidate + skill/change promotion

7. G0-B7-C22-C23
   rollout/rollback + human review

8. G0-B7-C24-C28
   cost/privacy/failure/tool bake-off/statistics

9. G0-B7-C29-C30
   adversarial + integration/property tests

10. G0-B7-BOOK
    complete Book 7 implementation checkpoint

11. G0-B7-REPAIR-01...N
    external review repairs

12. G0-B7-RATIFY
    Reality Lock PASS after independent review
```

---

# 39. Allowed / Prohibited Paths

## Allowed

- evaluation docs/schemas/config;
- evaluation runner/prototype;
- versioned fixtures;
- adapters for Promptfoo/Guardrails/Hermes eval candidates;
- skill candidate sandbox;
- metrics/reports;
- replay/comparison tooling;
- shadow/rollback prototypes.

## Prohibited

- direct production self-modification;
- production auto-install of generated skills;
- changing Book 1 authority to make experiments easier;
- cross-tenant corpus reuse without governance;
- enabling grant submission;
- turning Book 7 into generic AGI benchmarking;
- adding personality/autonomy plugins unrelated to Grant machine quality;
- treating model judge score as evidence authority;
- adopting external evaluation state as canonical product state.

---

# 40. Definition of Done

Book 7 is complete only when:

1. evaluation constitutional laws are ratified;
2. quality dimensions/hard gates are explicit;
3. EvalCase/EvalCorpus/EvalRun contracts exist;
4. corpus lineage/privacy governance works;
5. Georgia-first golden fixture pack exists;
6. grant draft quality is measured beyond style;
7. factuality/evidence coverage is measured;
8. eligibility/match accuracy is measured;
9. research quality is measured;
10. Personal Hermes has its own longitudinal suite;
11. CEO Hermes has its own orchestration suite;
12. workers have task-boundary suites;
13. memory/context doctrine is empirically testable;
14. Book 1/6 regressions are hard promotion gates;
15. model/routing choices can be compared objectively;
16. parser/retrieval choices can be compared objectively;
17. evaluator bias/failure is governed;
18. every candidate change follows one promotion path;
19. skill evolution tools can generate but not self-promote;
20. rollback is proven;
21. cost/latency/reliability are measured without overriding quality floors;
22. privacy/holdout integrity passes;
23. production feedback becomes governed FailureCases;
24. external eval tools have bounded dispositions;
25. statistical claims include adequate uncertainty/context;
26. adversarial P0 suite passes;
27. Reality Lock has zero open P0;
28. Book 8 receives executable quality gates.

---

# 41. Book 7 North-Star Test

Suppose tomorrow someone proposes:

> “Install this Hermes plugin. It automatically improves prompts, routes tasks to cheaper models, learns skills from client workflows, and makes grant drafts 20% better.”

The system must be able to respond:

```text
What exact capability is changing?
What is the current baseline?
Which client/product contract could it affect?
Which eval corpus tests it?
Which security/authority regressions apply?
Does it improve factuality or only style?
Does it preserve evidence support?
Does it preserve Personal/CEO separation?
Does it leak tenant workflows?
What does it cost?
How reliable is it?
Who/what generated the candidate?
Who may approve promotion?
What version would be deployed?
How would it be shadowed/canary-tested?
How do we roll it back?
Can we reproduce the decision later?
```

If the answer is simply:

> “The plugin says it self-improves,”

Book 7 fails.

The desired machine does not chase intelligence theater.

It improves only when evidence proves the change belongs.