"""UI-independent computation core for wmath."""

from wmath.core.evaluator import evaluate
from wmath.core.lexer import Token, lex
from wmath.core.models import Diagnostic, EvalInput, EvalOutput, PlotArtifact, RenderedRow
from wmath.core.parser import ParsedLine, parse_line
from wmath.core.placeholder import evaluate_placeholder
from wmath.core.render_text import format_rendered_row, format_rendered_rows, format_warning_bar

__all__ = [
    "Diagnostic",
    "EvalInput",
    "EvalOutput",
    "ParsedLine",
    "PlotArtifact",
    "RenderedRow",
    "Token",
    "evaluate",
    "evaluate_placeholder",
    "lex",
    "parse_line",
    "format_rendered_row",
    "format_rendered_rows",
    "format_warning_bar",
]
