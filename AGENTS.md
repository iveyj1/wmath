# Agent Instructions

This project is a Python/PySide6 working prototype of `wmath`, a free-form computational sheet for Linux desktop.

Always consult these files before implementation work:

- `spec.md` — authoritative product/language baseline
- `PLAN.md` — milestone plan and current focus
- `TODO.md` — detailed task backlog
- `docs/user.md` — user-facing behavior and usage
- `docs/dev.md` — architecture and development notes

## Development Rules

- Prefer low dependencies and easy local modification.
- Use Python and PySide6 for the prototype.
- Keep the evaluator/core independent from Qt UI code.
- Keep source files small and cohesive where practical.
- Add or update tests for parser/evaluator behavior.
- Run relevant tests before declaring work complete.
- Update `PLAN.md` and `TODO.md` after each implementation step.
- Update `docs/user.md` for user-facing behavior, syntax, shortcuts, diagnostics, persistence, or UI changes.
- If user docs are not updated, state why no docs update was needed.
- Work through the current plan as far as practical unless blocked.
- Clearly summarize completed work, tests run, docs status, and remaining tasks.

## Prototype Architecture Preference

Keep a clean boundary between UI and computation:

```text
wmath/
  app/        # PySide6 app shell, windows, widgets, actions
  core/       # lexer, parser, evaluator, units, formatter, includes
  storage/    # sheet files, sidecar metadata, MRU state
  tests/      # pytest tests, especially for core behavior
```

The core should expose a simple API usable without Qt, so it can be tested headlessly and possibly replaced/reused later.

## Documentation Policy

Any change affecting the following requires a docs update in the same turn:

- supported syntax
- evaluation semantics
- units or display formatting
- keyboard shortcuts
- file formats or metadata
- save/load/MRU behavior
- diagnostics or warnings
- visible UI behavior
- known limitations

If no documentation update is needed, explicitly say why in the final response.
