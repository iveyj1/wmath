# TODO

## Inbox - to be categorized/planned
- [ ] Investigate harmless Qt `QTextCursor::setPosition` warning when editor cursor reaches line/file end.


## Immediate

Milestone 010 complete. Next immediate focus is not selected.

- [x] Add README or expand docs with Linux venv install/run summary.
- [x] Add Windows venv install/run summary.
- [x] Make MRU/state path platform-aware: XDG state on Linux, `%LOCALAPPDATA%` fallback on Windows, without adding Qt to storage.
- [x] Add tests for platform MRU/state path selection with mocked environment values.
- [x] Select packaging path: source/venv for now; defer binary packaging unless explicitly scoped.
- [x] Capture future binary packaging candidates: PyInstaller for Windows, AppImage/Flatpak for Linux.
- [x] Add optional launcher script if useful.
- [x] Review dependency pins and distribution notes for Linux and Windows source installs.
- [x] Smoke-test Windows source run on a real Windows system.
- [x] Add GitHub Actions CI for pytest, compileall, and ruff.

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

- [x] New file action.
- [x] Open file dialog.
- [x] Save.
- [x] Save As.
- [x] Dirty state tracking, including undo back to saved text.
- [x] Dirty replace confirmation.
- [x] MRU persistence.
- [x] Platform-aware MRU state location for Windows source-run support.
- [x] Editor/render scroll sync, proportional basic.
- [x] Active line highlight, basic marker in rendered pane.
- [x] Increase prototype UI font sizes for readability.
- [x] Suppress known harmless Qt AT-SPI startup warning.
- [x] Avoid rendered-pane cursor out-of-range warnings by rendering results in a selectable label rather than a second text editor.
- [x] Include warning bar, missing/cycle include warnings.
- [x] Metadata read/write.
- [x] Value column placement.
- [x] Display all values control.
- [x] Hide values when explicit `|` removed.
- [x] Omit `|` display suffix from rendered formulas.

## Documentation Backlog

- [x] Expand `docs/user.md` with current syntax examples.
- [x] Document Milestone 001 launch and architecture notes in user/dev docs.
- [x] Add Linux/Windows source-run notes for venv approach, using `python -m pip` to avoid stale generated pip script paths.
- [x] Add packaging notes after packaging approach is selected.

## Process Backlog

- [x] Keep `PLAN.md` milestone checkboxes current through Milestone 009.
- [x] Keep this TODO current through Milestone 009.
- [x] Add scripted test-run logging/freshness checks for pi prompts.
- [x] Add GitHub Actions CI for push/pull-request checks.
- [ ] Add prompt templates or skills when workflow gaps appear.
