"""Prototype app configuration loaded from the project root.

This is intentionally separate from sheet metadata. It is a local UI tuning file
for prototype ergonomics and may be replaced by real preferences later.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.cwd() / "wmath_config.json"


@dataclass(frozen=True)
class AppConfig:
    fontFamily: str = "monospace"
    defaultFontPointSize: float = 11.0
    fontLetterSpacingPercent: float = 100.0
    editorFontScale: float = 1.0
    renderedFontScale: float = 1.0
    editorDocumentMargin: float = 3.0
    renderedRowHeightScale: float = 1.15
    renderedLayoutSpacing: int = 1
    plotDefaultHeight: int = 180
    plotMinHeight: int = 80
    plotMaxHeight: int = 1200
    plotOuterMargin: int = 6
    plotLeftGutter: int = 44
    plotTopGutter: int = 14
    plotRightGutter: int = 12
    plotBottomGutter: int = 30


def load_app_config(path: Path = CONFIG_PATH) -> AppConfig:
    """Load local prototype UI config, falling back to defaults on errors."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppConfig()
    if not isinstance(raw, dict):
        return AppConfig()
    return AppConfig(
        fontFamily=_str(raw, "fontFamily", AppConfig.fontFamily),
        defaultFontPointSize=_float(raw, "defaultFontPointSize", AppConfig.defaultFontPointSize, 6.0, 36.0),
        fontLetterSpacingPercent=_float(raw, "fontLetterSpacingPercent", 100.0, 50.0, 200.0),
        editorFontScale=_float(raw, "editorFontScale", 1.0, 0.5, 2.0),
        renderedFontScale=_float(raw, "renderedFontScale", 1.0, 0.5, 2.0),
        editorDocumentMargin=_float(raw, "editorDocumentMargin", 3.0, 0.0, 20.0),
        renderedRowHeightScale=_float(raw, "renderedRowHeightScale", 1.15, 0.8, 3.0),
        renderedLayoutSpacing=_int(raw, "renderedLayoutSpacing", 1, 0, 20),
        plotDefaultHeight=_int(raw, "plotDefaultHeight", 180, 40, 2400),
        plotMinHeight=_int(raw, "plotMinHeight", 80, 20, 2400),
        plotMaxHeight=_int(raw, "plotMaxHeight", 1200, 40, 4000),
        plotOuterMargin=_int(raw, "plotOuterMargin", 6, 0, 80),
        plotLeftGutter=_int(raw, "plotLeftGutter", 44, 0, 200),
        plotTopGutter=_int(raw, "plotTopGutter", 14, 0, 200),
        plotRightGutter=_int(raw, "plotRightGutter", 12, 0, 200),
        plotBottomGutter=_int(raw, "plotBottomGutter", 30, 0, 200),
    )


def _str(raw: dict[str, Any], key: str, default: str) -> str:
    value = raw.get(key)
    return value if isinstance(value, str) and value else default


def _float(raw: dict[str, Any], key: str, default: float, minimum: float, maximum: float) -> float:
    value = raw.get(key)
    if not isinstance(value, int | float):
        return default
    return float(max(minimum, min(maximum, value)))


def _int(raw: dict[str, Any], key: str, default: int, minimum: int, maximum: int) -> int:
    value = raw.get(key)
    if not isinstance(value, int):
        return default
    return max(minimum, min(maximum, value))
