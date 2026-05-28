from pathlib import Path

from wmath.core import evaluate
from wmath.core.models import EvalInput


def test_include_evaluates_as_prelude_without_rendering_included_rows(tmp_path: Path) -> None:
    main = tmp_path / "main.wmath"
    defs = tmp_path / "defs.wmath"
    defs.write_text("base = 10\ndouble(x) = x * 2\n", encoding="utf-8")

    output = evaluate(EvalInput('include "defs.wmath"\ndouble(base) |', file_path=main))

    assert len(output.rows) == 2
    assert output.rows[0].formula is None
    assert output.rows[0].value is None
    assert output.rows[1].value == "20"
    assert output.warnings == ()


def test_nested_include_resolves_relative_to_including_file(tmp_path: Path) -> None:
    main = tmp_path / "main.wmath"
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "defs.wmath").write_text('include "more.wmath"\na = b + 1\n', encoding="utf-8")
    (subdir / "more.wmath").write_text("b = 4\n", encoding="utf-8")

    output = evaluate(EvalInput('include "sub/defs.wmath"\na |', file_path=main))

    assert output.rows[1].value == "5"
    assert output.warnings == ()


def test_missing_include_produces_warning(tmp_path: Path) -> None:
    output = evaluate(EvalInput('include "missing.wmath"\n1 |', file_path=tmp_path / "main.wmath"))

    assert output.rows[0].formula is None
    assert output.rows[0].diagnostics[0].severity == "warning"
    assert "include file not found" in output.warnings[0].message
    assert output.rows[1].value == "1"


def test_include_cycle_produces_warning(tmp_path: Path) -> None:
    main = tmp_path / "main.wmath"
    defs = tmp_path / "defs.wmath"
    main.write_text('include "defs.wmath"\n', encoding="utf-8")
    defs.write_text('include "main.wmath"\na = 1\n', encoding="utf-8")

    output = evaluate(EvalInput(main.read_text(encoding="utf-8"), file_path=main))

    assert "include cycle detected" in output.warnings[0].message
