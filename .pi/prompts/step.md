---
description: Continue implementation from PLAN/TODO
argument-hint: "[focus]"
---
Read `spec.md`, `PLAN.md`, `TODO.md`, `AGENTS.md`, and relevant source files.

Continue implementation as far as practical for: $ARGUMENTS

Requirements:

- Follow the current milestone unless the focus says otherwise.
- Prefer low dependencies and simple, modifiable code.
- Keep core logic independent from Qt UI code.
- Add or update tests for parser/evaluator/core behavior.
- Run relevant tests through `.pi/scripts/testlog run -- <command>`, or explain why they cannot be run.
- Update `PLAN.md` and `TODO.md` to reflect completed and remaining work.
- Update `docs/user.md` if user-facing behavior changed.
- End with: 
   - completed work
   - tests run/passed/failed
   - docs status
   - remaining tasks for $ARGUMENTS or "$ARGUMENTS implementation complete"
   - a brief manual smoke test procedure if that makes sense.
