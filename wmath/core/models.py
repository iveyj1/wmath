"""Core data models shared by evaluators and UI renderers.

This module intentionally has no Qt imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

Dimension = tuple[int, int, int, int, int, int, int]

DiagnosticSeverity = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class Diagnostic:
    """A row-local diagnostic message."""

    message: str
    severity: DiagnosticSeverity = "error"


@dataclass(frozen=True)
class PlotArtifact:
    """Qt-free plot data produced by core evaluation."""

    points: tuple[tuple[float, float], ...]
    x_range: tuple[float, float]
    y_range: tuple[float, float]
    x_dimension: Dimension
    y_dimension: Dimension
    requested_size: tuple[int, int] | None = None


RenderArtifact = PlotArtifact


@dataclass(frozen=True)
class RenderedRow:
    """Renderable output for one source row."""

    line_number: int
    formula: str | None = None
    value: str | None = None
    artifact: RenderArtifact | None = None
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class EvalInput:
    """Input to the UI-independent evaluation pipeline."""

    source: str
    file_path: Path | None = None
    metadata: Any | None = None


@dataclass(frozen=True)
class EvalOutput:
    """Evaluation output consumed by the desktop UI."""

    rows: tuple[RenderedRow, ...]
    warnings: tuple[Diagnostic, ...] = field(default_factory=tuple)
