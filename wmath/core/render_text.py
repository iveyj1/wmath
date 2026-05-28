"""Plain-text rendering helpers for evaluation output.

This module intentionally has no Qt imports. The desktop UI can use these helpers
until richer rendered widgets exist, and tests can verify row/diagnostic formatting
headlessly.
"""

from __future__ import annotations

from wmath.core.models import Diagnostic, EvalOutput, RenderedRow


def format_rendered_rows(output: EvalOutput, *, active_line: int | None = None) -> str:
    """Format an evaluation output as line-aligned plain text.

    Args:
        output: Evaluated rows and warnings.
        active_line: 1-based active source line. If provided, the row is marked
            with `▶`.
    """

    return "\n".join(format_rendered_row(row, active_line=active_line) for row in output.rows)


def format_rendered_row(row: RenderedRow, *, active_line: int | None = None) -> str:
    """Format one rendered row."""

    marker = "▶" if active_line == row.line_number else " "
    formula = row.formula or ""
    value = f"  ⇒ {row.value}" if row.value else ""
    diagnostics = format_diagnostics(row.diagnostics)
    diagnostic_text = f"  {diagnostics}" if diagnostics else ""
    return f"{marker}{row.line_number:>4}  {formula}{value}{diagnostic_text}"


def format_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> str:
    """Format row-local diagnostics compactly."""

    return "  ".join(f"{_severity_symbol(diagnostic)} {diagnostic.message}" for diagnostic in diagnostics)


def format_warning_bar(warnings: tuple[Diagnostic, ...]) -> str:
    """Format document-level warnings for the warning bar."""

    return "  ".join(f"{_severity_symbol(warning)} {warning.message}" for warning in warnings)


def _severity_symbol(diagnostic: Diagnostic) -> str:
    if diagnostic.severity == "info":
        return "ⓘ"
    if diagnostic.severity == "warning":
        return "⚠"
    return "✖"
