from wmath.core import evaluate
from wmath.core.models import EvalInput


def values(source: str) -> list[str | None]:
    return [row.value for row in evaluate(EvalInput(source)).rows]


def test_units_multiply_and_display_default_conventional() -> None:
    output = evaluate(EvalInput("length = 2 m\nforce = 10 N\nwork = force * length |"))

    assert output.rows[2].value == "20 J"


def test_explicit_display_unit_compatible() -> None:
    output = evaluate(EvalInput("force = 10 N\nd = 2 m\nwork = force * d | J"))

    assert output.rows[2].value == "20 J"


def test_incompatible_unit_addition_diagnostic() -> None:
    output = evaluate(EvalInput("1 m + 1 s |"))

    assert output.rows[0].diagnostics[0].message == "dimensions are incompatible"


def test_power_and_sqrt_units() -> None:
    assert values("area = (3 m)^2 |\nsqrt(area) |") == ["9 m^2", "3 m"]


def test_vector_elementwise_and_scalar_ops() -> None:
    assert values("v = [1, 2, 3]\nw = v * 2 |\nw + [1, 1, 1] |") == [None, "[2, 4, 6]", "[3, 5, 7]"]


def test_vector_index_slice_append_length_dot() -> None:
    output = evaluate(EvalInput("v = [1, 2, 3]\nv[2] |\nv[2:] |\nappend(v, [4]) |\nlength(v) |\ndot(v, v) |"))

    assert [row.value for row in output.rows] == [None, "2", "[2, 3]", "[1, 2, 3, 4]", "3", "14"]


def test_matrix_literal_and_matrix_arithmetic_diagnostic() -> None:
    output = evaluate(EvalInput("m = [[1, 2], [3, 4]] |\nm + m |"))

    assert output.rows[0].value == "[[1, 2], [3, 4]]"
    assert output.rows[1].diagnostics[0].message == "matrix arithmetic is not implemented yet"


def test_matrix_width_validation() -> None:
    output = evaluate(EvalInput("[[1], [2, 3]] |"))

    assert output.rows[0].diagnostics[0].message == "matrix rows must have consistent widths"
