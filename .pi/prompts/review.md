---
description: Review current changes for correctness, docs, and plan alignment
argument-hint: "[focus]"
---
Review the current repository changes for: $ARGUMENTS

Check:

- Alignment with `spec.md`
- Alignment with `PLAN.md` and `TODO.md`
- Whether user-facing changes require `docs/user.md` updates
- Whether developer/process changes require `docs/dev.md` or `AGENTS.md` updates
- Test coverage gaps
- Low-dependency/modifiability concerns

Run read-only inspection commands as needed. Do not modify files unless explicitly asked.
