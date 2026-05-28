# mathsheeet User Guide

`mathsheeet` is a free-form computational sheet for Linux desktop.

This repository is currently in working-prototype phase. The intended app has:

- a left plain-text source pane
- a right line-aligned rendered results pane
- immediate recalculation
- unit-aware arithmetic
- save/load, metadata, MRU, and include support

See `spec.md` for the authoritative product and language specification.

## Prototype Status

The prototype implementation has not been created yet. Current work starts with a Python/PySide6 desktop shell.

## Planned Launch Instructions

Once Milestone 001 is implemented, the expected development launch flow will be similar to:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m mathsheeet
```

These instructions will be updated when the project skeleton exists.

## Planned Sheet Syntax

The v1 language will support examples like:

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

Legacy display suffix syntax is intentionally not required.

## Planned Keyboard Shortcuts

- `Ctrl+O` open
- `Ctrl+S` save
- `Ctrl+Shift+S` save as
- `Ctrl+Z` undo
- `Ctrl+Y` / `Ctrl+Shift+Z` redo

## Known Prototype Limitations

- The app shell is not yet implemented.
- Parser/evaluator behavior is not yet implemented.
- Packaging is not yet selected.
