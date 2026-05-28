# TODO

## Inbox - to be categorized/planned
- None


## Immediate

Milestones 006 and 007 complete. Next immediate focus is Milestone 008 include support.

- [ ] Resolve include paths relative to including file directory.
- [ ] Evaluate included files as prelude context.
- [ ] Keep included rows out of main rendered rows.
- [ ] Detect missing include files and cycles with visible warnings.

## Core Backlog

- [x] Define `EvalInput`, `EvalOutput`, `RenderedRow`, and `Diagnostic` model classes.
- [x] Implement lexer.
- [x] Implement parser.
- [x] Add Qt-free plain-text row rendering helpers.
- [x] Implement scalar numeric evaluator environment.
- [x] Implement scalar value model with unit dimensions.
- [x] Implement unit dimension model.
- [x] Implement formatter.
- [ ] Implement include resolver.
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
- [x] Include warning bar, basic output-warning display.
- [x] Metadata read/write.
- [ ] Value column placement.

## Documentation Backlog

- [ ] Expand `docs/user.md` with syntax examples once parser/evaluator exists.
- [x] Document Milestone 001 launch and architecture notes in user/dev docs.
- [ ] Add packaging notes after packaging approach is selected.

## Process Backlog

- [x] Keep `PLAN.md` milestone checkboxes current through Milestone 007.
- [x] Keep this TODO current through Milestone 007.
- [ ] Add prompt templates or skills when workflow gaps appear.
