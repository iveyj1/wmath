"""Temporary render pipeline used before the parser/evaluator exists."""

from __future__ import annotations

from wmath.core.models import EvalInput, EvalOutput, RenderedRow


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

    rows = tuple(
        RenderedRow(line_number=index, formula=line.rstrip() or None)
        for index, line in enumerate(lines, start=1)
    )
    return EvalOutput(rows=rows)
