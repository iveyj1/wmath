# TODO

## Inbox - to be categorized/planned
- None


## Immediate

Milestone 002 complete. Next immediate focus is Milestone 003 core data model and render pipeline improvements.

- [ ] Make placeholder renderer expose diagnostics/warnings in the UI.
- [ ] Refine active-line highlight rendering beyond the temporary `▶` marker.
- [ ] Review scroll sync behavior with longer documents.
- [ ] Consider moving row formatting out of `MainWindow` before parser/evaluator work.

## Core Backlog

- [x] Define `EvalInput`, `EvalOutput`, `RenderedRow`, and `Diagnostic` model classes.
- [ ] Implement lexer.
- [ ] Implement parser.
- [ ] Implement scalar value model.
- [ ] Implement unit dimension model.
- [ ] Implement evaluator environment.
- [ ] Implement formatter.
- [ ] Implement include resolver.
- [ ] Add pytest test suite for core behavior.

## UI Backlog

- [x] Open file dialog.
- [x] Save.
- [x] Save As.
- [x] Dirty state tracking.
- [x] Dirty replace confirmation.
- [x] MRU persistence.
- [x] Editor/render scroll sync, basic.
- [x] Active line highlight, basic marker in rendered pane.
- [x] Increase prototype UI font sizes for readability.
- [x] Suppress known harmless Qt AT-SPI startup warning.
- [x] Avoid rendered-pane cursor out-of-range warnings by rendering results in a selectable label rather than a second text editor.
- [ ] Include warning bar.
- [x] Metadata read/write.
- [ ] Value column placement.

## Documentation Backlog

- [ ] Expand `docs/user.md` with syntax examples once parser/evaluator exists.
- [x] Document Milestone 001 launch and architecture notes in user/dev docs.
- [ ] Add packaging notes after packaging approach is selected.

## Process Backlog

- [x] Keep `PLAN.md` milestone checkboxes current through Milestone 002.
- [x] Keep this TODO current through Milestone 002.
- [ ] Add prompt templates or skills when workflow gaps appear.
