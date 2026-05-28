from pathlib import Path

from wmath.core import EvalInput, evaluate_placeholder, format_rendered_rows, format_warning_bar
from wmath.core.models import Diagnostic, EvalOutput, RenderedRow


def test_placeholder_returns_one_row_for_empty_source() -> None:
    output = evaluate_placeholder(EvalInput(source=""))

    assert len(output.rows) == 1
    assert output.rows[0].line_number == 1
    assert output.rows[0].formula is None


def test_placeholder_mirrors_source_lines() -> None:
    output = evaluate_placeholder(EvalInput(source="a = 1\nb = 2 |", file_path=Path("x.wmath")))

    assert [row.line_number for row in output.rows] == [1, 2]
    assert [row.formula for row in output.rows] == ["a = 1", "b = 2 |"]


def test_placeholder_preserves_trailing_blank_line() -> None:
    output = evaluate_placeholder(EvalInput(source="a = 1\n"))

    assert len(output.rows) == 2
    assert output.rows[1].line_number == 2
    assert output.rows[1].formula is None


def test_placeholder_reports_include_warning() -> None:
    output = evaluate_placeholder(EvalInput(source='include "defs.wmath"\na = 1'))

    assert output.rows[0].diagnostics[0].severity == "warning"
    assert "include evaluation is not implemented yet" in output.rows[0].diagnostics[0].message
    assert output.warnings[0].message == "line 1: include evaluation is not implemented yet"


def test_render_text_formats_active_line_values_and_diagnostics() -> None:
    row = RenderedRow(
        line_number=2,
        formula="x = 1 |",
        value="1",
        diagnostics=(Diagnostic("sample warning", "warning"),),
    )

    text = format_rendered_rows(EvalOutput(rows=(row,)), active_line=2)

    assert text == "▶   2  x = 1 |  ⇒ 1  ⚠ sample warning"


def test_warning_bar_formatting() -> None:
    text = format_warning_bar((Diagnostic("missing include", "warning"), Diagnostic("note", "info")))

    assert text == "⚠ missing include  ⓘ note"


def test_core_models_are_qt_independent() -> None:
    row = RenderedRow(line_number=3, formula="x", diagnostics=(Diagnostic("note", "info"),))

    assert row.line_number == 3
    assert row.diagnostics[0].severity == "info"
