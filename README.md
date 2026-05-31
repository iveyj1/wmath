# wmath

`wmath` is a Python/PySide6 working prototype of a free-form computational sheet.

Linux is the primary development target. Windows source-run support has been smoke-tested and is kept viable, while binary packaging remains deferred.

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

Windows source-run support has been smoke-tested with the venv instructions above.

## Units

The seven SI base units and 22 named SI derived units are built in. Use ASCII names `ohm` and `degC` for `Ω` and `°C`.

## Custom display units

Unit-like variables can be defined in sheets or includes and used after `|`:

```text
ft = 0.3048 m
distance = 20 m | ft
```

The value is converted and rendered with the requested label, e.g. `65.6167979003 ft`.

## CSV import

CSV import reads numeric columns as vectors:

```text
t = csv("run.csv", "time") * s
d = csv("run.csv", "distance") * m
plot(t, d, [0 s, 10 s], [0 m, 100 m]) |
```

CSV values import as dimensionless vectors; attach units in sheet expressions.

## Plotting

Vector plotting uses:

```text
plot(x, y, min_x, max_x, min_y, max_y) |
```

The current implementation produces core plot artifacts, textual summaries, and simple Qt-rendered plot widgets in the desktop UI. Grouped ranges and optional size are supported, e.g. `plot(x, y, [0, 4], [0, 16], [500, 240]) |`.

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
- Binary packaging is deferred; use source/venv installs for now.
