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


def test_user_defined_display_unit_keeps_requested_label() -> None:
    output = evaluate(EvalInput("ft = 0.3048 m\nd = 20 m | ft"))

    assert output.rows[1].value == "65.6167979003 ft"


def test_compound_user_defined_display_unit_keeps_requested_label() -> None:
    output = evaluate(EvalInput("ft = 0.3048 m\nminute = 60 s\nspeed = 10 m / s | ft / minute"))

    assert output.rows[2].value == "1968.50393701 ft/minute"


def test_display_unit_rejects_arbitrary_calculation() -> None:
    output = evaluate(EvalInput("ft = 0.3048 m\nd = 20 m | 2 ft"))

    assert output.rows[1].diagnostics[0].message == "display unit must be a unit-name expression"


def test_incompatible_unit_addition_diagnostic() -> None:
    output = evaluate(EvalInput("1 m + 1 s |"))

    assert output.rows[0].diagnostics[0].message == "dimensions are incompatible"


def test_power_and_sqrt_units() -> None:
    assert values("area = (3 m)^2 |\nsqrt(area) |") == ["9 m^2", "3 m"]


def test_si_base_units_include_current_amount_and_luminosity() -> None:
    output = evaluate(EvalInput("current = 2 A |\namount = 3 mol |\nbrightness = 4 cd |"))

    assert [row.value for row in output.rows] == ["2 A", "3 mol", "4 cd"]


def test_si_base_units_combine_in_fallback_formatting() -> None:
    output = evaluate(EvalInput("charge_like = 2 A * s |\nexotic = 3 mol / cd |"))

    assert [row.value for row in output.rows] == ["2 C", "3 mol cd^-1"]


def test_si_named_derived_units_display_by_default() -> None:
    output = evaluate(
        EvalInput(
            "\n".join(
                [
                    "freq = 2 / s |",
                    "force = 3 kg * m / s^2 |",
                    "pressure = 4 N / m^2 |",
                    "energy = 5 N * m |",
                    "power = 6 J / s |",
                    "charge = 7 A * s |",
                    "voltage = 8 W / A |",
                    "capacitance = 9 C / V |",
                    "resistance = 10 V / A |",
                    "conductance = 11 A / V |",
                    "flux = 12 V * s |",
                    "field = 13 Wb / m^2 |",
                    "inductance = 14 Wb / A |",
                    "illuminance = 15 cd / m^2 |",
                    "catalytic = 16 mol / s |",
                    "absorbed = 17 J / kg |",
                ]
            )
        )
    )

    assert [row.value for row in output.rows] == [
        "2 Hz",
        "3 N",
        "4 Pa",
        "5 J",
        "6 W",
        "7 C",
        "8 V",
        "9 F",
        "10 ohm",
        "11 S",
        "12 Wb",
        "13 T",
        "14 H",
        "15 lx",
        "16 kat",
        "17 Gy",
    ]


def test_ambiguous_si_named_derived_units_are_available_explicitly() -> None:
    output = evaluate(EvalInput("angle = 2 | rad\nsolid = 3 | sr\ntemp = 4 K | degC\ndose = 5 J / kg | Sv"))

    assert [row.value for row in output.rows] == ["2 rad", "3 sr", "4 degC", "5 Sv"]


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
