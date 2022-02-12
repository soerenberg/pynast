"""Scan stan code."""
from enum import Enum, auto


class TokenType(Enum):
    """Token type for Stan."""
    NEWLINE = auto()
    SPACE = auto()

    STRING = auto()

    IDENTIFIER = auto()

    EOF = auto()
