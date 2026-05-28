"""Temporary render pipeline used before the parser/evaluator exists."""

from __future__ import annotations

from wmath.core.models import Diagnostic, EvalInput, EvalOutput, RenderedRow


def evaluate_placeholder(eval_input: EvalInput) -> EvalOutput:
    """Mirror source lines into render rows without evaluating expressions.

    This keeps Milestone 001 useful while preserving the same core/UI boundary
    that the real evaluator will use.
    """

    lines = eval_input.source.splitlines()
    if eval_input.source.endswith("\n"):
        lines.append("")
    if not lines:
        lines = [""]

    rendered_rows: list[RenderedRow] = []
    warnings: list[Diagnostic] = []
    for index, line in enumerate(lines, start=1):
        text = line.rstrip()
        diagnostics: tuple[Diagnostic, ...] = ()
        if text.lstrip().startswith("include "):
            diagnostic = Diagnostic("include evaluation is not implemented yet", "warning")
            diagnostics = (diagnostic,)
            warnings.append(Diagnostic(f"line {index}: {diagnostic.message}", "warning"))
        rendered_rows.append(
            RenderedRow(line_number=index, formula=text or None, diagnostics=diagnostics)
        )

    return EvalOutput(rows=tuple(rendered_rows), warnings=tuple(warnings))
