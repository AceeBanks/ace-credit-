# G0-B7 — Internal Adversarial Self-Review (seal checkpoint)

| Field | Value |
|---|---|
| Checkpoint | `G0-B7-BOOK` internal review |
| Method | Attempt to prove the Book 7 completion claim false |
| Evidence | Fresh runs, this session, post final-suite green |

The self-review follows the mission (section 29): try to break the claim
that Book 7 can measure a candidate against a baseline, attack it, detect
hard regressions, preserve evidence integrity, and make auditable promotion
decisions. Each attack surface below was probed against live code.

## Attack surfaces probed

### 1. LLM judge self-preference / candidate self-promotion — CLOSED
`test_eval_properties.py::test_invariant_6_generators_cannot_self_promote`
and `test_skill_promotion.py::test_promotion_requires_independent_evaluator`
prove PROM-005: a candidate whose generator equals the evaluator is REJECTED
with `PROM-005_SELF_EVALUATION`. `evaluate_promotion` also vetoes on any hard
gate failure (PROM-001/002) and on hard-family regressions (PROM-002).

### 2. Humanizer semantic drift — CLOSED
Amendment 003 bounds Humanizer to STYLE_TRANSFORM with protected elements.
`HZR-A..J` (10 attacks: `$75,000`→`$750,000`, `October 15`→`16`, org-name
replacement, citation→unsupported claim, future→historical, invented
partnership, dropped terminology, removed uncertainty qualifier,
QUESTION→FACT, prose-up/factuality-down) all blocked —
`test_adversarial_eval.py::test_all_10_humanizer_attacks_blocked` (10/10)
and red-green provable (`test_hzr_attacks_are_red_green_provable`).

### 3. Private-data leakage — CLOSED
`test_privacy_leakage.py` (8 tests) covers privacy scans, cross-tenant
leakage, holdout contamination, memorization-not-capability, failure
harvesting, feedback-not-training-truth. Corpus registry enforces
tenant-scoped governance: `test_corpus_lineage.py::test_tenant_private_requires_governance`.

### 4. Holdout contamination — CLOSED
`EvalCorpusVersion` is immutable and hash-recorded; tampering raises
(`test_version_immutable_hash`). `corpus.py` detects duplicates and
contamination; holdout classes are enforced. No fixture is shared between
holdout and dev/golden without governance.

### 5. Fake gold labels — CLOSED
`label_origin` is restricted (`HUMAN_REVIEWER / HUMAN_ATTESTED / MODEL_GENERATED
/ SYNTHETIC / DERIVED_FROM_EVIDENCE`); model labels cannot masquerade as human
gold (`attack_19_model_label_as_human_gold` in the adversarial suite, plus
`EvalCase.__post_init__` validation).

### 6. Security regression — CLOSED
`test_security_regression.py` re-runs the Book 6 repair seams live through
`run_book6_seam_probes()` (grant authority ladder, capability binding,
tenant/project/resource binding, approval registry, DecisionRegistry,
gateway verification, replay, submission disablement) plus 12 hard gates.
Any seam failure flips `security_regression_pass` and the Reality Lock
(`test_injected_seam_defect_flips_security_regression`).

### 7. Weak statistical claims — CLOSED
`test_statistical_discipline.py` enforces `meaningful_improvement` (relative
margin), sample-size floors, confusion-matrix honesty, severity counting.
D2 records sample size, fixture identity, model/version (none), source
state, eval version, limitations.

### 8. Stale evaluation corpus — CLOSED
`CorpusRegistry.assert_immutable` + hash re-derivation on `get()`; a new
version is required for any corpus change (`next_version`). The Reality Lock
freshness suite (15 tests) re-derives the lock from current evidence; a stale
lock cannot authorize Book 8.

### 9. Unbound model versions — CLOSED
`ModelRun` and `LLMJudge` carry `model_version`; `evaluate_promotion`
requires baseline/candidate run refs; routing evaluation binds version refs
(`routing_eval.py`). No candidate can be promoted without a version-identified
baseline (`attack_40_self_improved_without_baseline`, `attack_31_rollout_version_unidentifiable`).

### 10. Non-reproducible D2 — CLOSED (honest harness-only)
`tools/g0/d2_harness.py` is deterministic and repeatable; `D2_REPRODUCTION
checks` in `test_d2_experiment.py` (14 tests) assert the artifact set and
the honest `BLOCKED_MODEL_RUNTIME` status. No fake model call, no fake
human-review score, no fabricated draft (baseline draft is derived
deterministically from governed evidence).

## Adversarial suite totals (fresh)

- 40 plan attacks (C29-01..40): all blocked with defense on; with defense
  disabled ≥40 fail (red-green, not vacuous).
- 10 Humanizer attacks (HZR-A..J): all blocked; red-green provable.
- P0 subset (leakage, bypass, submission, injection, aggregate-win-over-P0):
  all blocked.
- Combined adversarial/security/integration evidence:
  `test_adversarial_eval.py` + `test_security_regression.py` +
  `test_eval_properties.py` + `test_skill_promotion.py` +
  `test_change_promotion.py` + `test_corpus_lineage.py` →
  **72 passed** in one fresh run.

## Result

The completion claim **withstands** the self-review: no defect found that
permits a candidate to promote itself, break a hard gate, leak private
data, contaminate the corpus, or fake a D2 result. Book 7 stands sealed
with `status=PASS`, `p0_open=0`, `ready_for_book8=true`, submission
disabled, and the D2 live-model lane honestly reported as
`BLOCKED_MODEL_RUNTIME` (`d2_live_model_run_complete=false`).

## Residual risks (tracked, not P0)

- D2 live-model comparison remains unexercised until a model runtime is
  configured (harness + guards complete; disposition DEFER per promotion law).
- Human-review scores are not fabricated; none recorded (no reviewer).
- Statistical power is limited to a single-fixture experiment; Book 8
  expands coverage (recorded in `G0_B7_D2_EXPERIMENT_RECORD.md`).
