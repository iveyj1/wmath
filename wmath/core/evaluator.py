"""Scalar evaluator for parsed wmath rows."""

from __future__ import annotations

import math
from dataclasses import dataclass
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
    NameExpr,
    NumberExpr,
    SliceExpr,
    UnaryExpr,
)
from wmath.core.models import Diagnostic, EvalInput, EvalOutput, RenderedRow
from wmath.core.parser import parse_line


@dataclass(frozen=True)
class UserFunction:
    params: tuple[str, ...]
    body: Expr


@dataclass
class Environment:
    values: dict[str, float]
    functions: dict[str, UserFunction]


def evaluate(eval_input: EvalInput) -> EvalOutput:
    """Evaluate source top-to-bottom with scalar arithmetic."""

    env = Environment(values={}, functions={})
    rows: list[RenderedRow] = []
    warnings: list[Diagnostic] = []
    for line_number, line in enumerate(_logical_lines(eval_input.source), start=1):
        parsed = parse_line(line)
        diagnostics = [Diagnostic(message) for message in parsed.diagnostics]
        formula = line.rstrip() or None
        value_text: str | None = None

        stmt = parsed.statement
        if stmt is None:
            rows.append(RenderedRow(line_number, formula, None, tuple(diagnostics)))
            continue
        if isinstance(stmt, IncludeStmt):
            warning = Diagnostic("include evaluation is not implemented yet", "warning")
            warnings.append(Diagnostic(f"line {line_number}: {warning.message}", "warning"))
            rows.append(RenderedRow(line_number, None, None, (warning,)))
            continue

        if not diagnostics:
            try:
                if isinstance(stmt, AssignmentStmt):
                    value = _eval_expr(stmt.expr, env)
                    env.values[stmt.name] = value
                    if stmt.show_value:
                        value_text = _format_number(value)
                elif isinstance(stmt, FunctionStmt):
                    env.functions[stmt.name] = UserFunction(stmt.params, stmt.expr)
                    if stmt.show_value:
                        diagnostics.append(Diagnostic("function definitions do not display a value", "info"))
                elif isinstance(stmt, ExpressionStmt):
                    value = _eval_expr(stmt.expr, env)
                    value_text = _format_number(value) if stmt.show_value else _format_number(value)
            except EvalError as exc:
                diagnostics.append(Diagnostic(str(exc)))

        rows.append(RenderedRow(line_number, formula, value_text, tuple(diagnostics)))

    return EvalOutput(rows=tuple(rows), warnings=tuple(warnings))


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
    """Evaluation error for a single row."""


def _eval_expr(expr: Expr, env: Environment) -> float:
    if isinstance(expr, NumberExpr):
        return expr.value
    if isinstance(expr, NameExpr):
        try:
            return env.values[expr.name]
        except KeyError as exc:
            raise EvalError(f"unknown name: {expr.name}") from exc
    if isinstance(expr, UnaryExpr):
        value = _eval_expr(expr.expr, env)
        return value if expr.op == "+" else -value
    if isinstance(expr, BinaryExpr):
        left = _eval_expr(expr.left, env)
        right = _eval_expr(expr.right, env)
        return _eval_binary(left, expr.op, right)
    if isinstance(expr, CallExpr):
        if not isinstance(expr.callee, NameExpr):
            raise EvalError("only named function calls are supported")
        args = tuple(_eval_expr(arg, env) for arg in expr.args)
        return _call_function(expr.callee.name, args, env)
    if isinstance(expr, ArrayExpr | SliceExpr):
        raise EvalError("vector evaluation is not implemented yet")
    raise EvalError("indexing is not implemented yet")


def _eval_binary(left: float, op: str, right: float) -> float:
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        if right == 0:
            raise EvalError("division by zero")
        return left / right
    if op == "^":
        return left**right
    raise EvalError(f"unknown operator: {op}")


def _call_function(name: str, args: tuple[float, ...], env: Environment) -> float:
    builtin = _BUILTINS.get(name)
    if builtin is not None:
        try:
            return builtin(*args)
        except TypeError as exc:
            raise EvalError(f"wrong argument count for {name}") from exc
        except ValueError as exc:
            raise EvalError(str(exc)) from exc

    function = env.functions.get(name)
    if function is None:
        raise EvalError(f"unknown function: {name}")
    if len(args) != len(function.params):
        raise EvalError(f"wrong argument count for {name}")
    child = Environment(values={**env.values, **dict(zip(function.params, args, strict=True))}, functions=env.functions)
    return _eval_expr(function.body, child)


def _sqrt(value: float) -> float:
    if value < 0:
        raise ValueError("sqrt input must be non-negative")
    return math.sqrt(value)


def _log(value: float) -> float:
    if value <= 0:
        raise ValueError("log input must be positive")
    return math.log(value)


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.12g}"


_BUILTINS: dict[str, Callable[..., float]] = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": _sqrt,
    "log": _log,
    "exp": math.exp,
}
