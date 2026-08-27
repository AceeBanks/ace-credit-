"""G0-B7-C28 — Statistical discipline.

Avoid fake precision from tiny eval sets. For quantitative comparisons,
report sample size, mean/rate, distribution/variance, confidence or
bootstrap interval, paired comparisons, failure counts by severity, and
uncertainty. Do not claim a 2% improvement is meaningful from 20 noisy
subjective cases.
"""
from __future__ import annotations

import math
from statistics import mean, stdev


def summarize_metric(*, values: list[float], name: str) -> dict:
    """Mean/distribution/uncertainty summary. Returns null uncertainty for
    tiny samples rather than fake confidence."""
    n = len(values)
    if n == 0:
        return {"name": name, "sample_size": 0, "mean": None, "std": None,
                "ci95": None, "note": "no data"}
    m = mean(values)
    if n == 1:
        return {"name": name, "sample_size": 1, "mean": round(m, 4),
                "std": None, "ci95": None, "note": "sample of 1: no "
                "distribution claim"}
    s = stdev(values) if n > 1 else 0.0
    ci = 1.96 * s / math.sqrt(n)  # approximate 95% CI
    return {"name": name, "sample_size": n, "mean": round(m, 4),
            "std": round(s, 4), "ci95": round(ci, 4),
            "note": f"95% CI ≈ mean ± {round(ci, 4)} (normal approx)"}


def meaningful_improvement(*, baseline_mean: float, candidate_mean: float,
                           sample_size: int, noise: float) -> dict:
    """C28: do not claim an improvement is meaningful from noisy tiny sets."""
    if sample_size < 10:
        return {"meaningful": False,
                "reason": f"sample size {sample_size} < 10; insufficient "
                          "evidence for a promotion claim",
                "delta": round(candidate_mean - baseline_mean, 4)}
    delta = candidate_mean - baseline_mean
    if abs(delta) <= noise:
        return {"meaningful": False,
                "reason": f"delta {delta:.4f} within noise {noise}; not "
                          "statistically meaningful",
                "delta": round(delta, 4)}
    return {"meaningful": True, "delta": round(delta, 4),
            "reason": "delta exceeds noise at adequate sample size"}


def confusion_matrix(*, cases: list[dict], expected_key: str,
                     predicted_key: str) -> dict:
    """For binary deterministic tasks (e.g. eligibility): confusion matrix +
    high-severity error classes. False-positive (false eligible) is the
    highest-severity class."""
    tp = fp = tn = fn = 0
    for case in cases:
        exp, pred = case[expected_key], case[predicted_key]
        if exp and pred:
            tp += 1
        elif not exp and pred:
            fp += 1
        elif not exp and not pred:
            tn += 1
        else:
            fn += 1
    total = tp + fp + tn + fn
    return {
        "true_positive": tp, "false_positive": fp,
        "true_negative": tn, "false_negative": fn,
        "total": total,
        "false_positive_rate": round(fp / (fp + tn), 4) if (fp + tn) else 0.0,
        "false_negative_rate": round(fn / (fn + tp), 4) if (fn + tp) else 0.0,
        "accuracy": round((tp + tn) / total, 4) if total else 1.0,
        "highest_severity_class": "false_positive (false eligible) "
                                  "> conservative unknown",
    }


def severity_failure_counts(*, failures: list[dict]) -> dict:
    """C28: failure counts by severity (P0/P1/P2)."""
    out = {"P0": 0, "P1": 0, "P2": 0}
    for f in failures:
        sev = f.get("severity", "P2")
        if sev in out:
            out[sev] += 1
    out["total"] = sum(out.values())
    return out
