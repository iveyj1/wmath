# TODO

## Inbox - to be categorized/planned
- None


## Immediate

Milestone 009 complete. Next immediate focus is Milestone 010 prototype packaging.

- [ ] Add README or expand docs with packaging/run summary.
- [ ] Select packaging path: venv instructions, PyInstaller, AppImage, or Flatpak.
- [ ] Add optional launcher script if useful.
- [ ] Review dependency pins and distribution notes.

## Core Backlog

- [x] Define `EvalInput`, `EvalOutput`, `RenderedRow`, and `Diagnostic` model classes.
- [x] Implement lexer.
- [x] Implement parser.
- [x] Add Qt-free plain-text row rendering helpers.
- [x] Implement scalar numeric evaluator environment.
- [x] Implement scalar value model with unit dimensions.
- [x] Implement unit dimension model.
- [x] Implement formatter.
- [x] Implement include resolver.
- [x] Add pytest coverage for parser and scalar evaluator behavior.

## UI Backlog

- [x] Open file dialog.
- [x] Save.
- [x] Save As.
- [x] Dirty state tracking.
- [x] Dirty replace confirmation.
- [x] MRU persistence.
- [x] Editor/render scroll sync, proportional basic.
- [x] Active line highlight, basic marker in rendered pane.
- [x] Increase prototype UI font sizes for readability.
- [x] Suppress known harmless Qt AT-SPI startup warning.
- [x] Avoid rendered-pane cursor out-of-range warnings by rendering results in a selectable label rather than a second text editor.
- [x] Include warning bar, missing/cycle include warnings.
- [x] Metadata read/write.
- [x] Value column placement.

## Documentation Backlog

- [x] Expand `docs/user.md` with current syntax examples.
- [x] Document Milestone 001 launch and architecture notes in user/dev docs.
- [ ] Add packaging notes after packaging approach is selected.

## Process Backlog

- [x] Keep `PLAN.md` milestone checkboxes current through Milestone 009.
- [x] Keep this TODO current through Milestone 009.
- [x] Add scripted test-run logging/freshness checks for pi prompts.
- [ ] Add prompt templates or skills when workflow gaps appear.
