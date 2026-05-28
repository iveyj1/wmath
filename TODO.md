# TODO

## Immediate

- [ ] Create Python project skeleton.
- [ ] Add minimal dependencies for PySide6 prototype.
- [ ] Create runnable app entry point.
- [ ] Implement main window layout:
  - [ ] header/status area
  - [ ] MRU placeholder bar
  - [ ] horizontal splitter
  - [ ] left source editor
  - [ ] right rendered pane
- [ ] Add placeholder render pipeline that mirrors source line count.
- [ ] Document launch instructions in `docs/user.md`.

## Core Backlog

- [ ] Define `EvalInput`, `EvalOutput`, `RenderedRow`, and `Diagnostic` model classes.
- [ ] Implement lexer.
- [ ] Implement parser.
- [ ] Implement scalar value model.
- [ ] Implement unit dimension model.
- [ ] Implement evaluator environment.
- [ ] Implement formatter.
- [ ] Implement include resolver.
- [ ] Add pytest test suite for core behavior.

## UI Backlog

- [ ] Open file dialog.
- [ ] Save.
- [ ] Save As.
- [ ] Dirty state tracking.
- [ ] Dirty replace confirmation.
- [ ] MRU persistence.
- [ ] Editor/render scroll sync.
- [ ] Active line highlight.
- [ ] Include warning bar.
- [ ] Metadata read/write.
- [ ] Value column placement.

## Documentation Backlog

- [ ] Expand `docs/user.md` with syntax examples once parser/evaluator exists.
- [ ] Expand `docs/dev.md` with architecture decisions as implementation solidifies.
- [ ] Add packaging notes after packaging approach is selected.

## Process Backlog

- [ ] Keep `PLAN.md` milestone checkboxes current.
- [ ] Keep this TODO current after each implementation turn.
- [ ] Add prompt templates or skills when workflow gaps appear.
