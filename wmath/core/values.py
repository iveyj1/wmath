"""Runtime values, units, and formatting."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

Dimension = tuple[int, int, int, int]
DIMENSIONLESS: Dimension = (0, 0, 0, 0)


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


Value = Scalar | Vector | Matrix


@dataclass(frozen=True)
class Unit:
    symbol: str
    factor: float
    dimension: Dimension


UNITS: dict[str, Unit] = {
    "m": Unit("m", 1.0, (1, 0, 0, 0)),
    "kg": Unit("kg", 1.0, (0, 1, 0, 0)),
    "s": Unit("s", 1.0, (0, 0, 1, 0)),
    "K": Unit("K", 1.0, (0, 0, 0, 1)),
    "N": Unit("N", 1.0, (1, 1, -2, 0)),
    "J": Unit("J", 1.0, (2, 1, -2, 0)),
    "Pa": Unit("Pa", 1.0, (-1, 1, -2, 0)),
    "W": Unit("W", 1.0, (2, 1, -3, 0)),
    "Hz": Unit("Hz", 1.0, (0, 0, -1, 0)),
}

_PREFERRED_UNITS = ["N", "J", "Pa", "W", "Hz", "m", "kg", "s", "K"]


def unit_value(name: str) -> Scalar | None:
    unit = UNITS.get(name)
    if unit is None:
        return None
    return Scalar(unit.factor, unit.dimension)


def format_value(value: Value, display_unit: Scalar | None = None) -> str:
    if isinstance(value, Scalar):
        return format_scalar(value, display_unit)
    if isinstance(value, Vector):
        return "[" + ", ".join(format_scalar(item, display_unit) for item in value.items) + "]"
    row_text = ["[" + ", ".join(format_scalar(item, display_unit) for item in row.items) + "]" for row in value.rows]
    return "[" + ", ".join(row_text) + "]"


def format_scalar(value: Scalar, display_unit: Scalar | None = None) -> str:
    suffix = ""
    number = value.value
    if display_unit is not None:
        if value.dimension != display_unit.dimension:
            raise ValueError("display unit is dimensionally incompatible")
        number = value.value / display_unit.value
        suffix = " " + _unit_symbol(display_unit.dimension)
    elif value.dimension != DIMENSIONLESS:
        suffix = " " + _unit_symbol(value.dimension)
    return _format_number(number) + suffix


def _unit_symbol(dimension: Dimension) -> str:
    for name in _PREFERRED_UNITS:
        if UNITS[name].dimension == dimension:
            return name
    parts: list[str] = []
    for symbol, exponent in zip(("m", "kg", "s", "K"), dimension, strict=True):
        if exponent == 1:
            parts.append(symbol)
        elif exponent != 0:
            parts.append(f"{symbol}^{exponent}")
    return " ".join(parts) if parts else ""


def _format_number(value: float) -> str:
    if isclose(value, round(value), rel_tol=0.0, abs_tol=1e-12):
        return str(int(round(value)))
    return f"{value:.12g}"
