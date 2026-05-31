"""Plain-text sheet and sidecar metadata persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

ShowValuesMode = Literal["explicit", "all_assignments"]


@dataclass(frozen=True)
class SheetMetadata:
    """User-visible sheet metadata stored next to a `.wmath` file."""

    showValuesMode: ShowValuesMode = "explicit"
    valueColumnPercent: float = 60.0
    significantFigures: int = 12
    scientificMagnitude: int = 12
    fontPointSize: float = 0.0


def metadata_path(sheet_path: Path) -> Path:
    """Return sidecar metadata path for a sheet path."""

    return sheet_path.with_name(f"{sheet_path.name}.meta.json")


def read_sheet(path: Path) -> str:
    """Read a sheet as UTF-8 text."""

    return path.read_text(encoding="utf-8")


def write_sheet(path: Path, source: str) -> None:
    """Write a sheet as UTF-8 text, creating parent directories as needed."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def load_metadata(sheet_path: Path) -> SheetMetadata:
    """Load sidecar metadata, using defaults for missing or invalid data."""

    path = metadata_path(sheet_path)
    if not path.exists():
        return SheetMetadata()

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return SheetMetadata()

    if not isinstance(raw, dict):
        return SheetMetadata()
    return _metadata_from_dict(raw)


def save_metadata(sheet_path: Path, metadata: SheetMetadata) -> None:
    """Write sidecar metadata next to a sheet."""

    path = metadata_path(sheet_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=2) + "\n", encoding="utf-8")


def _metadata_from_dict(raw: dict[str, Any]) -> SheetMetadata:
    mode = raw.get("showValuesMode")
    if mode not in ("explicit", "all_assignments"):
        mode = "explicit"

    value_column = raw.get("valueColumnPercent")
    if not isinstance(value_column, int | float):
        value_column = 60.0
    value_column = float(max(40.0, min(90.0, value_column)))

    significant = raw.get("significantFigures")
    if not isinstance(significant, int):
        significant = 12
    significant = max(3, min(15, significant))

    scientific = raw.get("scientificMagnitude")
    if not isinstance(scientific, int):
        scientific = 12
    scientific = max(3, min(12, scientific))

    font_size = raw.get("fontPointSize")
    if not isinstance(font_size, int | float):
        font_size = 0.0
    font_size = float(max(0.0, min(36.0, font_size)))

    return SheetMetadata(
        showValuesMode=mode,
        valueColumnPercent=value_column,
        significantFigures=significant,
        scientificMagnitude=scientific,
        fontPointSize=font_size,
    )
