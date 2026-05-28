---
name: wmath-dev
description: Project workflow for implementing the Python/PySide6 wmath prototype. Use when continuing implementation, planning milestones, checking docs, or reviewing progress.
---

# wmath Development Workflow

Use this skill for implementation turns in the `wmath` prototype.

## Required Context

Before coding, read:

1. `spec.md`
2. `PLAN.md`
3. `TODO.md`
4. `AGENTS.md`
5. Relevant source and documentation files

## Implementation Loop

1. Identify the current milestone and acceptance criteria.
2. Work as far as practical on a coherent slice.
3. Keep computational core code free of Qt dependencies.
4. Prefer low dependencies and simple Python code.
5. Add or update tests for core behavior.
6. Run relevant tests/lint, or explain why not.
7. Update `PLAN.md` and `TODO.md`.
8. Update `docs/user.md` for user-facing changes.
9. Update `docs/dev.md` for architecture, testing, packaging, or workflow changes.

## Stop Conditions

Stop only when one of these is true:

- The requested milestone/slice is complete.
- A decision from the user is genuinely required.
- The work is blocked by missing tools or failing external dependencies.
- Further changes would be too large/risky for one coherent step.

## Final Response Format

End with:

- Completed work
- Tests run
- Docs status
- Remaining tasks / blockers
