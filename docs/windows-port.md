 Porting this prototype to Windows looks very feasible, but it should be treated as a small platform-support pass rather
 than a rewrite.

 Overall feasibility

 The current implementation is already close to cross-platform:

 - UI is PySide6/Qt, which supports Windows well.
 - Core parser/evaluator is Qt-free pure Python.
 - Storage uses pathlib, UTF-8 text, and JSON sidecars.
 - File dialogs, shortcuts, widgets, and split panes are all standard Qt APIs.
 - Packaging is not selected yet, so Windows can still be included cleanly in Milestone 010.

 The main blocker is not architecture; it is that the product/docs currently define the target as “Linux desktop,” and a
 couple of implementation details assume Linux conventions.

 Likely Windows-specific changes

 ### 1. MRU/state location

 Current MRU path defaults to:

 ```text
   ~/.local/state/wmath/mru.json
 ```

 from wmath/storage/mru.py.

 That is Linux/XDG-specific. On Windows it should probably use one of:

 ```text
   %LOCALAPPDATA%\wmath\mru.json
 ```

 or Qt’s QStandardPaths.AppLocalDataLocation.

 Since storage is intentionally Qt-free, a good low-dependency option is:

 ```python
   if os.name == "nt":
       base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
   else:
       base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
 ```

 ### 2. Packaging

 For Windows, the practical path is probably PyInstaller:

 ```bash
   pyinstaller --windowed --name wmath ...
 ```

 PySide6 apps are commonly packaged this way, though Qt plugin collection needs testing.

 Possible packaging matrix:

 - Linux dev: venv / editable install
 - Linux distributable: AppImage or Flatpak later
 - Windows distributable: PyInstaller .exe or one-folder bundle

 ### 3. Docs/spec positioning

 spec.md and docs/user.md currently say Linux desktop. If Windows becomes a supported target, docs should be changed to
 say something like:

 │ Primary prototype target: Linux. Windows support is experimental.

 or:

 │ Desktop app for Linux and Windows.

 depending on how strong you want the commitment to be.

 ### 4. Shortcut behavior

 Most current shortcuts map cleanly:

 - Ctrl+N
 - Ctrl+O
 - Ctrl+S
 - Ctrl+Shift+S
 - Ctrl+Z
 - Ctrl+Y

 These are normal Windows conventions. Qt should handle them fine.

 ### 5. Fonts/UI sizing

 The app uses:

 ```python
   QFont("monospace")
   font.setStyleHint(QFont.StyleHint.Monospace)
 ```

 This should work, but Windows may choose a different fallback. It may be worth explicitly preferring Consolas on Windows
 if readability matters.

 ### 6. Include paths

 Includes resolve relative to the current file using pathlib, so this should mostly work. Windows backslash paths inside
 quoted include strings may deserve tests, but users can likely use forward slashes:

 ```text
   include "defs/common.wmath"
 ```

 which Windows accepts.

 ### 7. Qt warning suppression

 wmath/app/main.py suppresses a Linux AT-SPI Qt warning:

 ```python
   qt.accessibility.atspi.warning=false
 ```

 This is harmless on Windows, but it is Linux-specific noise. It does not block portability.

 Risk areas

 The highest-risk areas are not core math behavior; they are distribution/runtime details:

 1. PyInstaller + PySide6 plugin bundling.
 2. Windows app state location.
 3. Manual UI smoke testing on real Windows.
 4. Ensuring file dialogs, MRU paths, metadata sidecars, and include resolution behave with drive letters and spaces.

 Suggested porting plan

 1. Add platform-aware MRU path handling.
 2. Add tests for default MRU path behavior with mocked environment values.
 3. Add Windows notes to docs/user.md / docs/dev.md.
 4. Try source launch on Windows:

    ```powershell
      py -m venv .venv
      .\.venv\Scripts\Activate.ps1
      pip install -e .[dev]
      python -m wmath
    ```
 5. Package with PyInstaller.
 6. Smoke test save/load/MRU/includes on Windows.
 7. Decide whether Windows is “experimental” or officially supported.
