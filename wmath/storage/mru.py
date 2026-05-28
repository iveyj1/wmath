"""Most-recently-used file state."""

from __future__ import annotations

import json
import os
from pathlib import Path

MAX_MRU_ITEMS = 8


def default_mru_path() -> Path:
    """Return the default local-client MRU state path."""

    state_home = os.environ.get("XDG_STATE_HOME")
    base = Path(state_home).expanduser() if state_home else Path.home() / ".local" / "state"
    return base / "wmath" / "mru.json"


def load_mru(path: Path | None = None) -> list[Path]:
    """Load MRU paths, dropping malformed entries."""

    state_path = path or default_mru_path()
    if not state_path.exists():
        return []

    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(raw, list):
        return []

    items: list[Path] = []
    for item in raw:
        if isinstance(item, str) and item:
            candidate = Path(item).expanduser()
            if candidate not in items:
                items.append(candidate)
        if len(items) >= MAX_MRU_ITEMS:
            break
    return items


def save_mru(items: list[Path], path: Path | None = None) -> None:
    """Persist MRU paths."""

    state_path = path or default_mru_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    unique: list[str] = []
    for item in items:
        text = str(item.expanduser())
        if text not in unique:
            unique.append(text)
        if len(unique) >= MAX_MRU_ITEMS:
            break
    state_path.write_text(json.dumps(unique, indent=2) + "\n", encoding="utf-8")


def update_mru(items: list[Path], path: Path) -> list[Path]:
    """Return a new MRU list with path first."""

    expanded = path.expanduser().resolve()
    without = [item for item in items if item.expanduser().resolve() != expanded]
    return [expanded, *without][:MAX_MRU_ITEMS]
