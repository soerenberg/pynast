"""Scan stan code."""
from enum import Enum, auto
from typing import NamedTuple


class TokenType(Enum):
    """Token type for Stan."""
    NEWLINE = auto()
    SPACE = auto()

    STRING = auto()

    IDENTIFIER = auto()

    EOF = auto()


class Token(NamedTuple):
    """Token.

    Attributes:
        ttype: type of token
        line: line the token was scanned on
        column: horizontal position the token was scanned on
        lexeme: string as the token was scanned
        literal: literal value, only used for literals.
    """
    ttype: TokenType
    line: int
    column: int
    lexeme: str = ""
    literal: Any = None
