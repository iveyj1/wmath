from pathlib import Path

from wmath.core import evaluate, parse_line
from wmath.core.ast import CallExpr, StringExpr
from wmath.core.models import EvalInput


def test_parser_supports_string_literal_function_arguments() -> None:
    parsed = parse_line('csv("data.csv", "time")')

    assert isinstance(parsed.statement.expr, CallExpr)  # type: ignore[union-attr]
    assert isinstance(parsed.statement.expr.args[0], StringExpr)  # type: ignore[union-attr]
    assert parsed.statement.expr.args[0].value == "data.csv"  # type: ignore[union-attr]


def test_csv_import_by_header(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("time,distance\n0,0\n1,4.9\n2,19.6\n", encoding="utf-8")

    output = evaluate(EvalInput('d = csv("run.csv", "distance") |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].value == "[0, 4.9, 19.6]"


def test_csv_import_by_one_based_index(tmp_path: Path) -> None:
    data = tmp_path / "points.csv"
    data.write_text("0,10\n1,11\n2,12\n", encoding="utf-8")

    output = evaluate(EvalInput('y = csv("points.csv", 2) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].value == "[10, 11, 12]"


def test_csv_import_ignores_blank_rows(tmp_path: Path) -> None:
    data = tmp_path / "points.csv"
    data.write_text("0\n\n1\n  \n2\n", encoding="utf-8")

    output = evaluate(EvalInput('x = csv("points.csv", 1) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].value == "[0, 1, 2]"


def test_csv_import_can_attach_units_and_plot(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("time,distance\n0,0\n1,4\n2,8\n", encoding="utf-8")
    source = '\n'.join(
        [
            't = csv("run.csv", "time") * s',
            'd = csv("run.csv", "distance") * m',
            'plot(t, d, [0 s, 2 s], [0 m, 10 m]) |',
        ]
    )

    output = evaluate(EvalInput(source, file_path=tmp_path / "sheet.wmath"))

    assert output.rows[2].value == "plot: 3 points, x 0..2, y 0..10"


def test_csv_missing_file_diagnostic(tmp_path: Path) -> None:
    output = evaluate(EvalInput('csv("missing.csv", 1) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].diagnostics[0].message == "csv file not found: missing.csv"


def test_csv_missing_header_diagnostic(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("time,distance\n", encoding="utf-8")

    output = evaluate(EvalInput('csv("run.csv", "speed") |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].diagnostics[0].message == "csv header not found: speed"


def test_csv_nonnumeric_cell_diagnostic(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("0\nbad\n", encoding="utf-8")

    output = evaluate(EvalInput('csv("run.csv", 1) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].diagnostics[0].message == "csv row 2 has nonnumeric selected cell: 'bad'"


def test_csv_empty_cell_diagnostic(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("0,1\n2,\n", encoding="utf-8")

    output = evaluate(EvalInput('csv("run.csv", 2) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].diagnostics[0].message == "csv row 2 has empty selected cell"


def test_csv_missing_column_diagnostic(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("0,1\n2\n", encoding="utf-8")

    output = evaluate(EvalInput('csv("run.csv", 2) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].diagnostics[0].message == "csv row 2 missing selected column"


def test_csv_bad_selector_diagnostic(tmp_path: Path) -> None:
    data = tmp_path / "run.csv"
    data.write_text("0\n1\n", encoding="utf-8")

    output = evaluate(EvalInput('csv("run.csv", [1]) |', file_path=tmp_path / "sheet.wmath"))

    assert output.rows[0].diagnostics[0].message == "csv selector must be a string header or 1-based column index"
