# wmath Prototype Plan

This plan guides the Python/PySide6 working prototype. `spec.md` remains authoritative.

## Current Strategy

Build a low-dependency desktop prototype in Python using PySide6. Linux remains the primary development target; Windows source-run support has been smoke-tested and should be kept viable. Keep the math/evaluation core independent from Qt so the UI can be replaced later if needed.

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
- [x] Dirty state tracking, including clean state when undo returns to saved text.
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
- [x] Basic two-way scroll sync exists.

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

- [x] SI base dimensions `(m, kg, s, A, K, mol, cd)`.
- [x] Built-in SI base units and 22 named SI derived units.
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

- [x] Status indicator includes line count, evaluation status, dirty/save state.
- [x] Save/discard/cancel prompt appears on exit when dirty.
- [x] Include warning bar implemented.
- [x] File action buttons and shortcuts implemented, including New.
- [x] Undo/redo behavior works via editor widget and dirty state follows saved text.
- [x] Value column placement, display mode, number formatting, and font size use metadata settings.
- [x] Acceptance criteria from `spec.md` section 10 reviewed.

### 010 — Cross-Platform Source Run and Packaging Readiness

Goal: make the prototype easy to run from source on Linux and Windows, and keep later binary packaging decisions clean.

Acceptance criteria:

- [x] README or docs describe Linux venv install/run with `python -m pip`.
- [x] README or docs describe Windows venv install/run with `python -m pip`.
- [x] MRU/state path selection is platform-aware and remains Qt-free.
- [x] Dependency list is minimal and reviewed for Linux/Windows source installs.
- [x] Optional launcher script exists if useful and does not obscure Windows instructions.
- [x] Packaging approach selected: source/venv for now; PyInstaller/AppImage/Flatpak deferred or scoped explicitly.

### 011 — User-Defined Display Units via Sheets

Goal: allow ordinary sheet variables and includes to serve as custom display units.

Acceptance criteria:

- [x] A variable such as `ft = 0.3048 m` can be used in `d = 20 m | ft`.
- [x] Explicit display labels preserve the requested unit text instead of reverting to built-in preferred unit symbols.
- [x] Compound display unit labels such as `ft/s` are preserved.
- [x] Arbitrary display-unit calculations such as `| 2 ft` are rejected for now.
- [x] Included files can define display-unit variables.

### 012 — Plot Built-in and Textual Render Artifact

Goal: introduce graphing semantics without adding UI drawing complexity or Qt dependencies to the core.

Acceptance criteria:

- [x] Core model can represent a plot artifact separately from plain value text.
- [x] `plot(x, y, min_x, max_x, min_y, max_y)` validates vector lengths, scalar bounds, axis dimensions, and increasing ranges.
- [x] Plot evaluation produces deterministic structured points and axis metadata.
- [x] Initial rendered output is textual or ASCII and testable headlessly.
- [x] Unit-bearing axes are supported when bounds match vector dimensions.
- [x] Diagnostics cover wrong argument count/type, vector length mismatch, too few points, incompatible bounds, and non-increasing bounds.
- [x] Docs include examples for plain and unit-bearing plots.

### 013 — Qt Plot Rendering

Goal: render plot artifacts visually in the right pane after core plot semantics are stable.

Acceptance criteria:

- [x] Rendered pane can display mixed row content: text rows and plot rows/widgets.
- [x] A minimal Qt plot widget draws axes, line/points, and min/max labels.
- [x] Two-way scroll synchronization and active-row indication remain usable with plot rows.
- [x] No heavy plotting dependency such as matplotlib is required.

### 014 — Plot Range and Size Arguments

Goal: make plot declarations easier to read and give users basic control over plot size.

Acceptance criteria:

- [x] Existing six-argument form remains supported: `plot(x, y, min_x, max_x, min_y, max_y)`.
- [x] Range-vector form is supported: `plot(x, y, [min_x, max_x], [min_y, max_y])`.
- [x] Optional size-vector form is supported: `plot(x, y, [min_x, max_x], [min_y, max_y], [width, height])`.
- [x] Range vectors must contain exactly two scalar values with dimensions compatible with the relevant axis.
- [x] Size vector must contain exactly two dimensionless scalar values.
- [x] Core `PlotArtifact` records requested size without depending on Qt.
- [x] Qt plot widget honors requested height when practical and treats requested width as a maximum within the rendered pane.
- [x] Diagnostics cover malformed ranges, malformed size, incompatible bounds, and non-increasing bounds.
- [x] Docs and manual test sheet include enhanced plot examples.

### 015 — CSV Vector Import

Goal: import numeric CSV columns as vectors for plotting and data-analysis workflows.

Acceptance criteria:

- [x] String literals parse as expression values.
- [x] `csv(path, selector)` built-in exists.
- [x] `path` is a string value and resolves relative to the current sheet file, or current working directory for untitled sheets.
- [x] String selector uses the first row as headers, selects by exact header text, and skips the header row.
- [x] Numeric selector is a dimensionless 1-based integer column index and treats all rows as data.
- [x] Imported values are dimensionless scalar vectors, so units can be attached with existing vector-scalar multiplication.
- [x] Completely blank rows are ignored.
- [x] Diagnostics cover missing files, missing columns, malformed selectors, empty selected cells, and nonnumeric selected cells.
- [x] Tests cover header selection, index selection, relative path resolution, unit attachment, and bad data.
- [x] Docs and manual examples include CSV-to-plot workflow.

## Current Focus

Milestone 015 is implemented. Next implementation focus should be selected from remaining backlog.
