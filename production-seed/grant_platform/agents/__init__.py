"""G1 Wave 3 — Production Dual Hermes runtime.

Constitutional invariant (G0 §3): Personal Hermes != CEO Hermes != Workers.

- Personal Hermes owns the client relationship: conversations, intent
  extraction, clarification, curated memory continuity, explanations.
  It does NOT execute arbitrary operational tools.
- CEO Hermes consumes a governed IntentContract and produces durable
  TaskPlans / TaskContracts; workflow truth lives in the Store.
- Workers are task-scoped, stateless-by-default runners that claim tasks,
  assemble bounded ContextBundles, and write WorkerResults.
"""
