# wmath Specification (Implementation Baseline v0.2)

This document is the authoritative baseline for reimplementing the app from scratch.
It reflects current intended behavior and intentionally drops legacy syntax support.

## 1. Product Vision

`wmath` is a free-form computational sheet for desktop use. The current prototype targets Linux first, with Windows support planned as an experimental/source-run target before packaging is finalized.

- Left pane: plain-text source.
- Right pane: line-aligned rendered formulas, values, units, and diagnostics.
- Primary goals: minimal syntax, immediate feedback, first-class units, and notebook-like flow.

## 2. Scope

### In Scope (v1 baseline)

- Desktop app, Linux first with Windows support planned/experimental.
- Split synchronized view (entry + rendered).
- Top-to-bottom row evaluation with persistent environment.
- Scalars, vectors, and matrix literals (matrix arithmetic explicitly deferred).
- User-defined functions and selected built-in functions.
- Unit-aware arithmetic over base dimensions `(m, kg, s, K)`.
- Save/load, MRU display, include support, undo/redo.

### Out of Scope (v1)

- Collaborative editing/cloud sync.
- Full symbolic algebra/CAS.
- Full matrix algebra.
- User-defined unit registry from YAML (tracked backlog item 99).

## 3. UI and Interaction Requirements

## 3.1 Layout

- Header bar with filename, status, and file actions.
- MRU bar below header with clickable recent files.
- Two vertical panes below MRU bar:
  - Left: editable text.
  - Right: rendered rows aligned to source row numbers.
- Scroll sync from editor to rendered pane.
- Active cursor line highlight in rendered pane.

## 3.2 Status and Warnings

- Status indicator includes: line count, evaluation status, save/dirty state.
- Include-file warnings are shown in a dedicated warning bar above entry editor.

## 3.3 File Actions

- New, Open, Save, Save As buttons.
- Keyboard shortcuts:
  - `Ctrl+N` new
  - `Ctrl+O` open
  - `Ctrl+S` save
  - `Ctrl+Shift+S` save as
  - `Ctrl+Z` undo
  - `Ctrl+Y` / `Ctrl+Shift+Z` redo
- Dirty-buffer confirmation shown before replacing source via new/open/MRU.

## 4. Language Specification

## 4.1 Lexical Elements

- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`
- Numbers: decimal/scientific (`1`, `1.5`, `2e-3`)
- Operators: `+ - * / ^`
- Assignment: `=`
- Grouping: `(` `)`
- Collection/indexing: `[` `]` `,` `:`
- Display separator: `|`
- Comments:
  - `#` line comment
  - `/* ... */` block comment (may span lines)
