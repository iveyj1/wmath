# wmath Development Notes

## Implementation Choice

The working prototype uses Python with PySide6. This favors quick iteration and direct desktop UI development while keeping the dependency set modest. Linux remains the primary development platform, but Windows support is now part of the prototype plan as an experimental source-run target before binary packaging is selected.

## Architectural Boundary

Keep the computational core independent from Qt.

Current layout:

```text
wmath/
  app/        # PySide6 application, windows, widgets, actions
  core/       # lexer, parser, evaluator, values/units; no Qt imports
  storage/    # file metadata, MRU, persistence helpers
  __main__.py # `python -m wmath` entry point
```

Milestone 001 uses `wmath.core.placeholder.evaluate_placeholder()` as a temporary render pipeline. It returns core `EvalOutput` data and has no Qt dependency.

Milestone 002 adds Qt-free persistence helpers in `wmath.storage`:

- `files.py` handles `.wmath` text files and `<sheet>.meta.json` sidecars.
- `mru.py` handles local-client MRU JSON state with platform-aware defaults: `XDG_STATE_HOME` or `~/.local/state` on Linux/Unix-like systems, and `%LOCALAPPDATA%` or `~/AppData/Local` on Windows. This stays Qt-free by using `os.name`, environment variables, and `pathlib`.

The PySide window owns file dialogs and user confirmations; storage helpers remain plain Python and testable without Qt.

Milestone 003 adds `wmath.core.render_text`, a Qt-free plain-text row/warning formatter used by the UI. Placeholder include rows now emit warning diagnostics so the warning bar and row diagnostic path can be exercised before real include evaluation exists.

Milestones 004 and 005 add Qt-free parser/evaluator modules:

- `lexer.py` tokenizes numbers, identifiers, strings, comments, operators, grouping, arrays, display separators, and indexing punctuation.
- `ast.py` defines parser AST dataclasses.
- `parser.py` parses statements and expressions with v1 precedence.
- `evaluator.py` evaluates scalar numeric rows top-to-bottom with assignment, user functions, selected scalar built-ins, display values, and row-local diagnostics.

Milestones 006 and 007 add `wmath.core.values` and expand `evaluator.py` beyond plain numbers:

- scalar values carry dimension tuples in `(m, kg, s, K)` order
- built-in units live in a small in-code registry
- scalar arithmetic checks dimensions
- display formatting handles default conventional units and explicit display units
- vector values support elementwise/scalar ops, indexing, slicing, `append`, `length`, and `dot`
- matrix literals validate rows and display, while arithmetic returns the required not-implemented diagnostic

Milestone 008 implements include evaluation in `evaluator.py`. Includes resolve relative to the including file, evaluate into the same environment as prelude context, do not render included rows in the parent output, and report missing/cycle cases as warnings.

Milestone 009 polishes the UI acceptance path: status text reports line count, evaluation state, and dirty/save state; dirty state compares current editor text to the last new/open/save baseline so undoing back to saved text clears the marker; warning text is word-wrapped and multi-line; rendered value placement uses sidecar `valueColumnPercent` against the current rendered pane width; the header exposes `showValuesMode` and `valueColumnPercent` controls; a New action creates an untitled sheet; rendered formulas omit display suffixes; and `spec.md` section 10 acceptance criteria have been reviewed against current behavior.

The core should expose a plain Python API:

```python
@dataclass
class EvalInput:
    source: str
    file_path: Path | None = None
    metadata: SheetMetadata | None = None

@dataclass
class EvalOutput:
    rows: list[RenderedRow]
    warnings: list[Warning]
```

The UI should consume `EvalOutput` and render rows without knowing parser internals. `wmath.app.main_window.MainWindow` currently follows this by calling the evaluator and rendering returned rows via core text-formatting helpers. The rendered pane is implemented as a selectable `QLabel` inside `QScrollArea`, not a second text editor, while still supporting basic proportional scroll sync. A Qt `QTextCursor::setPosition` warning can still appear from editor end-of-line/end-of-file interactions and is tracked as a prototype issue.

## Platform and Packaging Policy

Milestone 010 treats source/venv installs as the supported packaging path for now:

- Linux: venv/editable install is the primary developer/user path.
- Windows: venv/editable install is planned and should be smoke-tested before calling it supported.
- Future Linux binaries can evaluate AppImage or Flatpak.
- Future Windows binaries can evaluate PyInstaller; PySide6 Qt plugin collection must be tested on real Windows.
- `docs/windows-port.md` records the initial Windows feasibility review and porting checklist.

Cross-platform design notes:

- Keep `wmath.core` Qt-free and platform-neutral.
- Keep `wmath.storage` Qt-free; use `os.name`, environment variables, and `pathlib` for platform state paths instead of Qt `QStandardPaths`.
- Prefer forward-slash relative include paths in examples; `pathlib` should still handle native Windows paths when files are selected through dialogs.
- Current shortcuts are compatible with normal Windows conventions through Qt.
- The monospace font currently uses Qt's generic monospace fallback; Windows may choose Consolas or another installed font.

## Dependency Policy

Prefer standard library first. Expected prototype dependencies:

- PySide6 for desktop UI
- pytest for tests
- ruff for formatting/linting

Avoid adding runtime dependencies unless they materially simplify the prototype.

## Testing Policy

- Parser/evaluator/unit behavior should be covered by `pytest`.
- UI behavior can initially be smoke-tested manually.
- Core tests should not import Qt.
- Current core placeholder and text-rendering tests live in `tests/test_placeholder_core.py`.
- Parser/evaluator tests live in `tests/test_parser_evaluator.py`.
- Unit/vector/matrix tests live in `tests/test_units_vectors.py`.
- Include tests live in `tests/test_includes.py`.
- Storage tests live in `tests/test_storage.py`.

Useful local commands:

```bash
.pi/scripts/testlog run -- pytest -q
.pi/scripts/testlog run -- python -m compileall wmath tests
.pi/scripts/testlog run -- .venv/bin/python -m ruff check .
```

GitHub Actions runs the same checks on Ubuntu for pushes and pull requests.

If the active shell has the editable dev install loaded, `python -m ruff check .` is equivalent.

Test runs should go through `.pi/scripts/testlog` so results are appended to `.pi/test-runs.jsonl` with the command, pass/fail status, current `HEAD`, tracked diff hash, and untracked file hash. See `.pi/scripts/README.md` for the full script manual and template reuse notes. Before rerunning a command during a finish/checkpoint pass, check freshness with:

```bash
.pi/scripts/testlog status -- pytest -q
```

A `fresh pass` result means the same command already passed for the current source tree and can be reported without rerunning. `stale` or `missing` means rerun through `testlog run`.

## Documentation Policy

Update `docs/user.md` when behavior changes for users. Update this file when architecture, commands, testing, or packaging practices change.

## Development Workflow with pi

Recommended loop:

1. Use `/step <focus>` to continue from `PLAN.md` and `TODO.md`.
2. Let the agent implement as far as practical for the current milestone.
3. Review diff manually.
4. Run the app manually when UI changes are involved.
5. Commit a coherent checkpoint.

Use git commits as durable checkpoints. Pi session history is useful, but repository files are the source of truth.
