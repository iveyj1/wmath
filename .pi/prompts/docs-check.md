---
description: Check whether user and developer docs are current
argument-hint: "[changed area]"
---
Check documentation currency for: $ARGUMENTS

Read `spec.md`, `PLAN.md`, `TODO.md`, `docs/user.md`, `docs/dev.md`, and relevant source files.

Identify:

- User-facing behavior missing from `docs/user.md`
- Developer workflow or architecture missing from `docs/dev.md`
- Plan/TODO items that are stale
- Any contradiction with `spec.md`

Do not modify files unless explicitly asked. Return a concise checklist of required updates.
