# wmath User Guide

`wmath` is a free-form computational sheet for desktop use. Linux is the primary prototype target; Windows source-run support has been smoke-tested.

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
- basic two-way editor/render scroll sync
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
- unit-aware scalar arithmetic over SI base units `m`, `kg`, `s`, `A`, `K`, `mol`, `cd`, plus the 22 named SI derived units
- default conventional unit display and explicit `| unit` display
- vector literals, scalar/vector ops, elementwise vector ops, indexing, slicing
- vector helpers: `append`, `length`, `dot`
- CSV column import via `csv(path, selector)`
- textual plot artifacts via `plot(x, y, min_x, max_x, min_y, max_y)`
- matrix literal validation and display
- include evaluation as prelude context
- include missing-file and cycle warnings
- status indicator with line count, evaluation state, and dirty/save state
- value display mode control: explicit `|` only or all values
- value column position control using metadata `valueColumnPercent`
- rendered number formatting controls for significant figures and scientific notation transition
- font-size control for editor and rendered pane

Include files are evaluated before following rows, but their rows are not rendered in the including sheet.

## Prototype UI Tuning

For now, local prototype spacing/font tuning is read from `wmath_config.json` in the current working directory. It controls font family, letter spacing, editor/rendered font scaling, row height, layout spacing, and plot margins. Restart the app after editing it.

Sheet-specific metadata still controls visible header settings such as `Font`, `Sig`, `Sci`, `Value %`, and `All values`.

## Development Launch Instructions

Linux/macOS-style shell:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m wmath
```

Windows PowerShell:

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
current = 2 A
amount = 3 mol
brightness = 4 cd
force = 10 N
work = force * length | J
charge = 2 A * s |
resistance = 10 V / A |
angle = 2 | rad
ft = 0.3048 m
distance = 20 m | ft
# t = csv("run.csv", "time") * s
# d = csv("run.csv", "distance") * m
v = [1, 2, 3]
v[2] |
v[2:] |
dot(v, v) |
plot(v, [1, 4, 9], 1, 3, 0, 10) |
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

Built-in SI named derived units are available as unit names: `rad`, `sr`, `Hz`, `N`, `Pa`, `J`, `W`, `C`, `V`, `F`, `ohm`, `S`, `Wb`, `T`, `H`, `degC`, `lm`, `lx`, `Bq`, `Gy`, `Sv`, and `kat`. ASCII identifiers are used for `ohm` and `degC` because `Ω` and `°C` are not valid identifiers in the current language. Some SI named units share dimensions, such as `Hz`/`Bq`, `Gy`/`Sv`, `cd`/`lm`, and dimensionless `rad`/`sr`; use explicit display syntax such as `| Sv` or `| rad` when you need the non-default label.

Unit-like variables can also be defined directly in sheets or includes and used as explicit display units:

```text
ft = 0.3048 m
inch = ft / 12
mi = 5280 ft
distance = 20 m | ft
```

The value is converted using the variable definition, and the requested display label is preserved. For example, `distance = 20 m | ft` renders in `ft`, not the default built-in `m` label. Display unit expressions are deliberately limited to unit-name arithmetic with names, `*`, `/`, and integer powers. Arbitrary calculations such as `| 2 ft` are rejected.

## CSV Import

CSV vector import reads one numeric CSV column as a dimensionless vector:

```text
t = csv("run.csv", "time") * s
d = csv("run.csv", "distance") * m
plot(t, d, [0 s, 10 s], [0 m, 100 m]) |
```

String selectors use the first CSV row as headers and skip that row. Numeric selectors are 1-based column indexes and treat every row as data:

```text
x = csv("headerless.csv", 1)
y = csv("headerless.csv", 2)
```

CSV values import as dimensionless numbers; attach units with normal multiplication. Relative paths resolve relative to the current sheet file, or the current working directory for untitled sheets. Completely blank CSV rows are ignored. Missing files, missing columns, empty cells, and nonnumeric selected cells produce row diagnostics.

## Plotting

Basic plot artifacts are implemented with:

```text
x = [0, 1, 2, 3, 4]
y = [0, 1, 4, 9, 16]
plot(x, y, 0, 4, 0, 16) |
```

Enhanced forms group ranges and allow optional size:

```text
plot(x, y, [0, 4], [0, 16]) |
plot(x, y, [0, 4], [0, 16], [500, 240]) |
```

For unit-bearing vectors, axis bounds should use compatible units:

```text
t = [0, 1, 2, 3] s
d = [0, 4.9, 19.6, 44.1] m
plot(t, d, 0 s, 3 s, 0 m, 50 m) |
```

The rendered pane shows a textual summary and a simple drawn plot with axes, point markers, a connected line, and min/max labels. The textual summary looks like:

```text
plot: 5 points, x 0..4, y 0..16
```

`| unit` display suffixes are not supported directly on plot rows yet; put compatible units on vector data and axis bounds instead. Optional plot size uses `[width, height]`; the current UI honors requested height when practical and treats requested width as a maximum so plots stay within the rendered pane.

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
- `significantFigures`: integer clamped to 3..15. This controls rendered numeric precision.
- `scientificMagnitude`: integer clamped to 3..12. Numbers with magnitude outside `10^±scientificMagnitude` render in scientific notation.
- `fontPointSize`: number clamped to 0..36. `0` uses the platform default; positive values set the rendered font size.

The header controls edit these metadata values:

- `All values`: toggles `showValuesMode` between explicit `|` display and showing all evaluated values.
- `Value %`: moves the value column position across the rendered pane width.
- `Sig`: controls significant figures for rendered numbers.
- `Sci`: controls when rendered numbers switch to scientific notation.
- `Font`: controls editor and rendered pane font size.

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

Edit source lines and confirm the rendered pane updates. Move between lines and confirm the rendered pane marks the active source row with `▶`. Scroll either pane and confirm the other pane follows proportionally. Add `plot([0, 1, 2], [0, 1, 4], 0, 2, 0, 4) |` and confirm a simple plot appears. Remove `|` from a row and confirm its value hides; enable `All values` and confirm values return. Change `Value %` and confirm the value column moves. Add a missing include such as `include "missing.wmath"` and confirm a warning appears in the warning bar and rendered row. Add an invalid row such as `missing + 1 |` and confirm status reports an error.

For storage behavior:

1. Create or edit text.
2. Use `Ctrl+Shift+S` and save as `example.wmath`.
3. Confirm `example.wmath` and `example.wmath.meta.json` are created.
4. Edit again and confirm the status/window title shows dirty state.
5. Use `Ctrl+S` and confirm dirty state clears. Edit, then undo back to saved text and confirm dirty state clears again.
6. Close the window while dirty and confirm Save / Discard / Cancel choices work.
7. Use `Ctrl+O` or an MRU button while dirty and confirm the discard prompt appears.

## Known Prototype Limitations

- User-defined unit registries are not implemented.
- CSV import rereads files on recalculation; caching is not implemented yet.
- Plotting is basic: drawn plots have fixed styling and no zoom/pan/hover interaction yet.
- Matrix arithmetic is not implemented; matrix operations report `matrix arithmetic is not implemented yet`.
- Source/venv install is the current packaging approach; binary packaging is deferred.
- Windows source-run support has been smoke-tested; binary packaging is still deferred.

## Troubleshooting

The app suppresses a known Qt AT-SPI accessibility warning that can appear on some Linux desktops and does not affect prototype behavior. A harmless `QTextCursor::setPosition` warning can still appear from Qt text editing at end-of-line/end-of-file interactions; this is a known prototype issue.
