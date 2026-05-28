# mathsheeet Development Notes

## Implementation Choice

The working prototype uses Python with PySide6. This favors quick iteration and direct desktop UI development while keeping the dependency set modest.

## Architectural Boundary

Keep the computational core independent from Qt.

Target layout:

```text
mathsheeet/
  app/        # PySide6 application, windows, widgets, actions
  core/       # parser/evaluator/unit system; no Qt imports
  storage/    # file metadata, MRU, persistence helpers
```

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

The UI should consume `EvalOutput` and render rows without knowing parser internals.

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
