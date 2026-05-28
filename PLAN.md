# wmath Prototype Plan

This plan guides the Python/PySide6 working prototype. `spec.md` remains authoritative.

## Current Strategy

Build a low-dependency Linux desktop prototype in Python using PySide6. Keep the math/evaluation core independent from Qt so the UI can be replaced later if needed.

## Milestones

### 001 — Project Skeleton and App Shell

Goal: create a runnable desktop shell with the intended layout but minimal behavior.

Acceptance criteria:

- [x] Python project structure exists.
- [x] App launches with PySide6 when dependencies are installed.
- [x] Header/status area is visible.
- [x] MRU bar placeholder is visible.
- [x] Split pane contains editable source text on the left.
- [x] Rendered rows pane exists on the right.
- [x] Basic keyboard shortcuts are wired or stubbed.
- [x] User docs explain how to launch the prototype.

### 002 — Storage Basics

Goal: plain text sheet persistence plus sidecar metadata scaffold.

Acceptance criteria:

- [x] Open `.wmath` file.
- [x] Save current file.
- [x] Save As.
- [x] Dirty state tracking.
- [x] Dirty-buffer confirmation before destructive open/MRU actions.
- [x] Sidecar `<sheet>.meta.json` read/write with required keys.
- [x] Local MRU state displayed in MRU bar.

### 003 — Core Data Model and Render Pipeline

Goal: connect source lines to rendered row objects, initially with placeholder evaluation.

Acceptance criteria:

- [x] Core API accepts source text and optional file path.
- [x] Core returns one rendered row per source row.
- [x] Diagnostics can be attached to individual rows.
- [x] UI updates rendered pane on edit.
- [x] Active editor line highlights corresponding rendered row.
- [x] Basic scroll sync exists or is explicitly documented as pending.

### 004 — Lexer and Parser

Goal: parse v1 baseline syntax without legacy syntax support.

Acceptance criteria:

- [x] Numbers, identifiers, operators, grouping, comments, continuations.
- [x] Assignment, function declaration, expression rows.
- [x] Display separator `|` and optional display unit expression.
- [x] Arrays, nested arrays, indexing, slicing.
- [x] Include directive parse support.
- [x] Parser tests cover valid and invalid syntax.

### 005 — Scalar Evaluation and Functions

Goal: top-to-bottom scalar evaluation with diagnostics.

Acceptance criteria:

- [x] Persistent environment across rows.
- [x] Arithmetic precedence follows `spec.md`.
- [x] Assignment and expression rows evaluate.
- [x] User-defined functions with lexical parameters.
- [x] Required scalar built-ins exist.
- [x] Failure in one row does not invalidate prior rows.

### 006 — Units and Display Formatting

Goal: dimension-aware scalar arithmetic and display conversion.

Acceptance criteria:

- [x] Base dimensions `(m, kg, s, K)`.
- [x] Built-in base and conventional units.
- [x] Add/subtract dimension checks.
- [x] Multiply/divide/power dimension handling.
- [x] `|` and `| unit` display syntax works.
- [x] Default display prefers conventional symbols where possible.

### 007 — Vectors and Matrix Groundwork

Goal: required vector behavior and matrix literal validation.

Acceptance criteria:

- [x] Homogeneous vector values.
- [x] Elementwise vector operations.
- [x] Scalar/vector operations.
- [x] 1-based indexing.
- [x] Inclusive slicing with defaults.
- [x] `append`, `length`, `dot`.
- [x] Matrix literals parse/evaluate.
- [x] Matrix arithmetic reports `matrix arithmetic is not implemented yet`.

### 008 — Include Support

Goal: evaluate included files as prelude context.

Acceptance criteria:

- [x] Include paths resolve relative to including file directory.
- [x] Included rows are not rendered into main sheet.
- [x] Missing include warnings visible in warning bar.
- [x] Include cycles detected and warned.

### 009 — UI Polish and Acceptance Sweep

Goal: satisfy v1 interaction acceptance criteria.

Acceptance criteria:

- [ ] Status indicator includes line count, evaluation status, dirty/save state.
- [ ] Include warning bar implemented.
- [ ] File action buttons and shortcuts implemented.
- [ ] Undo/redo behavior works via editor widget.
- [ ] Value column placement uses metadata setting.
- [ ] Acceptance criteria from `spec.md` section 10 reviewed.

### 010 — Prototype Packaging

Goal: make the prototype easy to run and share.

Acceptance criteria:

- [ ] README or docs describe install/run.
- [ ] Dependency list is minimal and pinned appropriately.
- [ ] Optional launcher script exists.
- [ ] Packaging approach selected: venv instructions, PyInstaller, AppImage, or Flatpak.

## Current Focus

Milestone 008 is implemented. Continue with Milestone 009: UI polish and acceptance sweep.
