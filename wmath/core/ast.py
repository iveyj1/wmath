"""Parser AST nodes for wmath."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NumberExpr:
    value: float


@dataclass(frozen=True)
class NameExpr:
    name: str


@dataclass(frozen=True)
class UnaryExpr:
    op: str
    expr: Expr


@dataclass(frozen=True)
class BinaryExpr:
    left: Expr
    op: str
    right: Expr


@dataclass(frozen=True)
class CallExpr:
    callee: Expr
    args: tuple[Expr, ...]


@dataclass(frozen=True)
class ArrayExpr:
    items: tuple[Expr, ...]


@dataclass(frozen=True)
class IndexExpr:
    collection: Expr
    index: Expr


@dataclass(frozen=True)
class SliceExpr:
    collection: Expr
    start: Expr | None
    end: Expr | None


Expr = NumberExpr | NameExpr | UnaryExpr | BinaryExpr | CallExpr | ArrayExpr | IndexExpr | SliceExpr


@dataclass(frozen=True)
class AssignmentStmt:
    name: str
    expr: Expr
    display: Expr | None = None
    show_value: bool = False


@dataclass(frozen=True)
class FunctionStmt:
    name: str
    params: tuple[str, ...]
    expr: Expr
    display: Expr | None = None
    show_value: bool = False


@dataclass(frozen=True)
class ExpressionStmt:
    expr: Expr
    display: Expr | None = None
    show_value: bool = False


@dataclass(frozen=True)
class IncludeStmt:
    path: str


Stmt = AssignmentStmt | FunctionStmt | ExpressionStmt | IncludeStmt
