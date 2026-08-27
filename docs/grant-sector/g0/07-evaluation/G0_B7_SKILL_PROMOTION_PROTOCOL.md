# G0-B7-C20 — Skill Promotion Protocol

**Document ID:** GS-G0-B7-C20-SKILL
**Status:** RATIFIED (Book 7 chapter C20)
**Implements:** Amendment 002 §6 single promotion path

Candidate generators may include: archived Hermes Skill Eval Lab, Hermes
Skill Factory pattern, SkillClaw, Hermes Dojo, 42-evey bounded plugins,
Compozy skill resources (if runtime candidate remains relevant), human
skills, failure-derived lessons. **They may generate candidates only.**

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

No candidate framework may directly overwrite production Hermes skill
directories (C29-32 attack). Every promoted skill has stable ID/version,
provenance, author/generator, eval result, authority requirements and
rollback version.
