"""Stan parser."""
from typing import Any, List
from tokens import Token, TokenType


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

    def _check(self, ttype: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().ttype == ttype
