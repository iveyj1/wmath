from wmath.core import evaluate, lex, parse_line
from wmath.core.ast import AssignmentStmt, CallExpr, FunctionStmt, IncludeStmt
from wmath.core.models import EvalInput
from wmath.storage import SheetMetadata


def test_lexer_numbers_identifiers_comments_and_display_pipe() -> None:
    tokens, errors = lex("area = 1.5e2 /* comment */ | m # trailing")

    assert errors == []
    assert [(token.kind, token.text) for token in tokens[:-1]] == [
        ("identifier", "area"),
        ("equals", "="),
        ("number", "1.5e2"),
        ("pipe", "|"),
        ("identifier", "m"),
    ]


def test_parser_assignment_and_display() -> None:
    parsed = parse_line("area = length * width | m")

    assert parsed.diagnostics == ()
    assert isinstance(parsed.statement, AssignmentStmt)
    assert parsed.statement.name == "area"
    assert parsed.statement.show_value is True


def test_parser_function_declaration_and_call() -> None:
    function = parse_line("f(x, y) = x + y")
    call = parse_line("f(1, 2)")

    assert isinstance(function.statement, FunctionStmt)
    assert isinstance(call.statement.expr, CallExpr)  # type: ignore[union-attr]


def test_parser_include() -> None:
    parsed = parse_line('include "defs.wmath"')

    assert isinstance(parsed.statement, IncludeStmt)
    assert parsed.statement.path == "defs.wmath"


def test_parser_array_index_and_slice_parse_without_diagnostics() -> None:
    assert parse_line("v = [1, 2, 3]").diagnostics == ()
    assert parse_line("v[1]").diagnostics == ()
    assert parse_line("v[2:]").diagnostics == ()
    assert parse_line("v[:3]").diagnostics == ()


def test_evaluator_scalar_assignment_and_display() -> None:
    output = evaluate(EvalInput("a = 2\nb = 3\na + b |"))

    assert [row.value for row in output.rows] == [None, None, "5"]
    assert output.rows[2].diagnostics == ()


def test_evaluator_hides_value_without_display_marker() -> None:
    output = evaluate(EvalInput("a = 2\na + 1"))

    assert [row.value for row in output.rows] == [None, None]


def test_evaluator_all_values_mode_ignores_display_marker_state() -> None:
    output = evaluate(EvalInput("a = 2\na + 1", metadata=SheetMetadata(showValuesMode="all_assignments")))

    assert [row.value for row in output.rows] == ["2", "3"]


def test_evaluator_number_format_metadata_controls_output() -> None:
    metadata = SheetMetadata(significantFigures=4, scientificMagnitude=3)
    output = evaluate(EvalInput("12345.6789 |\n0.00012345 |", metadata=metadata))

    assert [row.value for row in output.rows] == ["1.235e+04", "1.234e-04"]


def test_evaluator_rendered_formula_omits_display_suffix() -> None:
    output = evaluate(EvalInput("work = 20 J | J"))

    assert output.rows[0].formula == "work = 20 J"
    assert output.rows[0].value == "20 J"


def test_evaluator_assignment_display_and_persistent_environment() -> None:
    output = evaluate(EvalInput("a = 2 |\nb = a * 4 |"))

    assert [row.value for row in output.rows] == ["2", "8"]


def test_evaluator_functions_and_builtins() -> None:
    output = evaluate(EvalInput("double(x) = x * 2\ndouble(4) |\nsqrt(9) |"))

    assert [row.value for row in output.rows] == [None, "8", "3"]


def test_evaluator_row_failure_does_not_clear_prior_environment() -> None:
    output = evaluate(EvalInput("a = 2\nmissing + 1 |\na + 1 |"))

    assert output.rows[1].diagnostics[0].message == "unknown name: missing"
    assert output.rows[2].value == "3"


def test_evaluator_line_continuation_and_block_comments() -> None:
    output = evaluate(EvalInput("a = 1 + \\\n2 |\n/* comment\nblock */\na + 1 |"))

    assert output.rows[0].value == "3"
    assert output.rows[-1].value == "4"


def test_evaluator_missing_include_warning() -> None:
    output = evaluate(EvalInput('include "defs.wmath"\na = 1 |'))

    assert output.rows[0].formula is None
    assert output.rows[0].diagnostics[0].severity == "warning"
    assert "include file not found" in output.warnings[0].message
    assert output.rows[1].value == "1"
