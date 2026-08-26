# G0 Book 4 — Worker Memory Policy

**Document ID:** GS-G0-B4-C14-MEMORY-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C14
**Policy:** `config/g0/agents/worker_context_policy.yaml`
**Prototype:** `prototype/g0/agents/memory_lifecycle.py`

---

## 1. Purpose

Prevent specialist workers from developing unnecessary persistent
autobiographical memory.

## 2. Default: stateless across tasks (frozen)

> Workers are **stateless across tasks**. Persistent worker-specific memory is
> prohibited unless a later ADR proves it materially improves quality and
> cannot be represented as shared promoted procedural knowledge.

## 3. What a worker may receive

- TaskContract;
- bounded ContextBundle;
- role skill/instructions;
- source/artifact refs;
- task-local scratch state.

## 4. What a worker may produce

- WorkerResult;
- sidechain;
- MemoryCandidate / lesson candidate when appropriate.

## 5. Scratch retention

Task scratch expires after configured retention unless needed for
audit/replay.

## 6. Verified behaviors

- `test_new_worker_instance_repeats_task_from_contract`
- `test_worker_does_not_require_hidden_memory`
- `test_worker_determinism_changes_with_inputs`
