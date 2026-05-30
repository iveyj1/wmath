from wmath.core import evaluate, format_rendered_rows
from wmath.core.models import EvalInput, PlotArtifact


def test_plot_returns_text_and_structured_artifact() -> None:
    output = evaluate(EvalInput("x = [0, 1, 2]\ny = [0, 1, 4]\nplot(x, y, 0, 2, 0, 4) |"))

    row = output.rows[2]
    assert row.value == "plot: 3 points, x 0..2, y 0..4"
    assert isinstance(row.artifact, PlotArtifact)
    assert row.artifact.points == ((0.0, 0.0), (1.0, 1.0), (2.0, 4.0))
    assert row.artifact.x_range == (0.0, 2.0)
    assert row.artifact.y_range == (0.0, 4.0)


def test_plot_supports_unit_bearing_axes() -> None:
    output = evaluate(
        EvalInput("t = [0, 1, 2] s\nd = [0, 4, 8] m\nplot(t, d, 0 s, 2 s, 0 m, 10 m) |")
    )

    artifact = output.rows[2].artifact
    assert isinstance(artifact, PlotArtifact)
    assert artifact.points == ((0.0, 0.0), (1.0, 4.0), (2.0, 8.0))
    assert output.rows[2].value == "plot: 3 points, x 0..2, y 0..10"


def test_plot_accepts_range_vectors() -> None:
    output = evaluate(EvalInput("plot([0, 1, 2], [0, 1, 4], [0, 2], [0, 4]) |"))

    row = output.rows[0]
    assert row.value == "plot: 3 points, x 0..2, y 0..4"
    assert isinstance(row.artifact, PlotArtifact)
    assert row.artifact.requested_size is None


def test_plot_accepts_range_vectors_and_requested_size() -> None:
    output = evaluate(EvalInput("plot([0, 1, 2], [0, 1, 4], [0, 2], [0, 4], [500, 240]) |"))

    assert isinstance(output.rows[0].artifact, PlotArtifact)
    assert output.rows[0].artifact.requested_size == (500, 240)


def test_plot_range_vectors_support_units() -> None:
    output = evaluate(EvalInput("t = [0, 1, 2] s\nd = [0, 4, 8] m\nplot(t, d, [0 s, 2 s], [0 m, 10 m]) |"))

    assert output.rows[2].value == "plot: 3 points, x 0..2, y 0..10"


def test_plot_rejects_wrong_argument_count() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], [0, 1]) |"))

    assert output.rows[0].diagnostics[0].message == "plot expects four, five, or six arguments"


def test_plot_rejects_non_vector_axes() -> None:
    output = evaluate(EvalInput("plot(1, [0, 1], 0, 1, 0, 1) |"))

    assert output.rows[0].diagnostics[0].message == "plot expects x and y vectors"


def test_plot_rejects_mismatched_vector_lengths() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1, 2], 0, 1, 0, 2) |"))

    assert output.rows[0].diagnostics[0].message == "plot vectors must have the same length"


def test_plot_rejects_too_few_points() -> None:
    output = evaluate(EvalInput("plot([0], [0], 0, 1, 0, 1) |"))

    assert output.rows[0].diagnostics[0].message == "plot requires at least two points"


def test_plot_rejects_incompatible_bounds() -> None:
    output = evaluate(EvalInput("t = [0, 1] s\ny = [0, 1] m\nplot(t, y, 0 m, 1 m, 0 m, 1 m) |"))

    assert output.rows[2].diagnostics[0].message == "plot x bounds are dimensionally incompatible"


def test_plot_rejects_malformed_range_vector() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], [0, 1, 2], [0, 1]) |"))

    assert output.rows[0].diagnostics[0].message == "plot x range must be a two-item vector"


def test_plot_rejects_malformed_size_vector() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], [0, 1], [0, 1], [400]) |"))

    assert output.rows[0].diagnostics[0].message == "plot size must be a two-item vector"


def test_plot_rejects_dimensioned_size_vector() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], [0, 1], [0, 1], [400 m, 200 m]) |"))

    assert output.rows[0].diagnostics[0].message == "plot size values must be dimensionless"


def test_plot_rejects_non_positive_size_vector() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], [0, 1], [0, 1], [400, 0]) |"))

    assert output.rows[0].diagnostics[0].message == "plot size values must be positive"


def test_plot_rejects_non_increasing_bounds() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], 1, 0, 0, 1) |"))

    assert output.rows[0].diagnostics[0].message == "plot x bounds must be increasing"


def test_plot_rejects_display_unit_suffix_for_now() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], 0, 1, 0, 1) | m"))

    assert output.rows[0].diagnostics[0].message == "plots do not support display unit suffixes yet"


def test_text_renderer_includes_plot_summary() -> None:
    output = evaluate(EvalInput("plot([0, 1], [0, 1], 0, 1, 0, 1) |"))

    rendered = format_rendered_rows(output)

    assert "⇒ plot: 2 points, x 0..1, y 0..1" in rendered
