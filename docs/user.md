# wmath User Guide

`wmath` is a free-form computational sheet for desktop use. Linux is the primary prototype target; Windows source-run support is planned and currently experimental.

This repository is currently in working-prototype phase. The intended app has:

- a left plain-text source pane
- a right line-aligned rendered results pane
- immediate recalculation
- unit-aware arithmetic
- save/load, metadata, MRU, and include support

See `spec.md` for the authoritative product and language specification.

## Prototype Status

Milestones 001 through 009 are implemented. The app currently provides a PySide6 desktop shell with:

- header/status row
- New, Open, Save, and Save As buttons
- MRU placeholder bar
- left source editor
- right rendered pane
- placeholder rendering that mirrors source lines
- basic editor-to-render scroll sync
- larger prototype UI fonts for readability
- basic active-line marker in the rendered pane
- basic warning bar for document-level warnings
- Open, Save, and Save As for `.wmath` text files
- dirty-state window/status markers
- dirty-buffer confirmation before Open or MRU replacement
- sidecar metadata read/write at `<sheet>.meta.json`
- local MRU buttons
- parser support for assignments, function declarations, expression rows, display `|`, arrays, indexing/slicing syntax, and include directives
- scalar numeric evaluation with persistent top-to-bottom environment
- user-defined scalar functions
- scalar built-ins: `sin`, `cos`, `tan`, `sqrt`, `log`, `exp`
- unit-aware scalar arithmetic over `m`, `kg`, `s`, `K`, `N`, `J`, `Pa`, `W`, `Hz`
- default conventional unit display and explicit `| unit` display
- vector literals, scalar/vector ops, elementwise vector ops, indexing, slicing
- vector helpers: `append`, `length`, `dot`
- matrix literal validation and display
- include evaluation as prelude context
- include missing-file and cycle warnings
- status indicator with line count, evaluation state, and dirty/save state
- value display mode control: explicit `|` only or all values
- value column position control using metadata `valueColumnPercent`

Include files are evaluated before following rows, but their rows are not rendered in the including sheet.

## Development Launch Instructions

Linux/macOS-style shell:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m wmath
```

Windows PowerShell (planned/experimental until smoke-tested on a real Windows system):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m wmath
```

Use `python -m pip` instead of bare `pip` to avoid stale generated script paths if a checkout or `.venv` directory has moved. If the virtual environment is badly stale, remove `.venv` and recreate it.

You can also launch through the installed script after installation:

```bash
wmath
```

## Current Sheet Syntax

The current prototype supports scalar, unit, vector, and matrix examples like:

```text
a = 2 |
b = 3 |
a + b |
double(x) = x * 2
double(4) |
sqrt(9) |
length = 2 m
force = 10 N
work = force * length | J
v = [1, 2, 3]
v[2] |
v[2:] |
dot(v, v) |
m = [[1, 2], [3, 4]] |
include "defs.wmath"
```

Rows display values only when `|` is present unless the `All values` checkbox is enabled. The rendered pane omits the `|` suffix and shows only formula text plus value.

## Planned Sheet Syntax

The v1 language will support unit-aware examples like:

```text
length = 2 m
width = 3 m
area = length * width |
force = 10 N
work = force * length | J
```

Display syntax uses `|`:

```text
area = length * width |
work = force * d | J
```

Legacy display suffix syntax is intentionally not required. Explicit display units such as `| J` convert/display compatible values. Incompatible display units produce row diagnostics.

## Includes

Include another file with:

```text
include "relative/path.wmath"
```

Paths resolve relative to the including file. Included definitions are available to later rows. Included rows are not rendered in the including sheet. Missing files and include cycles appear in the warning bar.

## Files and Metadata

Sheets are plain UTF-8 text files with the `.wmath` extension.

Saving also writes sidecar metadata next to the sheet:

```text
<sheet>.wmath.meta.json
```

Current metadata keys:

- `showValuesMode`: `explicit` or `all_assignments`
- `valueColumnPercent`: number clamped to 40..90. This controls approximate value placement as a percentage of the rendered pane width.

The header controls edit these metadata values:

- `All values`: toggles `showValuesMode` between explicit `|` display and showing all evaluated values.
- `Value %`: moves the value column position across the rendered pane width.

Recent files are stored as local client state under the platform state directory. Current Linux default:

```text
~/.local/state/wmath/mru.json
```

Windows default:

```text
%LOCALAPPDATA%\wmath\mru.json
```

If `%LOCALAPPDATA%` is unavailable, wmath falls back to:

```text
%USERPROFILE%\AppData\Local\wmath\mru.json
```

## Keyboard Shortcuts

Currently wired in the prototype:

- `Ctrl+N` new untitled sheet
- `Ctrl+O` open `.wmath` file
- `Ctrl+S` save current file, or Save As if untitled
- `Ctrl+Shift+S` save as
- `Ctrl+Z` undo in the source editor
- `Ctrl+Y` / `Ctrl+Shift+Z` redo in the source editor

## Manual Smoke Test

```bash
python -m wmath
```

Edit source lines and confirm the rendered pane updates. Move between lines and confirm the rendered pane marks the active source row with `▶`. Remove `|` from a row and confirm its value hides; enable `All values` and confirm values return. Change `Value %` and confirm the value column moves. Add a missing include such as `include "missing.wmath"` and confirm a warning appears in the warning bar and rendered row. Add an invalid row such as `missing + 1 |` and confirm status reports an error.

For storage behavior:

1. Create or edit text.
2. Use `Ctrl+Shift+S` and save as `example.wmath`.
3. Confirm `example.wmath` and `example.wmath.meta.json` are created.
4. Edit again and confirm the status/window title shows dirty state.
5. Use `Ctrl+S` and confirm dirty state clears. Edit, then undo back to saved text and confirm dirty state clears again.
6. Use `Ctrl+O` or an MRU button while dirty and confirm the discard prompt appears.

## Known Prototype Limitations

- User-defined unit registries are not implemented.
- Matrix arithmetic is not implemented; matrix operations report `matrix arithmetic is not implemented yet`.
- Source/venv install is the current packaging approach; binary packaging is deferred.
- Windows support is planned but not yet smoke-tested on a real Windows system.

## Troubleshooting

The app suppresses a known Qt AT-SPI accessibility warning that can appear on some Linux desktops and does not affect prototype behavior. A harmless `QTextCursor::setPosition` warning can still appear from Qt text editing at end-of-line/end-of-file interactions; this is a known prototype issue.
