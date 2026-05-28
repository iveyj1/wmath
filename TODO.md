# TODO

## Inbox - to be categorized/planned
- None


## Immediate

Milestone 003 complete. Next immediate focus is Milestone 004 lexer and parser.

- [ ] Implement token model and lexer for v1 lexical elements.
- [ ] Implement parser AST model.
- [ ] Parse assignments, function declarations, expression rows, display suffixes, arrays, indexing, slicing, and includes.
- [ ] Add parser diagnostics and pytest coverage.

## Core Backlog

- [x] Define `EvalInput`, `EvalOutput`, `RenderedRow`, and `Diagnostic` model classes.
- [ ] Implement lexer.
- [ ] Implement parser.
- [x] Add Qt-free plain-text row rendering helpers.
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

- [x] Keep `PLAN.md` milestone checkboxes current through Milestone 003.
- [x] Keep this TODO current through Milestone 003.
- [ ] Add prompt templates or skills when workflow gaps appear.