- Line continuation: trailing `\` joins with next line before parse.

## 4.2 Statements

- Assignment: `name = expression`
- Function declaration: `f(x, y) = expression`
- Expression-only row: `expression`
- Include directive: `include "relative/path.wmath"`

Include directive semantics:

- Include rows are not rendered as formulas.
- Included source is evaluated as prelude context.
- Include path is resolved relative to including file directory.
- Include cycles are detected and warned.

## 4.3 Display Value Syntax (Required)

Legacy `=` display suffix is not required.

- Show value: append `|`
  - Example: `area = length * width |`
- Show value in requested unit: append `| <unit expression>`
  - Example: `work = force * d | J`

Rules:

- In explicit display mode, rows without `|` do not show values.
- `showValuesMode = all_assignments` shows evaluated values even without `|`.
- The rendered formula omits the display suffix; `|` controls value display but is not shown in the rendered pane.
- If a display unit expression is dimensionally compatible, value is converted.
- If incompatible, row gets a diagnostic.

## 4.4 Expressions and Precedence

- Literals: numbers
- Names: variables, units, functions
- Function call: `f(a, b)`
- Arrays/vectors: `[1, 2, 3]`
- Matrix literal (groundwork): `[[1,2],[3,4]]`
- Indexing: `v[1]` (1-based)
- Slicing: `v[2:4]` (inclusive end)

Precedence:

1. postfix indexing/slicing/call
2. `^`
3. unary `+ -`
4. `* /`
5. `+ -`

## 5. Types and Evaluation Semantics

## 5.1 Value Types

- Scalar: `f64` + dimension vector.
- Vector: ordered homogeneous list of scalar values.
- Matrix literal type: row list of homogeneous vectors.

## 5.2 Row Evaluation Model

- Evaluate rows top-to-bottom.
- Environment accumulates variables/functions.
- Failure in one row does not invalidate prior rows.
- Diagnostics are row-local and include line context.

## 5.3 Functions

User-defined:

- `f(x, y) = expression`
- Lexically scoped parameters.

Built-ins required:

- Scalar math: `sin`, `cos`, `tan`, `sqrt`, `log`, `exp`
- Vector helpers: `append(v1, v2)`, `length(v)`, `dot(v1, v2)`

Built-in constraints:

- `sin/cos/tan/log/exp`: dimensionless scalar input.
- `sqrt`: scalar, non-negative value, even unit exponents.
- `dot`: vectors only, same length, term units must be compatible for sum.

## 5.4 Vector Operations (Required)

- Scalar-vector and vector-scalar `+ - * /`.
- Vector-vector elementwise `+ - * /` with same-length requirement.
- Indexing `v[i]`:
  - `i` must be dimensionless integer >= 1.
  - out-of-bounds is error.
- Slicing `v[a:b]` inclusive:
  - defaults: `[:b]` starts at 1, `[a:]` ends at length.
  - bounds errors are reported.

## 5.5 Matrix Groundwork (Required)

- Parse/evaluate nested array literals as matrix values.
- Validate consistent row widths and compatible element units.
- Any matrix arithmetic operation returns explicit diagnostic:
  - `matrix arithmetic is not implemented yet`

## 6. Units and Dimensional Analysis

## 6.1 Base Dimensions

- Canonical basis: `(m, kg, s, K)`.
- Internal representation: exponent tuple per basis dimension.

## 6.2 Built-in Units

- Base: `m`, `kg`, `s`, `K`
- Conventional at minimum: `N`, `J`, `Pa`, `W`, `Hz`

## 6.3 Unit Rules

- Add/subtract require identical dimensions.
- Multiply/divide combine exponents.
- Power:
  - exponent must be dimensionless.
  - non-integer exponent requires dimensionless base.

## 6.4 Display Unit Resolution

- Default display prefers conventional symbol when exact match.
- Otherwise display factored base-unit form.
- Explicit `| unit_expr` overrides default display unit.

## 7. Persistence

## 7.1 Sheet Files

- Main source file: plain text `.wmath`.
- Sidecar metadata file: `<sheet>.meta.json`.

Metadata keys required:

- `showValuesMode`: `explicit | all_assignments`
- `valueColumnPercent`: number (40..90)

## 7.2 MRU

- MRU list is local-client state.
- MRU storage should use platform-appropriate state locations: XDG state on Linux and local app data on Windows.
- Display in MRU bar with clickable entries.

## 8. Rendering Rules

- One rendered row per source row (except include directives render blank/no formula state).
- Render row may contain:
  - normalized formula text without display suffix
  - optional value/unit
  - optional diagnostics
- Value column placement driven by `valueColumnPercent`.

## 9. Non-Functional Requirements

- Startup target: < 1 second typical desktop in source/venv development mode.
- Recalc target: about 100 formulas in about 500 ms.
- Deterministic evaluation and formatting.
- Offline operation.

## 10. Reimplementation Acceptance Criteria

A clean-room implementation is acceptable if all are true:

1. `|` and `| unit` display syntax works and legacy display syntax is not required.
2. Includes evaluate definitions without rendering include file lines.
3. Include missing/cycle cases produce visible warnings.
4. Vectors support elementwise ops, indexing, slicing, append, length, dot.
5. Matrix literals parse/evaluate; matrix arithmetic reports not implemented.
6. Unit checking and conversions follow dimension rules above.
7. Save/load + metadata + dirty prompts + MRU + shortcuts behave as specified.

## 11. Technology Guidance

Preferred stack remains:

- Tauri v2
- React + TypeScript + Vite
- CodeMirror 6 editor
- Rust evaluation core

Equivalent stack is acceptable if all functional and non-functional requirements are met.
