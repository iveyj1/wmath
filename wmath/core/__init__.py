"""UI-independent computation core for wmath."""

from wmath.core.models import Diagnostic, EvalInput, EvalOutput, RenderedRow
from wmath.core.placeholder import evaluate_placeholder
from wmath.core.render_text import format_rendered_row, format_rendered_rows, format_warning_bar

__all__ = [
    "Diagnostic",
    "EvalInput",
    "EvalOutput",
    "RenderedRow",
    "evaluate_placeholder",
    "format_rendered_row",
    "format_rendered_rows",
    "format_warning_bar",
]
