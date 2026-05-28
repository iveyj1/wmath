# wmath Development Notes

## Implementation Choice

The working prototype uses Python with PySide6. This favors quick iteration and direct desktop UI development while keeping the dependency set modest.

## Architectural Boundary

Keep the computational core independent from Qt.

Current layout:

```text
wmath/
  app/        # PySide6 application, windows, widgets, actions
  core/       # parser/evaluator/unit system; no Qt imports
  storage/    # file metadata, MRU, persistence helpers
  __main__.py # `python -m wmath` entry point
```

Milestone 001 uses `wmath.core.placeholder.evaluate_placeholder()` as a temporary render pipeline. It returns core `EvalOutput` data and has no Qt dependency.

Milestone 002 adds Qt-free persistence helpers in `wmath.storage`:

- `files.py` handles `.wmath` text files and `<sheet>.meta.json` sidecars.
- `mru.py` handles local-client MRU JSON state, defaulting to `~/.local/state/wmath/mru.json` unless `XDG_STATE_HOME` is set.

The PySide window owns file dialogs and user confirmations; storage helpers remain plain Python and testable without Qt.

Milestone 003 adds `wmath.core.render_text`, a Qt-free plain-text row/warning formatter used by the UI. Placeholder include rows now emit warning diagnostics so the warning bar and row diagnostic path can be exercised before real include evaluation exists.

Milestones 004 and 005 add Qt-free parser/evaluator modules:

- `lexer.py` tokenizes numbers, identifiers, strings, comments, operators, grouping, arrays, display separators, and indexing punctuation.
- `ast.py` defines parser AST dataclasses.
- `parser.py` parses statements and expressions with v1 precedence.
- `evaluator.py` evaluates scalar numeric rows top-to-bottom with assignment, user functions, selected scalar built-ins, display values, and row-local diagnostics.

The evaluator is intentionally scalar-only at this stage. Units, vectors, matrices, and include evaluation remain later milestones.

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

The UI should consume `EvalOutput` and render rows without knowing parser internals. `wmath.app.main_window.MainWindow` currently follows this by calling the placeholder evaluator and rendering returned rows via core text-formatting helpers. The rendered pane is implemented as a selectable `QLabel` inside `QScrollArea`, not a second text editor, to avoid QTextCursor warnings while still supporting basic proportional scroll sync.

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
- Storage tests live in `tests/test_storage.py`.

Useful commands:

```bash
pytest -q
python -m compileall wmath tests
.venv/bin/python -m ruff check .
```

If the active shell has the editable dev install loaded, `python -m ruff check .` is equivalent.

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
