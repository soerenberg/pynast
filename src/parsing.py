"""Stan parser."""
from typing import Any, List
from tokens import Token, TokenType

import expr


class ParseError(Exception):
    """Parse exception."""

    def __init__(self, token: Token, message: str):
        super().__init__(f"In line {token.line}: {message}")


class Parser:
    """Stan parser."""

    def __init__(self, token_list: List[Token]):
        self._token_list = list(token_list)
        self._current = 0

    def parse(self) -> List[Any]:
        """Run parser."""
        result = []

        while not self._is_at_end():
            self._pop_token()
            result.append(None)

        return result

    def _pop_token(self):
        token = self._peek()

        if not self._is_at_end():
            self._current += 1

        return token

    def _is_at_end(self) -> bool:
        """Check if EOF encountered yet."""
        return self._peek().ttype == TokenType.EOF

    def _peek(self) -> Token:
        """Peek at current element."""
        return self._token_list[self._current]

    def _get_current(self) -> Token:
        """Return current token."""
        return self._token_list[self._current]

    def _previous(self) -> Token:
        """Return previous token."""
        return self._token_list[self._current - 1]

    def _check(self, ttype: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().ttype == ttype

    def _match_any(self, *args) -> bool:
        for ttype in args:
            if self._check(ttype):
                self._pop_token()
                return True
        return False

    def _match(self, ttype: TokenType) -> bool:
        """Short form for _match_any with only one argument."""
        return self._match_any(ttype)

    def _consume(self, ttype: TokenType) -> Token:
        """Consume token of required type or raise error."""
        if self._check(ttype):
            return self._pop_token()

        raise ParseError(self._get_current(), "Expected {ttype}.")


    def _parse_unary(self) -> expr.Unary:
        if self._match_any(TokenType.BANG, TokenType.MINUS, TokenType.PLUS,
                           TokenType.HAT):
            operator = self._previous()

            right = self._parse_unary()

            return expr.Unary(operator, right)

        raise ParseError(self._peek(), "Expect '!', '-', '+' or '^'.")
