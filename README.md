# wmath

`wmath` is a Python/PySide6 working prototype of a free-form computational sheet.

Linux is the primary development target. Windows source-run support is planned and experimental; the code is kept cross-platform where practical.

## Run from source

### Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m wmath
```

Use `python -m pip` instead of the bare `pip` script so installs still work if a checkout or virtual environment has moved and generated script shebangs are stale. If `.venv` is badly stale, remove it and recreate it.

After installation, the console entry point is also available:

```bash
wmath
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m wmath
```

Windows support still needs real-machine smoke testing before it is considered supported.

## Tests

```bash
.pi/scripts/testlog run -- pytest -q
.pi/scripts/testlog run -- python -m compileall wmath tests
.pi/scripts/testlog run -- .venv/bin/python -m ruff check .
```

## Packaging status

The current packaging path is source/venv installation. Binary packaging is deferred:

- Windows candidate: PyInstaller
- Linux candidates: AppImage or Flatpak

## Current limitations

- Matrix arithmetic is intentionally not implemented yet.
- User-defined unit registries are not implemented yet.
- Windows source-run support is planned but not yet smoke-tested.
