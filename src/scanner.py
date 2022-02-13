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


class Scanner:
    """Scanner for Stan."""

    def __init__(self, source: str):
        self._source = source
        self._tokens: List[Token] = []

        self._start = 0
        self._current = 0
        self._line = 1
        self._column = 1

    def scan_tokens(self) -> List[Token]:
        # TODO list comprehension
        while not self._is_at_end():
            self._column += self._current - self._start
            self._start = self._current
            self._scan_single_token()

        self._tokens.append(
            Token(ttype=TokenType.EOF,
                  line=self._line,
                  column=self._column + 1))

        return self._tokens

    def _scan_single_token(self) -> None:
        char = self._pop_char()

        if char == "\n":
            self._add_token(TokenType.NEWLINE)
            self._increase_line()
        elif char in [" ", "\t"]:
            self._add_token(TokenType.SPACE)
        else:
            raise ValueError("Unknown character '{char}'.")

    def _add_token(self, ttype: TokenType, literal: Any = None) -> None:
        lexeme = self._source[self._start:self._current]

        self._tokens.append(
            Token(ttype=ttype,
                  lexeme=lexeme,
                  literal=literal,
                  line=self._line,
                  column=self._column))

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def _pop_char(self) -> str:
        """Advance by a single character."""
        char = self._source[self._current]
        self._current += 1
        return char

    def _peek(self, offset=0) -> str:
        """Peek at `offset` characters ahead (n=0 means current token)."""
        if self._current + offset >= len(self._source):
            return "\0"

        return self._source[self._current + offset]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False

        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _increase_line(self):
        self._line += 1
        self._column = 0
