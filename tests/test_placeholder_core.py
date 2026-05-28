from wmath.core import EvalInput, evaluate_placeholder
from wmath.core.models import Diagnostic, RenderedRow


def test_placeholder_returns_one_row_for_empty_source() -> None:
    output = evaluate_placeholder(EvalInput(source=""))

    assert len(output.rows) == 1
    assert output.rows[0].line_number == 1
    assert output.rows[0].formula is None


def test_placeholder_mirrors_source_lines() -> None:
    output = evaluate_placeholder(EvalInput(source="a = 1\nb = 2 |"))

    assert [row.line_number for row in output.rows] == [1, 2]
    assert [row.formula for row in output.rows] == ["a = 1", "b = 2 |"]


def test_placeholder_preserves_trailing_blank_line() -> None:
    output = evaluate_placeholder(EvalInput(source="a = 1\n"))

    assert len(output.rows) == 2
    assert output.rows[1].line_number == 2
    assert output.rows[1].formula is None


def test_core_models_are_qt_independent() -> None:
    row = RenderedRow(line_number=3, formula="x", diagnostics=(Diagnostic("note", "info"),))

    assert row.line_number == 3
    assert row.diagnostics[0].severity == "info"
