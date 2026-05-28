---
description: Finish current task with tests, docs, and plan updates
argument-hint: "[task]"
---
Finish the current task end-to-end: $ARGUMENTS

Before stopping:

- If implementation is not complete, warn user.
- For each relevant test/lint command, first run `.pi/scripts/testlog status -- <command>`.
- If status reports a fresh pass, reuse that result instead of rerunning.
- If status is stale or missing, run the command through `.pi/scripts/testlog run -- <command>`, or explain why it cannot be run.
- Update `PLAN.md` milestone checkboxes.
- Update `TODO.md`.
- Update `docs/user.md` for user-facing behavior changes.
- Update `docs/dev.md` for architecture/workflow changes.
- Summarize any blockers or deferred work.
- Commit to repo if tracked files have changed.

Proceed as far as practical without waiting for additional prompting unless a decision is genuinely required.
