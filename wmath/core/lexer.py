"""Lexer for wmath source rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TokenKind = Literal[
    "number",
    "identifier",
    "string",
    "operator",
    "equals",
    "lparen",
    "rparen",
    "lbracket",
    "rbracket",
    "comma",
    "colon",
    "pipe",
    "eof",
]


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    text: str
    position: int


_SINGLE_TOKENS: dict[str, TokenKind] = {
    "=": "equals",
    "(": "lparen",
    ")": "rparen",
    "[": "lbracket",
    "]": "rbracket",
    ",": "comma",
    ":": "colon",
    "|": "pipe",
}
_OPERATORS = set("+-*/^")


def lex(text: str) -> tuple[list[Token], list[str]]:
    """Lex one logical source row."""

    tokens: list[Token] = []
    errors: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == "#":
            break
        if char == "/" and index + 1 < len(text) and text[index + 1] == "*":
            end = text.find("*/", index + 2)
            if end == -1:
                errors.append(f"unterminated block comment at column {index + 1}")
                break
            index = end + 2
            continue
        if char.isdigit() or (char == "." and index + 1 < len(text) and text[index + 1].isdigit()):
            start = index
            index = _consume_number(text, index)
            tokens.append(Token("number", text[start:index], start))
            continue
        if char.isalpha() or char == "_":
            start = index
            index += 1
            while index < len(text) and (text[index].isalnum() or text[index] == "_"):
                index += 1
            tokens.append(Token("identifier", text[start:index], start))
            continue
        if char == '"':
            start = index
            index += 1
            value: list[str] = []
            while index < len(text) and text[index] != '"':
                if text[index] == "\\" and index + 1 < len(text):
                    index += 1
                value.append(text[index])
                index += 1
            if index >= len(text):
                errors.append(f"unterminated string at column {start + 1}")
            else:
                index += 1
                tokens.append(Token("string", "".join(value), start))
            continue
        if char in _OPERATORS:
            tokens.append(Token("operator", char, index))
            index += 1
            continue
        kind = _SINGLE_TOKENS.get(char)
        if kind is not None:
            tokens.append(Token(kind, char, index))
            index += 1
            continue
        errors.append(f"unexpected character {char!r} at column {index + 1}")
        index += 1

    tokens.append(Token("eof", "", len(text)))
    return tokens, errors


def _consume_number(text: str, index: int) -> int:
    seen_dot = False
    while index < len(text):
        char = text[index]
        if char.isdigit():
            index += 1
        elif char == "." and not seen_dot:
            seen_dot = True
            index += 1
        else:
            break
    if index < len(text) and text[index] in "eE":
        exp = index + 1
        if exp < len(text) and text[exp] in "+-":
            exp += 1
        if exp < len(text) and text[exp].isdigit():
            index = exp + 1
            while index < len(text) and text[index].isdigit():
                index += 1
    return index
