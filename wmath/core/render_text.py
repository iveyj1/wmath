"""Plain-text rendering helpers for evaluation output.

This module intentionally has no Qt imports. The desktop UI can use these helpers
until richer rendered widgets exist, and tests can verify row/diagnostic formatting
headlessly.
"""

from __future__ import annotations

from wmath.core.models import Diagnostic, EvalOutput, RenderedRow


def format_rendered_rows(
    output: EvalOutput,
    *,
    active_line: int | None = None,
    value_column_percent: float = 60.0,
    line_width: int = 100,
) -> str:
    """Format an evaluation output as line-aligned plain text.

    Args:
        output: Evaluated rows and warnings.
        active_line: 1-based active source line. If provided, the row is marked
            with `▶`.
        value_column_percent: Approximate column for values, clamped to 40..90.
        line_width: Formatting width used to compute the value column.
    """

    return "\n".join(
        format_rendered_row(
            row,
            active_line=active_line,
            value_column_percent=value_column_percent,
            line_width=line_width,
        )
        for row in output.rows
    )


def format_rendered_row(
    row: RenderedRow,
    *,
    active_line: int | None = None,
    value_column_percent: float = 60.0,
    line_width: int = 100,
) -> str:
    """Format one rendered row."""

    marker = "▶" if active_line == row.line_number else " "
    formula = row.formula or ""
    prefix = f"{marker}{row.line_number:>4}  {formula}"
    value = f"⇒ {row.value}" if row.value else ""
    diagnostics = format_diagnostics(row.diagnostics)
    diagnostic_text = f"  {diagnostics}" if diagnostics else ""
    if not value:
        return f"{prefix}{diagnostic_text}"

    value_column = _value_column(value_column_percent, line_width)
    padding = " " * max(2, value_column - len(prefix))
    return f"{prefix}{padding}{value}{diagnostic_text}"


def format_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> str:
    """Format row-local diagnostics compactly."""

    return "  ".join(f"{_severity_symbol(diagnostic)} {diagnostic.message}" for diagnostic in diagnostics)


def format_warning_bar(warnings: tuple[Diagnostic, ...]) -> str:
    """Format document-level warnings for the warning bar."""

    return "\n".join(f"{_severity_symbol(warning)} {warning.message}" for warning in warnings)


def _value_column(value_column_percent: float, line_width: int) -> int:
    clamped_percent = max(40.0, min(90.0, value_column_percent))
    return max(12, round(max(40, line_width) * clamped_percent / 100.0))


def _severity_symbol(diagnostic: Diagnostic) -> str:
    if diagnostic.severity == "info":
        return "ⓘ"
    if diagnostic.severity == "warning":
        return "⚠"
    return "✖"
