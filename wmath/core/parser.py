"""Recursive-descent parser for wmath rows."""

from __future__ import annotations

from dataclasses import dataclass

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
    Stmt,
    UnaryExpr,
)
from wmath.core.lexer import Token, lex


@dataclass(frozen=True)
class ParsedLine:
    statement: Stmt | None
    diagnostics: tuple[str, ...] = ()


def parse_line(text: str) -> ParsedLine:
    tokens, lex_errors = lex(text)
    if lex_errors:
        return ParsedLine(None, tuple(lex_errors))
    parser = Parser(tokens)
    return parser.parse_statement()


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.errors: list[str] = []

    def parse_statement(self) -> ParsedLine:
        if self._check("eof"):
            return ParsedLine(None)
        if self._check_text("include"):
            return self._parse_include()

        if self._check("identifier") and self._peek_next().kind == "equals":
            name = self._advance().text
            self._advance()
            expr = self._parse_expression()
            show, display = self._parse_display()
            self._finish_line()
            return ParsedLine(AssignmentStmt(name, expr, display, show), tuple(self.errors))

        if (
            self._check("identifier")
            and self._peek_next().kind == "lparen"
            and self._looks_like_function_declaration()
        ):
            return self._parse_function_declaration()

        expr = self._parse_expression()
        show, display = self._parse_display()
        self._finish_line()
        return ParsedLine(ExpressionStmt(expr, display, show), tuple(self.errors))

    def _parse_include(self) -> ParsedLine:
        self._advance()
        if not self._check("string"):
            self.errors.append("include expects a quoted path")
            return ParsedLine(None, tuple(self.errors))
        path = self._advance().text
        self._finish_line()
        return ParsedLine(IncludeStmt(path), tuple(self.errors))

    def _parse_function_declaration(self) -> ParsedLine:
        name = self._consume("identifier", "expected function name").text
        self._consume("lparen", "expected '('")
        params: list[str] = []
        if not self._check("rparen"):
            while True:
                params.append(self._consume("identifier", "expected parameter name").text)
                if not self._match("comma"):
                    break
        self._consume("rparen", "expected ')'")
        self._consume("equals", "expected '='")
        expr = self._parse_expression()
        show, display = self._parse_display()
        self._finish_line()
        return ParsedLine(FunctionStmt(name, tuple(params), expr, display, show), tuple(self.errors))

    def _parse_display(self) -> tuple[bool, Expr | None]:
        if not self._match("pipe"):
            return False, None
        if self._check("eof"):
            return True, None
        return True, self._parse_expression()

    def _parse_expression(self) -> Expr:
        return self._parse_additive()

    def _parse_additive(self) -> Expr:
        expr = self._parse_multiplicative()
        while self._match_operator("+", "-"):
            op = self._previous().text
            right = self._parse_multiplicative()
            expr = BinaryExpr(expr, op, right)
        return expr

    def _parse_multiplicative(self) -> Expr:
        expr = self._parse_unary()
        while True:
            if self._match_operator("*", "/"):
                op = self._previous().text
                right = self._parse_unary()
                expr = BinaryExpr(expr, op, right)
            elif self._starts_primary():
                right = self._parse_unary()
                expr = BinaryExpr(expr, "*", right)
            else:
                return expr

    def _parse_unary(self) -> Expr:
        if self._match_operator("+", "-"):
            return UnaryExpr(self._previous().text, self._parse_unary())
        return self._parse_power()

    def _parse_power(self) -> Expr:
        expr = self._parse_postfix()
        if self._match_operator("^"):
            expr = BinaryExpr(expr, "^", self._parse_unary())
        return expr

    def _parse_postfix(self) -> Expr:
        expr = self._parse_primary()
        while True:
            if self._match("lparen"):
                args: list[Expr] = []
                if not self._check("rparen"):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match("comma"):
                            break
                self._consume("rparen", "expected ')'")
                expr = CallExpr(expr, tuple(args))
            elif self._match("lbracket"):
                if self._match("colon"):
                    end = None if self._check("rbracket") else self._parse_expression()
                    self._consume("rbracket", "expected ']'")
                    expr = SliceExpr(expr, None, end)
                else:
                    first = self._parse_expression()
                    if self._match("colon"):
                        end = None if self._check("rbracket") else self._parse_expression()
                        self._consume("rbracket", "expected ']'")
                        expr = SliceExpr(expr, first, end)
                    else:
                        self._consume("rbracket", "expected ']'")
                        expr = IndexExpr(expr, first)
            else:
                return expr

    def _parse_primary(self) -> Expr:
        if self._match("number"):
            try:
                return NumberExpr(float(self._previous().text))
            except ValueError:
                self.errors.append(f"invalid number {self._previous().text!r}")
                return NumberExpr(0.0)
        if self._match("identifier"):
            return NameExpr(self._previous().text)
        if self._match("lparen"):
            expr = self._parse_expression()
            self._consume("rparen", "expected ')'")
            return expr
        if self._match("lbracket"):
            items: list[Expr] = []
            if not self._check("rbracket"):
                while True:
                    items.append(self._parse_expression())
                    if not self._match("comma"):
                        break
            self._consume("rbracket", "expected ']'")
            return ArrayExpr(tuple(items))
        self.errors.append(f"expected expression at column {self._peek().position + 1}")
        if not self._check("eof"):
            self._advance()
        return NumberExpr(0.0)

    def _starts_primary(self) -> bool:
        return self._check("number") or self._check("identifier") or self._check("lparen") or self._check("lbracket")

    def _looks_like_function_declaration(self) -> bool:
        depth = 0
        index = self.current + 1
        while index < len(self.tokens):
            token = self.tokens[index]
            if token.kind == "lparen":
                depth += 1
            elif token.kind == "rparen":
                depth -= 1
                if depth == 0:
                    return index + 1 < len(self.tokens) and self.tokens[index + 1].kind == "equals"
            index += 1
        return False

    def _finish_line(self) -> None:
        if not self._check("eof"):
            self.errors.append(f"unexpected token {self._peek().text!r} at column {self._peek().position + 1}")

    def _match(self, kind: str) -> bool:
        if self._check(kind):
            self._advance()
            return True
        return False

    def _match_operator(self, *operators: str) -> bool:
        if self._check("operator") and self._peek().text in operators:
            self._advance()
            return True
        return False

    def _consume(self, kind: str, message: str) -> Token:
        if self._check(kind):
            return self._advance()
        self.errors.append(f"{message} at column {self._peek().position + 1}")
        return Token("eof", "", self._peek().position)

    def _check(self, kind: str) -> bool:
        return self._peek().kind == kind

    def _check_text(self, text: str) -> bool:
        return self._peek().text == text

    def _advance(self) -> Token:
        if not self._check("eof"):
            self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _peek_next(self) -> Token:
        return self.tokens[min(self.current + 1, len(self.tokens) - 1)]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
