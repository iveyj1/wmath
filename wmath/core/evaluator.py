"""Evaluator for wmath rows."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from wmath.core.ast import (
    ArrayExpr,
    AssignmentStmt,
    BinaryExpr,
    CallExpr,
    Expr,
    ExpressionStmt,
    FunctionStmt,
    IncludeStmt,
    IndexExpr,
    NameExpr,
    NumberExpr,
    SliceExpr,
    UnaryExpr,
)
from wmath.core.models import Diagnostic, EvalInput, EvalOutput, RenderedRow
from wmath.core.parser import parse_line
from wmath.core.values import DIMENSIONLESS, Matrix, Scalar, Value, Vector, format_value, unit_value


@dataclass(frozen=True)
class UserFunction:
    params: tuple[str, ...]
    body: Expr


@dataclass
class Environment:
    values: dict[str, Value]
    functions: dict[str, UserFunction]


def evaluate(eval_input: EvalInput) -> EvalOutput:
    env = Environment(values={}, functions={})
    file_path = eval_input.file_path.expanduser().resolve() if eval_input.file_path else None
    include_stack = (file_path,) if file_path is not None else ()
    return _evaluate_source(
        eval_input.source,
        env,
        file_path=file_path,
        include_stack=include_stack,
        eval_metadata=eval_input.metadata,
    )


def _evaluate_source(
    source: str,
    env: Environment,
    *,
    file_path: Path | None,
    include_stack: tuple[Path, ...],
    eval_metadata: object | None = None,
) -> EvalOutput:
    rows: list[RenderedRow] = []
    warnings: list[Diagnostic] = []
    for line_number, line in enumerate(_logical_lines(source), start=1):
        parsed = parse_line(line)
        diagnostics = [Diagnostic(message) for message in parsed.diagnostics]
        stmt = parsed.statement
        formula = _formula_text(line, stmt) if stmt is not None else (line.rstrip() or None)
        value_text: str | None = None
        if stmt is None:
            rows.append(RenderedRow(line_number, formula, None, tuple(diagnostics)))
            continue
        if isinstance(stmt, IncludeStmt):
            include_warnings = _evaluate_include(stmt, env, file_path, include_stack, line_number)
            warnings.extend(include_warnings)
            rows.append(RenderedRow(line_number, None, None, include_warnings))
            continue
        if not diagnostics:
            try:
                if isinstance(stmt, AssignmentStmt):
                    value = _eval_expr(stmt.expr, env)
                    env.values[stmt.name] = value
                    if stmt.show_value or _show_all_values(eval_metadata):
                        value_text = _format_display(value, stmt.display, _display_label(line), env)
                elif isinstance(stmt, FunctionStmt):
                    env.functions[stmt.name] = UserFunction(stmt.params, stmt.expr)
                    if stmt.show_value:
                        diagnostics.append(Diagnostic("function definitions do not display a value", "info"))
                elif isinstance(stmt, ExpressionStmt):
                    value = _eval_expr(stmt.expr, env)
                    if stmt.show_value or _show_all_values(eval_metadata):
                        value_text = _format_display(value, stmt.display, _display_label(line), env)
            except EvalError as exc:
                diagnostics.append(Diagnostic(str(exc)))
        rows.append(RenderedRow(line_number, formula, value_text, tuple(diagnostics)))
    return EvalOutput(rows=tuple(rows), warnings=tuple(warnings))


def _evaluate_include(
    stmt: IncludeStmt,
    env: Environment,
    current_file: Path | None,
    include_stack: tuple[Path, ...],
    line_number: int,
) -> tuple[Diagnostic, ...]:
    base_dir = current_file.parent if current_file is not None else Path.cwd()
    target = (base_dir / stmt.path).expanduser().resolve()
    location = f"line {line_number}: include {stmt.path!r}"
    if target in include_stack:
        return (Diagnostic(f"{location}: include cycle detected", "warning"),)
    try:
        source = target.read_text(encoding="utf-8")
    except OSError:
        return (Diagnostic(f"{location}: include file not found", "warning"),)

    output = _evaluate_source(source, env, file_path=target, include_stack=(*include_stack, target))
    return output.warnings


def _show_all_values(eval_metadata: object | None) -> bool:
    return getattr(eval_metadata, "showValuesMode", "explicit") == "all_assignments"


def _formula_text(line: str, stmt: object) -> str | None:
    text = line.rstrip()
    if not text:
        return None
    if isinstance(stmt, IncludeStmt):
        return None
    pipe_index = _top_level_pipe_index(text)
    if pipe_index is not None:
        text = text[:pipe_index].rstrip()
    return text or None


def _top_level_pipe_index(text: str) -> int | None:
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "([":
            depth += 1
        elif char in ")]" and depth > 0:
            depth -= 1
        elif char == "|" and depth == 0:
            return index
    return None


def _display_label(line: str) -> str | None:
    pipe_index = _top_level_pipe_index(line.rstrip())
    if pipe_index is None:
        return None
    label = line[pipe_index + 1 :].strip()
    if not label:
        return None
    return "".join(label.split())


def _format_display(value: Value, display: Expr | None, display_label: str | None, env: Environment) -> str:
    display_unit = None
    if display is not None:
        _validate_display_unit_expr(display)
        unit = _eval_expr(display, env)
        if not isinstance(unit, Scalar):
            raise EvalError("display unit must be scalar")
        display_unit = unit
    try:
        return format_value(value, display_unit, display_label)
    except ValueError as exc:
        raise EvalError(str(exc)) from exc


def _validate_display_unit_expr(expr: Expr) -> None:
    if isinstance(expr, NameExpr):
        return
    if isinstance(expr, BinaryExpr):
        if expr.op in ("*", "/"):
            _validate_display_unit_expr(expr.left)
            _validate_display_unit_expr(expr.right)
            return
        if expr.op == "^" and isinstance(expr.right, NumberExpr) and expr.right.value.is_integer():
            _validate_display_unit_expr(expr.left)
            return
    raise EvalError("display unit must be a unit-name expression")


def _logical_lines(source: str) -> list[str]:
    lines = _strip_block_comments(source).splitlines()
    if source.endswith("\n"):
        lines.append("")
    if not lines:
        return [""]
    logical: list[str] = []
    pending = ""
    for line in lines:
        if line.endswith("\\"):
            pending += line[:-1]
        else:
            logical.append(pending + line)
            pending = ""
    if pending:
        logical.append(pending)
    return logical


def _strip_block_comments(source: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(source):
        if source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end == -1:
                result.append("\n" * source[index:].count("\n"))
                break
            comment = source[index : end + 2]
            result.append("\n" * comment.count("\n"))
            index = end + 2
        else:
            result.append(source[index])
            index += 1
    return "".join(result)


class EvalError(Exception):
    pass


def _eval_expr(expr: Expr, env: Environment) -> Value:
    if isinstance(expr, NumberExpr):
        return Scalar(expr.value)
    if isinstance(expr, NameExpr):
        if expr.name in env.values:
            return env.values[expr.name]
        unit = unit_value(expr.name)
        if unit is not None:
            return unit
        raise EvalError(f"unknown name: {expr.name}")
    if isinstance(expr, UnaryExpr):
        value = _eval_expr(expr.expr, env)
        if not isinstance(value, Scalar):
            raise EvalError("unary operators require scalar")
        return value if expr.op == "+" else Scalar(-value.value, value.dimension)
    if isinstance(expr, BinaryExpr):
        return _eval_binary(_eval_expr(expr.left, env), expr.op, _eval_expr(expr.right, env))
    if isinstance(expr, CallExpr):
        if not isinstance(expr.callee, NameExpr):
            raise EvalError("only named function calls are supported")
        args = tuple(_eval_expr(arg, env) for arg in expr.args)
        return _call_function(expr.callee.name, args, env)
    if isinstance(expr, ArrayExpr):
        return _eval_array(expr, env)
    if isinstance(expr, IndexExpr):
        return _eval_index(_eval_expr(expr.collection, env), _eval_expr(expr.index, env))
    if isinstance(expr, SliceExpr):
        start = None if expr.start is None else _eval_expr(expr.start, env)
        end = None if expr.end is None else _eval_expr(expr.end, env)
        return _eval_slice(_eval_expr(expr.collection, env), start, end)
    raise EvalError("unsupported expression")


def _eval_array(expr: ArrayExpr, env: Environment) -> Value:
    values = tuple(_eval_expr(item, env) for item in expr.items)
    if all(isinstance(value, Scalar) for value in values):
        scalars = tuple(value for value in values if isinstance(value, Scalar))
        _ensure_compatible_scalars(scalars)
        return Vector(scalars)
    if all(isinstance(value, Vector) for value in values):
        rows = tuple(value for value in values if isinstance(value, Vector))
        if rows and len({len(row.items) for row in rows}) != 1:
            raise EvalError("matrix rows must have consistent widths")
        for row in rows:
            _ensure_compatible_scalars(row.items)
        return Matrix(rows)
    raise EvalError("array elements must be all scalars or all vectors")


def _eval_binary(left: Value, op: str, right: Value) -> Value:
    if isinstance(left, Matrix) or isinstance(right, Matrix):
        raise EvalError("matrix arithmetic is not implemented yet")
    if isinstance(left, Vector) or isinstance(right, Vector):
        return _eval_vector_binary(left, op, right)
    return _eval_scalar_binary(left, op, right)


def _eval_scalar_binary(left: Scalar, op: str, right: Scalar) -> Scalar:
    if op in ("+", "-"):
        _require_same_dimension(left, right)
        return Scalar(left.value + right.value if op == "+" else left.value - right.value, left.dimension)
    if op == "*":
        return Scalar(left.value * right.value, _combine_dim(left.dimension, right.dimension, 1))
    if op == "/":
        if right.value == 0:
            raise EvalError("division by zero")
        return Scalar(left.value / right.value, _combine_dim(left.dimension, right.dimension, -1))
    if op == "^":
        if right.dimension != DIMENSIONLESS:
            raise EvalError("power exponent must be dimensionless")
        if right.value.is_integer():
            power = int(right.value)
            return Scalar(left.value**right.value, tuple(dim * power for dim in left.dimension))
        if left.dimension != DIMENSIONLESS:
            raise EvalError("non-integer power requires dimensionless base")
        return Scalar(left.value**right.value)
    raise EvalError(f"unknown operator: {op}")


def _eval_vector_binary(left: Value, op: str, right: Value) -> Vector:
    if isinstance(left, Vector) and isinstance(right, Vector):
        if len(left.items) != len(right.items):
            raise EvalError("vector lengths must match")
        return Vector(tuple(_eval_scalar_binary(a, op, b) for a, b in zip(left.items, right.items, strict=True)))
    if isinstance(left, Vector) and isinstance(right, Scalar):
        return Vector(tuple(_eval_scalar_binary(item, op, right) for item in left.items))
    if isinstance(left, Scalar) and isinstance(right, Vector):
        return Vector(tuple(_eval_scalar_binary(left, op, item) for item in right.items))
    raise EvalError("unsupported vector operation")


def _eval_index(collection: Value, index: Value) -> Scalar:
    if not isinstance(collection, Vector):
        raise EvalError("indexing requires vector")
    idx = _as_index(index)
    if idx < 1 or idx > len(collection.items):
        raise EvalError("vector index out of bounds")
    return collection.items[idx - 1]


def _eval_slice(collection: Value, start: Value | None, end: Value | None) -> Vector:
    if not isinstance(collection, Vector):
        raise EvalError("slicing requires vector")
    start_index = 1 if start is None else _as_index(start)
    end_index = len(collection.items) if end is None else _as_index(end)
    if start_index < 1 or end_index > len(collection.items) or start_index > end_index + 1:
        raise EvalError("vector slice out of bounds")
    return Vector(collection.items[start_index - 1 : end_index])


def _call_function(name: str, args: tuple[Value, ...], env: Environment) -> Value:
    if name in _BUILTINS:
        return _BUILTINS[name](args)
    function = env.functions.get(name)
    if function is None:
        raise EvalError(f"unknown function: {name}")
    if len(args) != len(function.params):
        raise EvalError(f"wrong argument count for {name}")
    child = Environment(values={**env.values, **dict(zip(function.params, args, strict=True))}, functions=env.functions)
    return _eval_expr(function.body, child)


def _builtin_scalar_1(name: str, args: tuple[Value, ...], fn: Callable[[float], float]) -> Scalar:
    if len(args) != 1 or not isinstance(args[0], Scalar):
        raise EvalError(f"{name} expects one scalar")
    if name in {"sin", "cos", "tan", "log", "exp"} and args[0].dimension != DIMENSIONLESS:
        raise EvalError(f"{name} input must be dimensionless")
    try:
        return Scalar(fn(args[0].value))
    except ValueError as exc:
        raise EvalError(str(exc)) from exc


def _builtin_sqrt(args: tuple[Value, ...]) -> Scalar:
    if len(args) != 1 or not isinstance(args[0], Scalar):
        raise EvalError("sqrt expects one scalar")
    value = args[0]
    if value.value < 0:
        raise EvalError("sqrt input must be non-negative")
    if any(dim % 2 for dim in value.dimension):
        raise EvalError("sqrt requires even unit exponents")
    return Scalar(math.sqrt(value.value), tuple(dim // 2 for dim in value.dimension))


def _builtin_append(args: tuple[Value, ...]) -> Vector:
    if len(args) != 2 or not all(isinstance(arg, Vector) for arg in args):
        raise EvalError("append expects two vectors")
    left, right = args
    assert isinstance(left, Vector) and isinstance(right, Vector)
    _ensure_compatible_scalars(left.items + right.items)
    return Vector(left.items + right.items)


def _builtin_length(args: tuple[Value, ...]) -> Scalar:
    if len(args) != 1 or not isinstance(args[0], Vector):
        raise EvalError("length expects one vector")
    return Scalar(float(len(args[0].items)))


def _builtin_dot(args: tuple[Value, ...]) -> Scalar:
    if len(args) != 2 or not all(isinstance(arg, Vector) for arg in args):
        raise EvalError("dot expects two vectors")
    left, right = args
    assert isinstance(left, Vector) and isinstance(right, Vector)
    if len(left.items) != len(right.items):
        raise EvalError("vector lengths must match")
    products = [_eval_scalar_binary(a, "*", b) for a, b in zip(left.items, right.items, strict=True)]
    _ensure_compatible_scalars(tuple(products))
    return Scalar(sum(item.value for item in products), products[0].dimension if products else DIMENSIONLESS)


def _as_index(value: Value) -> int:
    if not isinstance(value, Scalar) or value.dimension != DIMENSIONLESS or not value.value.is_integer():
        raise EvalError("index must be a dimensionless integer")
    return int(value.value)


def _ensure_compatible_scalars(items: tuple[Scalar, ...]) -> None:
    if not items:
        return
    dimension = items[0].dimension
    if any(item.dimension != dimension for item in items):
        raise EvalError("array elements must have compatible units")


def _require_same_dimension(left: Scalar, right: Scalar) -> None:
    if left.dimension != right.dimension:
        raise EvalError("dimensions are incompatible")


def _combine_dim(left: tuple[int, ...], right: tuple[int, ...], sign: int) -> tuple[int, ...]:
    return tuple(a + sign * b for a, b in zip(left, right, strict=True))


_BUILTINS: dict[str, Callable[[tuple[Value, ...]], Value]] = {
    "sin": lambda args: _builtin_scalar_1("sin", args, math.sin),
    "cos": lambda args: _builtin_scalar_1("cos", args, math.cos),
    "tan": lambda args: _builtin_scalar_1("tan", args, math.tan),
    "log": lambda args: _builtin_scalar_1("log", args, math.log),
    "exp": lambda args: _builtin_scalar_1("exp", args, math.exp),
    "sqrt": _builtin_sqrt,
    "append": _builtin_append,
    "length": _builtin_length,
    "dot": _builtin_dot,
}
