"""Runtime values, units, and formatting."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from wmath.core.models import Dimension, PlotArtifact
DIMENSIONLESS: Dimension = (0, 0, 0, 0, 0, 0, 0)


@dataclass(frozen=True)
class Scalar:
    value: float
    dimension: Dimension = DIMENSIONLESS


@dataclass(frozen=True)
class Vector:
    items: tuple[Scalar, ...]


@dataclass(frozen=True)
class Matrix:
    rows: tuple[Vector, ...]


@dataclass(frozen=True)
class StringValue:
    value: str


Value = Scalar | Vector | Matrix | StringValue | PlotArtifact


@dataclass(frozen=True)
class Unit:
    symbol: str
    factor: float
    dimension: Dimension


UNITS: dict[str, Unit] = {
    # SI base units, dimension order: m, kg, s, A, K, mol, cd.
    "m": Unit("m", 1.0, (1, 0, 0, 0, 0, 0, 0)),
    "kg": Unit("kg", 1.0, (0, 1, 0, 0, 0, 0, 0)),
    "s": Unit("s", 1.0, (0, 0, 1, 0, 0, 0, 0)),
    "A": Unit("A", 1.0, (0, 0, 0, 1, 0, 0, 0)),
    "K": Unit("K", 1.0, (0, 0, 0, 0, 1, 0, 0)),
    "mol": Unit("mol", 1.0, (0, 0, 0, 0, 0, 1, 0)),
    "cd": Unit("cd", 1.0, (0, 0, 0, 0, 0, 0, 1)),
    # SI named derived units. ASCII names are used where SI symbols are not identifiers.
    "rad": Unit("rad", 1.0, DIMENSIONLESS),
    "sr": Unit("sr", 1.0, DIMENSIONLESS),
    "Hz": Unit("Hz", 1.0, (0, 0, -1, 0, 0, 0, 0)),
    "N": Unit("N", 1.0, (1, 1, -2, 0, 0, 0, 0)),
    "Pa": Unit("Pa", 1.0, (-1, 1, -2, 0, 0, 0, 0)),
    "J": Unit("J", 1.0, (2, 1, -2, 0, 0, 0, 0)),
    "W": Unit("W", 1.0, (2, 1, -3, 0, 0, 0, 0)),
    "C": Unit("C", 1.0, (0, 0, 1, 1, 0, 0, 0)),
    "V": Unit("V", 1.0, (2, 1, -3, -1, 0, 0, 0)),
    "F": Unit("F", 1.0, (-2, -1, 4, 2, 0, 0, 0)),
    "ohm": Unit("ohm", 1.0, (2, 1, -3, -2, 0, 0, 0)),
    "S": Unit("S", 1.0, (-2, -1, 3, 2, 0, 0, 0)),
    "Wb": Unit("Wb", 1.0, (2, 1, -2, -1, 0, 0, 0)),
    "T": Unit("T", 1.0, (0, 1, -2, -1, 0, 0, 0)),
    "H": Unit("H", 1.0, (2, 1, -2, -2, 0, 0, 0)),
    "degC": Unit("degC", 1.0, (0, 0, 0, 0, 1, 0, 0)),
    "lm": Unit("lm", 1.0, (0, 0, 0, 0, 0, 0, 1)),
    "lx": Unit("lx", 1.0, (-2, 0, 0, 0, 0, 0, 1)),
    "Bq": Unit("Bq", 1.0, (0, 0, -1, 0, 0, 0, 0)),
    "Gy": Unit("Gy", 1.0, (2, 0, -2, 0, 0, 0, 0)),
    "Sv": Unit("Sv", 1.0, (2, 0, -2, 0, 0, 0, 0)),
    "kat": Unit("kat", 1.0, (0, 0, -1, 0, 0, 1, 0)),
}

_PREFERRED_UNITS = [
    "N",
    "Pa",
    "J",
    "W",
    "C",
    "V",
    "F",
    "ohm",
    "S",
    "Wb",
    "T",
    "H",
    "lx",
    "kat",
    "Gy",
    "Hz",
    "m",
    "kg",
    "s",
    "A",
    "K",
    "mol",
    "cd",
]


def unit_value(name: str) -> Scalar | None:
    unit = UNITS.get(name)
    if unit is None:
        return None
    return Scalar(unit.factor, unit.dimension)


def format_value(
    value: Value,
    display_unit: Scalar | None = None,
    display_symbol: str | None = None,
    *,
    significant_figures: int = 12,
    scientific_magnitude: int = 12,
) -> str:
    if isinstance(value, Scalar):
        return format_scalar(value, display_unit, display_symbol, significant_figures, scientific_magnitude)
    if isinstance(value, Vector):
        return "[" + ", ".join(
            format_scalar(item, display_unit, display_symbol, significant_figures, scientific_magnitude)
            for item in value.items
        ) + "]"
    if isinstance(value, StringValue):
        return repr(value.value)
    if isinstance(value, Matrix):
        row_text = [
            "["
            + ", ".join(
                format_scalar(item, display_unit, display_symbol, significant_figures, scientific_magnitude)
                for item in row.items
            )
            + "]"
            for row in value.rows
        ]
        return "[" + ", ".join(row_text) + "]"
    return format_plot(value, significant_figures, scientific_magnitude)


def format_scalar(
    value: Scalar,
    display_unit: Scalar | None = None,
    display_symbol: str | None = None,
    significant_figures: int = 12,
    scientific_magnitude: int = 12,
) -> str:
    suffix = ""
    number = value.value
    if display_unit is not None:
        if value.dimension != display_unit.dimension:
            raise ValueError("display unit is dimensionally incompatible")
        number = value.value / display_unit.value
        suffix = " " + (display_symbol or _unit_symbol(display_unit.dimension))
    elif value.dimension != DIMENSIONLESS:
        suffix = " " + _unit_symbol(value.dimension)
    return _format_number(number, significant_figures, scientific_magnitude) + suffix


def format_plot(plot: PlotArtifact, significant_figures: int = 12, scientific_magnitude: int = 12) -> str:
    x_min, x_max = plot.x_range
    y_min, y_max = plot.y_range
    return (
        f"plot: {len(plot.points)} points, "
        f"x {_format_number(x_min, significant_figures, scientific_magnitude)}.."
        f"{_format_number(x_max, significant_figures, scientific_magnitude)}, "
        f"y {_format_number(y_min, significant_figures, scientific_magnitude)}.."
        f"{_format_number(y_max, significant_figures, scientific_magnitude)}"
    )


def _unit_symbol(dimension: Dimension) -> str:
    for name in _PREFERRED_UNITS:
        if UNITS[name].dimension == dimension:
            return name
    parts: list[str] = []
    for symbol, exponent in zip(("m", "kg", "s", "A", "K", "mol", "cd"), dimension, strict=True):
        if exponent == 1:
            parts.append(symbol)
        elif exponent != 0:
            parts.append(f"{symbol}^{exponent}")
    return " ".join(parts) if parts else ""


def _format_number(value: float, significant_figures: int = 12, scientific_magnitude: int = 12) -> str:
    significant_figures = max(3, min(15, significant_figures))
    scientific_magnitude = max(3, min(12, scientific_magnitude))
    if isclose(value, round(value), rel_tol=0.0, abs_tol=1e-12):
        return str(int(round(value)))
    abs_value = abs(value)
    use_scientific = abs_value != 0 and (abs_value >= 10**scientific_magnitude or abs_value < 10 ** -scientific_magnitude)
    if use_scientific:
        return f"{value:.{significant_figures - 1}e}"
    return f"{value:.{significant_figures}g}"
